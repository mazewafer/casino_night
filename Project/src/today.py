import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from Project.src.todo import connect

logger = logging.getLogger(__name__)


def today() -> list[dict]:
    """Return all unfinished tasks due today."""

    logger.debug("today called")

    today_date = datetime.now(
        ZoneInfo("America/Toronto")
    ).date()

    connection = connect()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT *
                FROM ToDoData
                WHERE `due` = %s
                AND `complete` IS NULL
                ORDER BY `item` ASC
                """,
                (today_date,)
            )

            tasks = cursor.fetchall()

        if not tasks:
            logger.warning("No unfinished tasks due today")
            return []

        for task in tasks:
            for field in ("start", "due", "complete"):
                if task[field] is not None:
                    task[field] = task[field].isoformat()

        logger.info("Found %d unfinished tasks due today", len(tasks))

        return tasks

    finally:
        connection.close()
        logger.debug("database connection closed")

