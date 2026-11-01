import os
import pytest
from datetime import date

from src.todo import add, connect, update


needs_db = pytest.mark.skipif(
    os.environ.get("SE101_NO_DB"),
    reason="no database available in this environment",
)


@needs_db
def test_update_persists_to_database():

    task = {
        "item": "test update 1",
        "title": "School",
        "start": "2026-10-01",
        "due": "2026-10-02",
        "complete": None
    }

    connection = connect()

    try:
        # Remove old test data
        with connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM ToDoData WHERE item = %s",
                (task["item"],)
            )
        connection.commit()

        # Add original task
        add(task)

        # Update task
        task_update = {
            "item": "test update 1",
            "title": "Workout",
            "start": "2026-09-01",
            "due": "2026-11-02",
            "complete": "2026-10-01"
        }

        update(task_update)

        # Read from database
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM ToDoData WHERE item = %s",
                (task["item"],)
            )
            result = cursor.fetchone()

        assert result is not None
        assert result["item"] == task_update["item"]
        assert result["title"] == task_update["title"]
        assert result["start"] == date(2026, 9, 1)
        assert result["due"] == date(2026, 11, 2)
        assert result["complete"] == date(2026, 10, 1)

    finally:
        # Clean up
        with connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM ToDoData WHERE item = %s",
                (task["item"],)
            )
        connection.commit()
        connection.close()


@needs_db
def test_update_item_not_exist_raises_error():

    task_update = {
        "item": "test update nonexistent",
        "title": "Workout",
        "start": "2026-09-01",
        "due": "2026-11-02",
        "complete": "2026-10-01"
    }

    connection = connect()

    try:
        # Make sure the item does not exist
        with connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM ToDoData WHERE item = %s",
                (task_update["item"],)
            )
        connection.commit()

    finally:
        connection.close()

    # Updating a nonexistent item should raise ValueError
    with pytest.raises(ValueError):
        update(task_update)


@needs_db
def test_update_info_not_change():

    task = {
        "item": "test update 1",
        "title": "School",
        "start": "2026-10-01",
        "due": "2026-10-02",
        "complete": None
    }

    connection = connect()

    try:
        # Remove old test data
        with connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM ToDoData WHERE item = %s",
                (task["item"],)
            )
        connection.commit()

        # Add original task
        add(task)

        # Update task
        task_update = {
            "item": "test update 1",
            "title": "School",
            "start": "2026-10-01",
            "due": "2026-10-02",
            "complete": None
        }

        update(task_update)

        # Read from database
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM ToDoData WHERE item = %s",
                (task["item"],)
            )
            result = cursor.fetchone()

        assert result is not None
        assert result["item"] == task_update["item"]
        assert result["title"] == task_update["title"]
        assert result["start"] == date(2026, 10, 1)
        assert result["due"] == date(2026, 10, 2)
        assert result["complete"] == None

    finally:
        # Clean up
        with connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM ToDoData WHERE item = %s",
                (task["item"],)
            )
        connection.commit()
        connection.close()