import os
import uuid
from datetime import date, datetime, timedelta
 
import pytest
 
from src.todo import connect, pick_tomorrow, tomorrow
 
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
 