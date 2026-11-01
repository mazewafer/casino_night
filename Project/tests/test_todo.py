import os
import sys
import pytest, pymysql
from datetime import date, timedelta

from src.todo import add, connect, delete

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

PREFIX = "test-delete-"

# Refuse to run against the team database: these tests insert and delete rows.
if os.environ.get("SE101_DB_NAME", "").startswith("team_"):
    pytest.exit("Tests must run against your own database, not the team one.")


def _insert(item, due=date(2026, 11, 5)):
    conn = connect()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO ToDoData (item, title, start, due, complete) "
                "VALUES (%s, %s, %s, %s, %s)",
                (item, "test task", date(2026, 11, 1), due, None),
            )
        conn.commit()
    finally:
        conn.close()


def _test_items():
    conn = connect()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT item FROM ToDoData WHERE item LIKE %s", (PREFIX + "%",))
            return {row["item"] for row in cur.fetchall()}
    finally:
        conn.close()


@pytest.fixture(autouse=True)
def cleanup():
    """Remove this file's test rows before and after each test."""
    def wipe():
        conn = connect()
        try:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM ToDoData WHERE item LIKE %s", (PREFIX + "%",))
            conn.commit()
        finally:
            conn.close()
    wipe()
    yield
    wipe()


def _task(item):
    return {"item": item, "title": "test task", "start": date(2026, 11, 1),
            "due": date(2026, 11, 5), "complete": None}


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

def test_delete_removes_existing_task():
    _insert(PREFIX + "a")
    delete(_task(PREFIX + "a"))
    assert PREFIX + "a" not in _test_items()


def test_delete_leaves_other_tasks():
    _insert(PREFIX + "a")
    _insert(PREFIX + "b")
    delete(_task(PREFIX + "a"))
    assert _test_items() == {PREFIX + "b"}


def test_delete_missing_task_does_nothing():
    _insert(PREFIX + "a")
    delete(_task(PREFIX + "missing"))   # should not raise
    assert _test_items() == {PREFIX + "a"}
