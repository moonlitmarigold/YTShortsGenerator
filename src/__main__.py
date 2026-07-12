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
        ids = sessions.SessionInfo.all_sessions_id()
        for id in ids:
            try:
                obj = sessions.SessionInfo.from_sql(id)
                obj.delete()
            except Exception:
                logger.exception("Failed to clear session %s, continuing with the rest", id)
