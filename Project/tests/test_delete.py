import os
import sys
from datetime import date

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from todo import connect, delete

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