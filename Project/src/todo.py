import os
import sys
from datetime import date, timedelta
import pymysql


def connect(**extra):
    """Open a connection using credentials from the environment."""
    missing = [name for name in
               ("SE101_DB_HOST", "SE101_DB_PORT", "SE101_DB_USER",
                "SE101_DB_PASSWORD", "SE101_DB_NAME")
               if not os.environ.get(name)]
    if missing:
        sys.exit("Not set in the environment: " + ", ".join(missing))
 
    # A connection over the network must be encrypted, and TLS needs the CA
    # certificate that proves the server is the one you think it is. A connection
    # to a server on this machine travels over the loopback interface, which no
    # other machine can see, so it does not.
    ca = os.environ.get("SE101_DB_CA")
    if ca:
        ssl_opts = {"ca": ca}
    elif os.environ["SE101_DB_HOST"] in ("localhost", "127.0.0.1", "::1"):
        ssl_opts = None
    else:
        sys.exit("SE101_DB_CA is not set, and " + os.environ["SE101_DB_HOST"] +
                 " is not this machine. A connection over the network must be "
                 "encrypted: download ca.pem from the Aiven service page and set "
                 "SE101_DB_CA to its full path.")
 
    return pymysql.connect(
        host=os.environ["SE101_DB_HOST"],
        port=int(os.environ["SE101_DB_PORT"]),
        user=os.environ["SE101_DB_USER"],
        password=os.environ["SE101_DB_PASSWORD"],
        database=os.environ["SE101_DB_NAME"],
        ssl=ssl_opts,
        cursorclass=pymysql.cursors.DictCursor,
        **extra,
    )

def earliest_pending(tasks):
    """Pick the unfinished task due soonest. No database in here.
 
    Takes a list of (item, type, started, due, done) tuples. Returns None if
    nothing is pending. Ties on due are broken by the task that was started
    first, then by item, so the answer is the same every time.
    """
    pending = [t for t in tasks if t[4] is None or t[4] == ""]
    if not pending:
        return None
    return min(pending, key=lambda t: (t[3], t[0], t[2]))

def next():
    """Fetch every task from the database and hand them to earliest_pending."""
    connection = connect()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT item, type, started, due, done FROM ToDoData")
            rows = cursor.fetchall()
    finally:
        connection.close()
    # The database returns NULL as None, which is what a tuple's done uses too,
    # so the values pass through unchanged.
    tasks = [(r["item"], r["type"], r["started"], r["due"], r["done"])
             for r in rows]
    return earliest_pending(tasks)
