import sqlite3

DATABASE_NAME = "tasks.db"


def get_connection():
    connection = sqlite3.connect(DATABASE_NAME)
    connection.row_factory = sqlite3.Row
    return connection

def create_table():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            done BOOLEAN NOT NULL
        )
    """)

    connection.commit()
    connection.close()
    
    
def seed_tasks():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT COUNT(*) FROM tasks")
    count = cursor.fetchone()[0]

    if count == 0:
        cursor.executemany(
            """
            INSERT INTO tasks (title, done)
            VALUES (?, ?)
            """,
            [
                ("Study FastAPI", False),
                ("Buy groceries", True),
                ("Complete assignment", False)
            ]
        )

    connection.commit()
    connection.close()