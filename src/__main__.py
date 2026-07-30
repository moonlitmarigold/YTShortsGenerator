from . import sql, sessions
import argparse
import logging
from . import menu
from .utils import errors
from pathlib import Path
import os
from typing import Optional

config_name = 'config.yaml'
env_name = '.env'

logger = logging.getLogger(__name__)

parser = argparse.ArgumentParser(
                    prog='YTShortsGenerator',
                    description='What the program does',
                    epilog='Text at the bottom of help')

parser.add_argument('--clear', action='store_true')
parser.add_argument('--reset', action='store_true')
parser.add_argument('--log', action='store_true')

parser.add_argument('--config', default=None)
parser.add_argument('--env', default=None)


def search_conf():
    path = Path('.').resolve()
    files = [x.name for x in path.iterdir() if x.is_file()]
    if not config_name in files:
        raise errors.ConfigFileNotFound(path)

    return str(path / files[files.index(config_name)])

def search_env():
    path = Path('.').resolve()
    files = [x.name for x in path.iterdir() if x.is_file()]
    if not env_name in files:
        raise errors.ConfigFileNotFound(path)

    return str(path / files[files.index(env_name)])

def resolve_config_env(conf:Optional[str] = None, env:Optional[str] = None):

    if not conf:
        os.environ['config_path'] = search_conf()
    else:
        config_path = Path(conf).resolve()
        if not config_path.is_file():
            raise errors.ConfigFileNotFound(config_path)
        os.environ['config_path'] = str(config_path)

    if not env:
        os.environ['env_path'] = search_env()
    else:
        env_path = Path(env).resolve()
        if not env_path.is_file():
            raise errors.ConfigFileNotFound(env_path)
        os.environ['env_path'] = str(env_path)




if __name__ == "__main__":
    args = parser.parse_args()

    if args.log:
        logging.basicConfig(level=logging.DEBUG)
        logger.debug('Test')

    if args.clear:
        sessions.SessionInfo.delete_stray_dirs()
        sessions.SessionInfo.delete_stray_sql_entries()
    elif args.reset:
        sessions.SessionInfo.reset()
    else:
        resolve_config_env(args.config, args.env)
        print(f"Config file: {os.environ['config_path']}")
        print(f"Env file: {os.environ['env_path']}")
        try:
            menu.Menu().start()
        except KeyboardInterrupt:
            print('Goodbye')




