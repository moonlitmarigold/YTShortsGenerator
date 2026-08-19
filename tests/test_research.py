from src import research
from src.classes import Research
from src.utils import Secrets
from pathlib import Path
from src.utils import cache

def test_cache():
    c = cache.SimpleCache()

    c.add('a', {'source':'test', 'time':'now'})
    print(c)


def test_wikiquote():
    env_file = Path('.env')

    conf = research.ResearchConfig()
    s = Secrets(_env_file=env_file)

    _obj = research.Wikiquote(
        conf, s
    )

    print(_obj.get_pages())
