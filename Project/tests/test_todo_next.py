
import os
import pytest
import logging
from datetime import date

from src.next import earliest_pending, next as get_next
from src.todo import add, connect


needs_db = pytest.mark.skipif(
    os.environ.get("SE101_NO_DB"),
    reason="no database available in this environment",
)


# ---------- earliest_pending tests ----------

def test_earliest_pending_returns_earliest_unfinished_task():
    task = {
        "item": "MATH 115 Assignment 3",
        "title": "Schoolwork",
        "start": date(2026, 9, 26),
        "due": date(2026, 9, 29),
        "complete": None
    }

    earliest_task = {
        "item": "Shopping",
        "title": "Personal",
        "start": date(2026, 9, 27),
        "due": date(2026, 9, 28),
        "complete": None
    }

    latest_task = {
        "item": "CS Assignment",
        "title": "Personal",
        "start": date(2026, 9, 28),
        "due": date(2026, 9, 30),
        "complete": None
    }

    assert earliest_pending([task, earliest_task, latest_task]) == earliest_task


def test_earliest_pending_ignores_finished_tasks():
    finished_task = {
        "item": "Shopping",
        "title": "Personal",
        "start": date(2026, 9, 27),
        "due": date(2026, 9, 28),
        "complete": date(2026, 9, 28)
    }

    unfinished_task = {
        "item": "CS Assignment",
        "title": "Personal",
        "start": date(2026, 9, 29),
        "due": date(2026, 9, 30),
        "complete": None
    }

    assert earliest_pending([finished_task, unfinished_task]) == unfinished_task


def test_earliest_pending_returns_none_when_no_tasks():
    assert earliest_pending([]) is None


def test_earliest_pending_returns_none_when_only_finished_tasks():
    finished_task = {
        "item": "Shopping",
        "title": "Personal",
        "start": date(2026, 9, 27),
        "due": date(2026, 9, 28),
        "complete": date(2026, 9, 28)
    }

    assert earliest_pending([finished_task]) is None


def test_earliest_pending_logs_debug_info(caplog):
    task = {
        "item": "MATH 115 Assignment 3",
        "title": "Schoolwork",
        "start": date(2026, 9, 26),
        "due": date(2026, 9, 29),
        "complete": None
    }

    earliest_task = {
        "item": "Shopping",
        "title": "Personal",
        "start": date(2026, 9, 27),
        "due": date(2026, 9, 28),
        "complete": None
    }

    latest_task = {
        "item": "CS Assignment",
        "title": "Personal",
        "start": date(2026, 9, 28),
        "due": date(2026, 9, 30),
        "complete": None
    }

    with caplog.at_level(logging.DEBUG):
        earliest_pending([task, earliest_task, latest_task])

    assert "earliest_pending called with 3 tasks" in caplog.text
    assert "Earliest pending task is Shopping" in caplog.text


def test_earliest_pending_logs_ignore_finished_info(caplog):
    finished_task = {
        "item": "Shopping",
        "title": "Personal",
        "start": date(2026, 9, 27),
        "due": date(2026, 9, 28),
        "complete": date(2026, 9, 28)
    }

    unfinished_task = {
        "item": "CS Assignment",
        "title": "Personal",
        "start": date(2026, 9, 29),
        "due": date(2026, 9, 30),
        "complete": None
    }

    with caplog.at_level(logging.INFO):
        earliest_pending([finished_task, unfinished_task])

    assert "Earliest pending task is CS Assignment" in caplog.text


def test_earliest_pending_logs_no_tasks_info(caplog):
    with caplog.at_level(logging.INFO):
        earliest_pending([])

    assert "No pending tasks found" in caplog.text


def test_earliest_pending_logs_only_finished_tasks_info(caplog):
    finished_task = {
        "item": "Shopping",
        "title": "Personal",
        "start": date(2026, 9, 27),
        "due": date(2026, 9, 28),
        "complete": date(2026, 9, 28)
    }

    with caplog.at_level(logging.INFO):
        earliest_pending([finished_task])

    assert "No pending tasks found" in caplog.text


# ---------- next database tests ----------

