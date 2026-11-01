from datetime import datetime, timedelta
import os
import sys
import pymysql
import logging

logger = logging.getLogger(__name__)

def connect():
    logger.debug("connect called")
    """Open a connection using credentials from the environment."""
    missing = [name for name in
               ("SE101_DB_HOST", "SE101_DB_PORT", "SE101_DB_USER",
                "SE101_DB_PASSWORD", "SE101_DB_NAME")
               if not os.environ.get(name)]
    if missing:
        sys.exit("Not set in the environment: " + ", ".join(missing))

    # A connection over the network must be encrypted, and TLS needs the CA
    # certificate that proves the server is the one you think it is. A connection
    # to a server on this machine travels over the loopback interface, which no
    # other machine can see, so it does not.
    ca = os.environ.get("SE101_DB_CA")
    if ca:
        ssl_opts = {"ca": ca}
    elif os.environ["SE101_DB_HOST"] in ("localhost", "127.0.0.1", "::1"):
        ssl_opts = None
    else:
        sys.exit("SE101_DB_CA is not set, and " + os.environ["SE101_DB_HOST"] +
                 " is not this machine. A connection over the network must be "
                 "encrypted: download ca.pem from the Aiven service page and set "
                 "SE101_DB_CA to its full path.")
    

    connection = pymysql.connect(
        host=os.environ["SE101_DB_HOST"],
        port=int(os.environ["SE101_DB_PORT"]),
        user=os.environ["SE101_DB_USER"],
        password=os.environ["SE101_DB_PASSWORD"],
        database=os.environ["SE101_DB_NAME"],
        ssl=ssl_opts,
        cursorclass=pymysql.cursors.DictCursor,
    )
    logger.info("database connection established")
    return connection

def add(task: dict) -> None:
    logger.debug("add called with task %s", task)

    connection = connect()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO ToDoData
                (`item`, `title`, `start`, `due`, `complete`)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    task["item"],
                    task["title"],
                    task["start"],
                    task["due"],
                    task["complete"]
                )
            )

        connection.commit()
        logger.info("task %s added successfully", task["item"])

    except pymysql.err.IntegrityError:
        logger.error("Failed to insert task %s", task["item"])
        raise ValueError("Could not add task due to a database constraint")

    finally:
        connection.close()
        logger.debug("database connection closed")