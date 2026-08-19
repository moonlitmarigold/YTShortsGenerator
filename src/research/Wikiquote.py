from .. import utils
from ..utils import errors
from .Base import BaseResearch
import dataclasses
import html
import re
import requests
import time

@dataclasses.dataclass
class Wikiquote(BaseResearch):


    API = "https://en.wikiquote.org/w/api.php"
    HEADERS = {"User-Agent": "ShortsGeneratorQuoteScraper/0.1 (moonlitmarigold12@gmail.com)", "Accept-Encoding": "gzip",}
    PAGES = ['Consistency']

    # Theme pages keep their quotes under a top level "Quotes" heading; every
    # other section (See also / External links) uses the same bullet syntax and
    # must not be collected.
    HEADING = re.compile(r"^(={2,})\s*(.*?)\s*\1\s*$")
    BULLET = re.compile(r"^(\*+)\s*(.*)$")

    def get_entry(self):
        pass

    def get_pages(self) -> dict[str, list[dict[str, str]]]:
        """Return {page title: [{'quote': ..., 'source': ...}, ...]} for PAGES."""
        return {title: self.parse_page(self.fetch_page(title)) for title in self.PAGES}

    def fetch_page(self, title: str) -> str:
        """Return the raw wikitext of a single theme page."""
        data = self.query(
            action="query",
            titles=title,
            prop="revisions",
            rvprop="content",
            rvslots="main",
        )

        # TODO: Check if page is not already has been fetched recently

        pages = data.get("query", {}).get("pages", [])
        if not pages or pages[0].get("missing"):
            raise errors.NoWikiquotePage(title)

        return pages[0]["revisions"][0]["slots"]["main"]["content"]

    def parse_page(self, wikitext: str) -> list[dict[str, str]]:
        """Pull the ``* quote`` / ``** source`` pairs out of the Quotes section."""
        entries: list[dict[str, str]] = []
        in_quotes = False

        for line in wikitext.splitlines():
            heading = self.HEADING.match(line)
            if heading:
                # Only a level 2 heading switches section; deeper ones (e.g.
                # "===Hoyt's New Cyclopedia===") stay inside their parent.
                if len(heading.group(1)) == 2:
                    in_quotes = heading.group(2).lower().startswith("quotes")
                continue

            if not in_quotes:
                continue

            bullet = self.BULLET.match(line)
            if not bullet:
                continue

            depth, text = len(bullet.group(1)), self.clean_markup(bullet.group(2))
            if not text:
                continue

            if depth == 1:
                entries.append({"quote": text, "source": ""})
            elif entries and not entries[-1]["source"]:
                # First sub-bullet is the attribution; later ones are
                # translations/notes we don't need.
                entries[-1]["source"] = text

        return entries

    @staticmethod
    def clean_markup(text: str) -> str:
        """Strip the wiki markup that would otherwise end up spoken out loud."""
        text = re.sub(r"<ref[^>]*/>", "", text)
        text = re.sub(r"<ref[^>]*>.*?</ref>", "", text, flags=re.DOTALL)
        text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
        text = re.sub(r"</?nowiki>", "", text)
        text = re.sub(r"<br\s*/?>", " ", text)
        text = re.sub(r"</?[a-zA-Z]+[^>]*>", "", text)

        # {{w|Foo}} / {{w|target|Foo}} keep the display text, other templates go.
        text = re.sub(r"\{\{\s*w\s*\|(?:[^{}|]*\|)?([^{}|]+)\}\}", r"\1", text)
        text = re.sub(r"\{\{[^{}]*\}\}", "", text)

        text = re.sub(r"\[\[(?:[^\[\]|]*\|)?([^\[\]|]+)\]\]", r"\1", text)
        text = re.sub(r"\[https?://\S+\s+([^\]]+)\]", r"\1", text)
        text = re.sub(r"\[https?://\S+\]", "", text)

        text = re.sub(r"'{2,}", "", text)

        return html.unescape(text).strip(" *:;,")

    def query(self, **params):
        params.setdefault("format", "json")
        params.setdefault("formatversion", 2)
        params.setdefault("maxlag", 5)

        for attempt in range(self.config.max_api_calls):
            r = requests.get(self.API, headers=self.HEADERS, params=params, timeout=self.config.timeout_sec)

            if r.status_code == 429:
                raise errors.RequestReturned429()

            data = r.json()

            err = data.get("error", {}).get("code")
            if err in ("maxlag", "ratelimited"):
                time.sleep(2 ** attempt)
                continue
            if "error" in data:
                raise RuntimeError(data["error"])

            return data
        raise errors.NoResultsAfterRequestAttempts(self.config.max_api_calls)


    def collect(self, external_ids:list[int]) -> list[utils.planner_schemas.Material]:
        pass
