from . import sql, sessions
import argparse
import logging

logger = logging.getLogger(__name__)

parser = argparse.ArgumentParser(
                    prog='YTShortsGenerator',
                    description='What the program does',
                    epilog='Text at the bottom of help')

parser.add_argument('--clear', action='store_true')

if __name__ == "__main__":
    args = parser.parse_args()

    if args.clear:
        sessions.SessionInfo.delete_stray_files()

