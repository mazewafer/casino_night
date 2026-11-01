import logging
from datetime import date
from Project.src.todo import connect

logger = logging.getLogger(__name__)


def today() -> list[dict]:
    logger.debug("today called")

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
                (date.today(),)
            )

            tasks = cursor.fetchall()

        if not tasks:
            logger.warning("No unfinished tasks due today")
            return []

        # Convert dates to strings
        for task in tasks:
            for field in ("start", "due", "complete"):
                if task[field] is not None:
                    task[field] = task[field].isoformat()

        logger.info("Found %d tasks due today", len(tasks))
        return tasks

    finally:
        connection.close()
        logger.debug("database connection closed")

