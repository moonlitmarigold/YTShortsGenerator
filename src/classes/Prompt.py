from pydantic import BaseModel
from .. import providers, generation_types, sessions
import json
import logging
logger = logging.getLogger(__name__)
import re
from pydantic import ValidationError

class Prompt:

    def __init__(self, config:providers.Base.ProviderConfig, secrets:type[BaseModel]):
        self.config = config
        self.provider: providers.Base.BaseProvider = self._provider(secrets)

    def _provider(self, secrets:type[BaseModel]):
        _provider = providers.PROVIDER_REGISTER.get(self.config.name, None)
        return _provider(self.config, secrets)

    @staticmethod
    def _parse_output(output:str):
        clean_output = Prompt.clean_and_parse_json(output)
        return generation_types.schemas.GeneratedVideoScript.model_validate(clean_output)

    @staticmethod
    def clean_and_parse_json(raw: str) -> dict:
        """
        Turn a messy LLM/log-polluted string into a proper JSON-serializable dict.

        Handles:
          - a leading/trailing python triple-quote wrapper ('''...''')
          - a leading/trailing markdown code fence (```json ... ```)
          - stray non-JSON content accidentally pasted mid-document (e.g. a
            pytest "FAILED ... [100%][...]" dump), which is stripped out before
            parsing so it doesn't break json.loads.

        Returns the parsed dict, or raises ValueError/json.JSONDecodeError if the
        content still can't be recovered into valid JSON.
        """
        text = raw.strip()

        # 1. Strip an outer python triple-quote wrapper, if present.
        text = re.sub(r"^'''\s*", "", text)
        text = re.sub(r"\s*'''\s*$", "", text)
        text = text.strip()

        # 2. Strip markdown code fences (```json ... ``` or ``` ... ```).
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```\s*$", "", text)
        text = text.strip()

        # 3. Remove any stray garbage blob that isn't part of the JSON, e.g. a
        #    pytest failure dump like: FAILED ... [100%]['...', '...', ...]
        #    This must run BEFORE brace-balancing, since the junk itself often
        #    contains unbalanced-looking braces/brackets that would confuse it.
        text = Prompt._strip_injected_garbage(text)

        # 4. Isolate the outermost {...} object in case any other stray text
        #    remains around it.
        text = Prompt._extract_balanced_object(text)

        return json.loads(text)

    @staticmethod
    def _strip_injected_garbage(text: str) -> str:
        """
        Removes accidentally-embedded test-runner output of the form:
            FAILED <anything> [100%][ '...', '...', ... ]
        which sometimes gets pasted into the middle of a JSON string by mistake.
        """
        pattern = re.compile(r"FAILED.*?\[100%\]\[.*?\](?=\s*\n)", re.DOTALL)
        return pattern.sub("", text)

    @staticmethod
    def _extract_balanced_object(text: str) -> str:
        """Finds the first '{' and returns everything up to its matching '}'."""
        start = text.find("{")
        if start == -1:
            raise ValueError("No JSON object found in input")

        depth = 0
        in_string = False
        escape = False
        for i in range(start, len(text)):
            ch = text[i]
            if in_string:
                if escape:
                    escape = False
                elif ch == "\\":
                    escape = True
                elif ch == '"':
                    in_string = False
            else:
                if ch == '"':
                    in_string = True
                elif ch == "{":
                    depth += 1
                elif ch == "}":
                    depth -= 1
                    if depth == 0:
                        return text[start: i + 1]

        raise ValueError("Unbalanced braces; could not find end of JSON object")


    def run(self, session:sessions.SessionInfo):
        logger.debug('Prompt content: %s', self.config.prompt)
        num_trys = 0
        while True:
            response = self.provider.prompt()
            try:
                script = self._parse_output(response)
                break
            except ValidationError as val_error:
                num_trys += 1
                logger.error('The AI has not been able to create the config the right way, will rerun the process')
                if num_trys == 3:
                    logger.error('The Ai was unable to deliver the right response after 3 attempts. Stopping the script.')
                    raise RuntimeError('The Ai was unable to deliver the right response after 3 attempts. Stopping the script.')

        logger.debug('LLM Response: %s', script.model_dump())
        session.inject_prompt_output(script, response)