@needs_db
def test_next_returns_earliest_unfinished_task():
    task = {
        "item": "test next MATH",
        "title": "Schoolwork",
        "start": "2026-09-26",
        "due": "2026-09-29",
        "complete": None
    }

    earliest_task = {
        "item": "test next Shopping",
        "title": "Personal",
        "start": "2026-09-27",
        "due": "2026-09-28",
        "complete": None
    }

    latest_task = {
        "item": "test next CS",
        "title": "Personal",
        "start": "2026-09-28",
        "due": "2026-09-30",
        "complete": None
    }

    connection = connect()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM ToDoData WHERE item IN (%s, %s, %s)",
                (task["item"], earliest_task["item"], latest_task["item"])
            )
        connection.commit()

        add(task)
        add(earliest_task)
        add(latest_task)

        result = get_next()

        assert result["item"] == earliest_task["item"]
        assert result["title"] == earliest_task["title"]

    finally:
        with connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM ToDoData WHERE item IN (%s, %s, %s)",
                (task["item"], earliest_task["item"], latest_task["item"])
            )
        connection.commit()
        connection.close()


@needs_db
def test_next_ignores_finished_tasks():
    finished_task = {
        "item": "test next finished",
        "title": "Personal",
        "start": "2026-09-27",
        "due": "2026-09-28",
        "complete": "2026-09-28"
    }

    unfinished_task = {
        "item": "test next unfinished",
        "title": "Personal",
        "start": "2026-09-29",
        "due": "2026-09-30",
        "complete": None
    }

    connection = connect()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM ToDoData WHERE item IN (%s, %s)",
                (finished_task["item"], unfinished_task["item"])
            )
        connection.commit()

        add(finished_task)
        add(unfinished_task)

        result = get_next()

        assert result["item"] == unfinished_task["item"]

    finally:
        with connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM ToDoData WHERE item IN (%s, %s)",
                (finished_task["item"], unfinished_task["item"])
            )
        connection.commit()
        connection.close()


@needs_db
def test_next_returns_none_when_no_tasks():
    connection = connect()

    try:
        # This test requires an empty dedicated test database.
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM ToDoData")
        connection.commit()

        assert get_next() is None

    finally:
        connection.close()


@needs_db
def test_next_returns_none_when_only_finished_tasks():
    finished_task = {
        "item": "test next only finished",
        "title": "Personal",
        "start": "2026-09-27",
        "due": "2026-09-28",
        "complete": "2026-09-28"
    }

    connection = connect()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM ToDoData WHERE item = %s",
                (finished_task["item"],)
            )
        connection.commit()

        add(finished_task)

        assert get_next() is None

    finally:
        with connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM ToDoData WHERE item = %s",
                (finished_task["item"],)
            )
        connection.commit()
        connection.close()


@needs_db
def test_next_breaks_due_date_tie_alphabetically():
    second_alphabetically = {
        "item": "test next MATH Assignment",
        "title": "Personal",
        "start": "2026-09-29",
        "due": "2026-09-30",
        "complete": None
    }

    first_alphabetically = {
        "item": "test next CS Assignment",
        "title": "Schoolwork",
        "start": "2026-09-26",
        "due": "2026-09-30",
        "complete": None
    }

    third_alphabetically = {
        "item": "test next Zebra drawing",
        "title": "Personal",
        "start": "2026-09-29",
        "due": "2026-09-30",
        "complete": None
    }

    connection = connect()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM ToDoData WHERE item IN (%s, %s, %s)",
                (
                    second_alphabetically["item"],
                    first_alphabetically["item"],
                    third_alphabetically["item"]
                )
            )
        connection.commit()

        add(second_alphabetically)
        add(first_alphabetically)
        add(third_alphabetically)

        result = get_next()

        assert result["item"] == first_alphabetically["item"]

    finally:
        with connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM ToDoData WHERE item IN (%s, %s, %s)",
                (
                    second_alphabetically["item"],
                    first_alphabetically["item"],
                    third_alphabetically["item"]
                )
            )
        connection.commit()
        connection.close()


