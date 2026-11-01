import os
import sys
import pymysql
import logging

from datetime import date, timedelta


logger = logging.getLogger(__name__)


def connect():
    """Open a connection using credentials from the environment."""
    logger.debug("connect called")

    missing = [name for name in
               ("SE101_DB_HOST", "SE101_DB_PORT", "SE101_DB_USER",
                "SE101_DB_PASSWORD", "SE101_DB_NAME")
               if not os.environ.get(name)]

    if missing:
        logger.error("Missing environment variables: %s", missing)
        sys.exit("Not set in the environment: " + ", ".join(missing))

    # Remote connections require TLS encryption
    ca = os.environ.get("SE101_DB_CA")

    if ca:
        if not os.path.isfile(ca):
            logger.error("CA certificate not found: %s", ca)
            sys.exit(f"CA certificate not found: {ca}")
        ssl_opts = {"ca": ca}
    elif os.environ["SE101_DB_HOST"] in ("localhost", "127.0.0.1", "::1"):
        ssl_opts = None
    else:
        sys.exit(
            "SE101_DB_CA is not set, and "
            + os.environ["SE101_DB_HOST"]
            + " is not this machine. A connection over the network must be "
            "encrypted: download ca.pem from the Aiven service page and set "
            "SE101_DB_CA to its full path."
        )

    try:
        connection = pymysql.connect(
            host=os.environ["SE101_DB_HOST"],
            port=int(os.environ["SE101_DB_PORT"]),
            user=os.environ["SE101_DB_USER"],
            password=os.environ["SE101_DB_PASSWORD"],
            database=os.environ["SE101_DB_NAME"],
            ssl=ssl_opts,
            cursorclass=pymysql.cursors.DictCursor,
        )

        logger.info("Database connection established")
        return connection

    except Exception:
        logger.exception("Database connection failed")
        raise


def pick_tomorrow(tasks, today=None):
    """Return the unfinished tasks in `tasks` that are due tomorrow."""
    if today is None:
        today = date.today()
    tomorrow_date = today + timedelta(days=1)
    return [t for t in tasks if t["complete"] is None and t["due"] == tomorrow_date]

def tomorrow(today=None):
    """Return the unfinished tasks due tomorrow, read from the database."""
    conn = connect()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT item, title, start, due, complete FROM ToDoData")
        rows = cursor.fetchall()
    finally:
        conn.close()
    return pick_tomorrow(rows, today)