
import os
import pymysql
import logging
from datetime import date

logger = logging.getLogger(__name__)


def connect():
    """Open a connection using credentials from the environment."""
    logger.debug("connect called")

    missing = [
        name for name in (
            "SE101_DB_HOST",
            "SE101_DB_PORT",
            "SE101_DB_USER",
            "SE101_DB_PASSWORD",
            "SE101_DB_NAME"
        )
        if not os.environ.get(name)
    ]

    if missing:
        raise RuntimeError(
            "Not set in the environment: " + ", ".join(missing)
        )

    # A remote database connection must use TLS.
    ca = os.environ.get("SE101_DB_CA")

    if ca:
        ssl_opts = {"ca": ca}
    elif os.environ["SE101_DB_HOST"] in (
        "localhost", "127.0.0.1", "::1"
    ):
        ssl_opts = None
    else:
        raise RuntimeError(
            "SE101_DB_CA is not set. "
            "Download ca.pem from Aiven and set SE101_DB_CA."
        )

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

    # Validate item and title
    for field in ("item", "title"):
        if not isinstance(task.get(field), str) or not task[field].strip():
            raise ValueError(f"{field} must be a non-empty string")

    # Validate date strings
    for field in ("start", "due", "complete"):
        value = task.get(field)

        if field == "complete" and value is None:
            continue

        if not isinstance(value, str):
            raise ValueError(f"{field} must be a date string")

        try:
            parsed_date = date.fromisoformat(value)
        except ValueError:
            raise ValueError(f"Invalid date for {field}: {value}")

        if parsed_date.isoformat() != value:
            raise ValueError(f"{field} must use YYYY-MM-DD format")

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

    except pymysql.err.IntegrityError as e:
        if e.args[0] == 1062:
            logger.error("Task %s already exists", task["item"])
            raise ValueError("Task already exists") from e

        logger.error("Database constraint error while adding task")
        raise

    finally:
        connection.close()
        logger.debug("database connection closed")