@needs_db
def test_next_logs_debug_info(caplog):
    task = {
        "item": "test next MATH log",
        "title": "Schoolwork",
        "start": "2026-09-26",
        "due": "2026-09-29",
        "complete": None
    }

    earliest_task = {
        "item": "test next Shopping log",
        "title": "Personal",
        "start": "2026-09-27",
        "due": "2026-09-28",
        "complete": None
    }

    latest_task = {
        "item": "test next CS log",
        "title": "Personal",
        "start": "2026-09-28",
        "due": "2026-09-30",
        "complete": None
    }

    connection = connect()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM ToDoData WHERE item IN (%s, %s, %s)",
                (task["item"], earliest_task["item"], latest_task["item"])
            )
        connection.commit()

        add(task)
        add(earliest_task)
        add(latest_task)

        with caplog.at_level(logging.DEBUG):
            get_next()

        assert "next called" in caplog.text
        assert "Next pending task is test next Shopping log" in caplog.text

    finally:
        with connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM ToDoData WHERE item IN (%s, %s, %s)",
                (task["item"], earliest_task["item"], latest_task["item"])
            )
        connection.commit()
        connection.close()


@needs_db
def test_next_logs_ignore_finished_info(caplog):
    finished_task = {
        "item": "test next finished log",
        "title": "Personal",
        "start": "2026-09-27",
        "due": "2026-09-28",
        "complete": "2026-09-28"
    }

    unfinished_task = {
        "item": "test next unfinished log",
        "title": "Personal",
        "start": "2026-09-29",
        "due": "2026-09-30",
        "complete": None
    }

    connection = connect()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM ToDoData WHERE item IN (%s, %s)",
                (finished_task["item"], unfinished_task["item"])
            )
        connection.commit()

        add(finished_task)
        add(unfinished_task)

        with caplog.at_level(logging.INFO):
            get_next()

        assert "Next pending task is test next unfinished log" in caplog.text

    finally:
        with connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM ToDoData WHERE item IN (%s, %s)",
                (finished_task["item"], unfinished_task["item"])
            )
        connection.commit()
        connection.close()


@needs_db
def test_next_logs_no_tasks_info(caplog):
    connection = connect()

    try:
        # This test requires an empty dedicated test database.
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM ToDoData")
        connection.commit()

        with caplog.at_level(logging.INFO):
            get_next()

        assert "No unfinished task found" in caplog.text

    finally:
        connection.close()


@needs_db
def test_next_logs_only_finished_tasks_info(caplog):
    finished_task = {
        "item": "test next only finished log",
        "title": "Personal",
        "start": "2026-09-27",
        "due": "2026-09-28",
        "complete": "2026-09-28"
    }

    connection = connect()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM ToDoData WHERE item = %s",
                (finished_task["item"],)
            )
        connection.commit()

        add(finished_task)

        with caplog.at_level(logging.INFO):
            get_next()

        assert "No unfinished task found" in caplog.text

    finally:
        with connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM ToDoData WHERE item = %s",
                (finished_task["item"],)
            )
        connection.commit()
        connection.close()


@needs_db
def test_next_logs_breaks_tie_alphabetically_info(caplog):
    second_alphabetically = {
        "item": "test next MATH tie log",
        "title": "Personal",
        "start": "2026-09-29",
        "due": "2026-09-30",
        "complete": None
    }

    first_alphabetically = {
        "item": "test next CS tie log",
        "title": "Schoolwork",
        "start": "2026-09-26",
        "due": "2026-09-30",
        "complete": None
    }

    third_alphabetically = {
        "item": "test next Zebra tie log",
        "title": "Personal",
        "start": "2026-09-29",
        "due": "2026-09-30",
        "complete": None
    }

    connection = connect()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM ToDoData WHERE item IN (%s, %s, %s)",
                (
                    second_alphabetically["item"],
                    first_alphabetically["item"],
                    third_alphabetically["item"]
                )
            )
        connection.commit()

        add(second_alphabetically)
        add(first_alphabetically)
        add(third_alphabetically)

        with caplog.at_level(logging.INFO):
            get_next()

        assert "Next pending task is test next CS tie log" in caplog.text

    finally:
        with connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM ToDoData WHERE item IN (%s, %s, %s)",
                (
                    second_alphabetically["item"],
                    first_alphabetically["item"],
                    third_alphabetically["item"]
                )
            )
        connection.commit()
        connection.close()
