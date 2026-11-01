import os
import pytest, pymysql
from datetime import date, timedelta

from src.todo import add, today, connect


needs_db = pytest.mark.skipif(
    os.environ.get("SE101_NO_DB"),
    reason="no database available in this environment",
)

@needs_db
def test_today_returns_correct_tasks():
    item_today = "Today Test Task"
    item_tomorrow = "Tomorrow Test Task"
    tomorrow = date.today() + timedelta(days=1)
    task_today = {
        "item": item_today,
        "title": "Work",
        "start": date.today(),
        "due": date.today(),
        "complete": None
    }
    task_tomorrow = {
        "item": item_tomorrow,
        "title": "Work",
        "start": date.today(),
        "due": tomorrow,
        "complete": None
    }
    try:
        add(task_today)
        add(task_tomorrow)

        result = today()

        assert any(row["item"] == item_today for row in result)
        assert not any(row["item"] == item_tomorrow for row in result)

    finally:
        connection = connect()
        with connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM ToDoData WHERE item IN (%s, %s)",
                (item_today, item_tomorrow)
            )
            connection.commit()
        connection.close()

@needs_db
def test_today_skips_completed_tasks():
    item_completed = "Today Test Completed Task"
    item_pending = "Today Test Pending Task"
    task_completed = {
        "item": item_completed,
        "title": "Work",
        "start": date.today(),
        "due": date.today(),
        "complete": date.today()
    }
    task_pending = {
        "item": item_pending,
        "title": "Work",
        "start": date.today(),
        "due": date.today(),
        "complete": None
    }

    try:
        add(task_completed)
        add(task_pending)

        result = today()

        assert any(row["item"] == item_pending for row in result)
        assert not any(row["item"] == item_completed for row in result)

    finally:
        connection = connect()
        with connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM ToDoData WHERE item IN (%s, %s)",
                (item_completed, item_pending)
            )
            connection.commit()
        connection.close()