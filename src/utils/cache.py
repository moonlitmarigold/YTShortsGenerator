import dataclasses
from pathlib import Path
import json

@dataclasses.dataclass
class SimpleCache:


    _cache:dict = dataclasses.field(init=False)

    @property
    def cache(self):
        if not hasattr(self, '_cache'):
            self._cache = self.load()
        return self._cache

    @property
    def cache_path(self):
        p = Path(__file__).parent.parent / '.cache'
        p.touch(exist_ok=True)
        return p

    def load(self):
        p = self.cache_path
        t = p.read_text()
        if t:
            return json.loads(t)
        return {}

    def add(self, namespace:str, entry:dict):
        if not namespace in self.cache.keys():
            self.cache[namespace] = []
        self.cache[namespace].append(entry)

    def get(self, namespace:str):
        if not namespace in self.cache.keys():
            return None
        return self.cache[namespace]

    def __del__(self):
        _json = json.dumps(self.cache)
        self.cache_path.write_text(_json)

    def __str__(self):
        return json.dumps(self.cache)
