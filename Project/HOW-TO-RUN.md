# How to run

## Setup (once)

    git clone https://git.uwaterloo.ca/se101-fall2026/projects/project-team-18.git
    cd project-team-18
    python3 -m pip install flask pymysql pytest

Create `Project/.env` with your own login for the team database (ask the host;
never commit this file):

    SE101_DB_HOST=<team host>
    SE101_DB_PORT=<team port>
    SE101_DB_USER=<your team_18 user>
    SE101_DB_PASSWORD=<your password>
    SE101_DB_NAME=team_18
    SE101_DB_CA=<full path to the host's ca.pem>

## Run the web app

From the `Project` folder:

    cd Project
    set -a; source .env; set +a
    python3 src/web.py

Open http://127.0.0.1:5000 in a browser. Stop the server with Ctrl+C.

## Run the tests

Tests insert and delete rows, so they run against **your own** database, never `team_18`.
Create `Project/test.env` with the same variable names pointing at your own Aiven service
and a separate database (e.g. `lab5test`), and load the table once, from the `Project` folder:

    mysql --host=<your host> --port=<your port> --user=avnadmin -p --ssl-ca=<your ca.pem> --ssl-mode=VERIFY_IDENTITY lab5test < schema.sql

Then, from the `Project` folder:

    set -a; source test.env; set +a
    python3 -m pytest tests -v

Tests must be run from `Project/`, because they import `src.todo`. `*.env` files are ignored by git.