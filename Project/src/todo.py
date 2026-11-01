
def update(task: dict) -> None:
        logger.debug("update called with item=%s", task["item"])
        connection = connect()
        try:
                with connection.cursor() as cursor:
                        cursor.execute("SELECT item FROM ToDoData WHERE item = %s", (task["item"],))
                        if cursor.fetchone() is None:
                                logger.warning("Attempted to update non-existent task: %s", task["item"])
                                raise ValueError("Item doesn't exist")
                        cursor.execute("UPDATE ToDoData SET title = %s, start = %s, due = %s, complete = %s WHERE item = %s", (task["title"], task["start"], task["due"], task["complete"], task["item"]))
                connection.commit()
                logger.info("Updated task: %s", task["item"])
        except Exception:
                connection.rollback()
                raise
        finally:
                connection.close()
                logger.debug("database connection closed")
