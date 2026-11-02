from datetime import date

from flask import Flask, flash, redirect, render_template, request, url_for

from todo import add, update, delete, today, tomorrow
from todo import next as next_task   # "next" is also a Python built-in, so rename it here

app = Flask(__name__)
app.secret_key = "local-dev-only"     # needed for the messages shown after each action


def _date_or_none(text):
    """Turn a form's 'YYYY-MM-DD' text into a date, or None if left blank."""
    text = (text or "").strip()
    return date.fromisoformat(text) if text else None


def _task_from_form(form):
    """Build a task dict, as in our contract, from the submitted form."""
    return {
        "item": form["item"].strip(),
        "title": form["title"].strip(),
        "start": _date_or_none(form["start"]),
        "due": _date_or_none(form["due"]),
        "complete": _date_or_none(form.get("complete")),
    }


@app.route("/")
def index():
    return render_template(
        "index.html",
        next_task=next_task(),
        today_tasks=today(),
        tomorrow_tasks=tomorrow(),
    )


@app.post("/add")
def add_route():
    try:
        add(_task_from_form(request.form))
        flash("Task added.")
    except Exception as e:
        flash(f"Could not add task: {e}")
    return redirect(url_for("index"))


@app.post("/update")
def update_route():
    try:
        update(_task_from_form(request.form))
        flash("Task updated.")
    except Exception as e:
        flash(f"Could not update task: {e}")
    return redirect(url_for("index"))


@app.post("/done")
def done_route():
    try:
        task = _task_from_form(request.form)
        task["complete"] = date.today()
        update(task)
        flash("Task marked done.")
    except Exception as e:
        flash(f"Could not mark task done: {e}")
    return redirect(url_for("index"))


@app.post("/delete")
def delete_route():
    try:
        delete({"item": request.form["item"].strip()})
        flash("Task deleted.")
    except Exception as e:
        flash(f"Could not delete task: {e}")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)