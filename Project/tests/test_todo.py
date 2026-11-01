import os
import pytest, pymysql
from datetime import date

from src.todo import add, connect


needs_db = pytest.mark.skipif(
    os.environ.get("SE101_NO_DB"),
    reason="no database available in this environment",
)

@needs_db
def test_add_long_task():
    item = "Long Task"
    connection = connect()
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM ToDoData WHERE item = %s", (item,))
        connection.commit()
    connection.close()

    task = {
        "item": item,
        "title": "Work",
        "start": "2026-01-01",
        "due": "2026-01-02",
        "complete": "2026-01-01"
    }
    try:
        add(task)
        connection = connect()
        with connection.cursor() as cursor:
            cursor.execute("SELECT item, title, start, due, complete FROM ToDoData WHERE item = %s", (item,))
            result = cursor.fetchone()
            assert result is not None
            assert result["item"] == item
            assert result["title"] == "Work"
            assert result["start"] == date(2026, 1, 1)
            assert result["due"] == date(2026, 1, 2)
            assert result["complete"] == date(2026, 1, 1)
        connection.close()
    finally:
        connection = connect()
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM ToDoData WHERE item = %s", (item,))
            connection.commit()
        connection.close()

@needs_db
def test_add_short_task():
    item = "Short Task"
    connection = connect()
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM ToDoData WHERE item = %s", (item,))
        connection.commit()
    connection.close()

    task = {
        "item": item,
        "title": "School",
        "start": None,
        "due": None,
        "complete": None
    }
    try:
        add(task)
        connection = connect()
        with connection.cursor() as cursor:
            cursor.execute("SELECT item, title, start, due, complete FROM ToDoData WHERE item = %s", (item,))
            result = cursor.fetchone()
            assert result is not None
            assert result["item"] == item
            assert result["title"] == "School"
            assert result["start"] is None
            assert result["due"] is None
            assert result["complete"] is None
        connection.close()
    finally:
        connection = connect()
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM ToDoData WHERE item = %s", (item,))
            connection.commit()
        connection.close()

@needs_db
def test_add_database_error():

    task = {
        "item": "Invalid Date Test Task",
        "title": "School",
        "start": "not-a-date",
        "due": "also-not-a-date",
        "complete": None
    }

    with pytest.raises(pymysql.err.OperationalError):
        add(task)

@needs_db
def test_add_existing_task():
    item = "Existing Task"
    connection = connect()
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM ToDoData WHERE item = %s", (item,))
        connection.commit()
    connection.close()

    task = {
        "item": item,
        "title": "School",
        "start": None,
        "due": None,
        "complete": None
    }
    add(task)
    
    with pytest.raises(ValueError):
        add(task)
    connection = connect()
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM ToDoData WHERE item = %s", (item,))
        connection.commit()
    connection.close()


def test_add_empty_title_rejected():
    task = {"item": "test-add-empty", "title": "  ", "start": date(2026, 11, 1),
            "due": date(2026, 11, 5), "complete": None}
    with pytest.raises(ValueError):
        add(task)
    # nothing should have been inserted
    conn = connect()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT item FROM ToDoData WHERE item = %s", ("test-add-empty",))
            assert cur.fetchone() is None
    finally:
        conn.close()