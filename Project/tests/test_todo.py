import os
import uuid
from datetime import date, datetime, timedelta
 

 

 

import sys
import pytest, pymysql


from src.todo import add, connect, delete, pick_tomorrow, tomorrow

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

 
TODAY = date(2026, 10, 10)
TOMORROW = date(2026, 10, 11)
 
 
def task(item, due, complete=None):
    """A task as tomorrow() reads it from the database: a dict of columns."""
    return {"item": item, "title": "a task", "start": date(2026, 10, 1),
            "due": due, "complete": complete}
 
 
def items(tasks):
    return [t["item"] for t in tasks]
 
 
# --- pick_tomorrow(): no database needed -----------------------------------
 
def test_includes_task_due_tomorrow():
    result = pick_tomorrow([task("a", TOMORROW)], today=TODAY)
    assert items(result) == ["a"]
 
 
def test_excludes_task_due_today():
    assert pick_tomorrow([task("a", TODAY)], today=TODAY) == []
 
 
def test_excludes_overdue_task():
    assert pick_tomorrow([task("a", TODAY - timedelta(days=1))], today=TODAY) == []
 
 
def test_excludes_task_due_day_after_tomorrow():
    assert pick_tomorrow([task("a", TOMORROW + timedelta(days=1))], today=TODAY) == []
 
 
def test_excludes_completed_task_due_tomorrow():
    done = task("a", TOMORROW, complete=date(2026, 10, 9))
    assert pick_tomorrow([done], today=TODAY) == []
 
 
def test_returns_every_task_due_tomorrow():
    tasks = [task("a", TOMORROW), task("b", TOMORROW)]
    assert set(items(pick_tomorrow(tasks, today=TODAY))) == {"a", "b"}
 
 
def test_mixed_list_returns_only_the_unfinished_tasks_due_tomorrow():
    tasks = [
        task("overdue", TODAY - timedelta(days=3)),
        task("today", TODAY),
        task("tomorrow open", TOMORROW),
        task("tomorrow done", TOMORROW, complete=TODAY),
        task("later", TOMORROW + timedelta(days=5)),
    ]
    assert items(pick_tomorrow(tasks, today=TODAY)) == ["tomorrow open"]
 
 
def test_empty_list_gives_empty_list():
    assert pick_tomorrow([], today=TODAY) == []
 
 
 
@pytest.mark.parametrize("today, expected", [
    (date(2026, 10, 31), date(2026, 11, 1)),   # end of a month
    (date(2026, 12, 31), date(2027, 1, 1)),    # end of a year
    (date(2028, 2, 28), date(2028, 2, 29)),    # leap year
    (date(2027, 2, 28), date(2027, 3, 1)),     # not a leap year
], ids=["month-end", "year-end", "leap-day", "no-leap-day"])
def test_tomorrow_rolls_over_calendar_boundaries(today, expected):
    result = pick_tomorrow([task("a", expected), task("b", today)], today=today)
    assert items(result) == ["a"]
 
 
def test_today_defaults_to_the_real_date():
    real_tomorrow = date.today() + timedelta(days=1)
    result = pick_tomorrow([task("a", real_tomorrow)])
    assert items(result) == ["a"]
 
 
def test_does_not_change_the_list_it_is_given():
    tasks = [task("a", TOMORROW), task("b", TODAY)]
    pick_tomorrow(tasks, today=TODAY)
    assert items(tasks) == ["a", "b"]
 
 
 
# --- tomorrow(): reads the real database -----------------------------------
#
# These insert rows directly, using the column names in tomorrow()'s query
# (item, title, start, due, complete). Each test uses uniquely named rows and
# the fixture deletes exactly those rows afterwards.
 
@pytest.fixture
def make_task():
    created = []
 
    def make(label, due, complete=None):
        name = "test-" + uuid.uuid4().hex[:8] + "-" + label
        created.append(name)
        connection = connect()
        try:
            cursor = connection.cursor()
            try:
                cursor.execute(
                    "INSERT INTO ToDoData (item, title, start, due, complete) "
                    "VALUES (%s, %s, %s, %s, %s)",
                    (name, "test task", date.today(), due, complete),
                )
            finally:
                cursor.close()
            connection.commit()
        finally:
            connection.close()
        return name
 
    yield make
 
    if created:
        connection = connect()
        try:
            cursor = connection.cursor()
            try:
                cursor.executemany("DELETE FROM ToDoData WHERE item = %s",
                                   [(name,) for name in created])
            finally:
                cursor.close()
            connection.commit()
        finally:
            connection.close()
 
 
@needs_db
def test_tomorrow_returns_a_task_due_tomorrow_from_the_table(make_task):
    name = make_task("in", date.today() + timedelta(days=1))
    assert name in items(tomorrow())
 
 
@needs_db
@pytest.mark.parametrize("offset", [-1, 0, 2], ids=["yesterday", "today", "day-after"])
def test_tomorrow_leaves_out_tasks_due_on_other_days(make_task, offset):
    name = make_task("out", date.today() + timedelta(days=offset))
    assert name not in items(tomorrow())
 
 
@needs_db
def test_tomorrow_leaves_out_a_completed_task(make_task):
    name = make_task("done", date.today() + timedelta(days=1),
                     complete=date.today())
    assert name not in items(tomorrow())
 
 
@needs_db
def test_tomorrow_uses_the_today_it_is_given(make_task):
    fixed_today = date(2030, 5, 5)
    name = make_task("fixed", date(2030, 5, 6))
    assert name in items(tomorrow(today=fixed_today))
    assert name not in items(tomorrow())
 


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

