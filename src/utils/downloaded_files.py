import dataclasses
from pathlib import Path
import json
import random

def file_generator(files):
    index = 0
    while True:
        if index == len(files):
            index = 0
        yield files[index]
        index += 1

@dataclasses.dataclass
class Downloaded:

    sub_folder:str

    json_info:dict = dataclasses.field(init=False)
    genres:dict = dataclasses.field(init=False)

    def __post_init__(self):
        raw = self.json_path.read_text()
        self.json_info = json.loads(raw)
        self.genres = self.file_by_genre()

    @property
    def base(self):
        return Path(__file__).parent.parent / "files"

    @property
    def path(self):
        return self.base / self.sub_folder

    @property
    def json_path(self):
        return self.path / '.json'

    def file_by_genre(self):
        result = dict()
        for entry in self.json_info:
            if entry['genre'] not in result.keys():
                result[entry['genre']] = [entry['file_name']]
            else:
                result[entry['genre']].append(entry['file_name'])
        return result

    def get_genre(self, genre):
        files = self.genres[genre]
        files = [self.path / file for file in files]
        random.shuffle(files)
        return file_generator(files)





