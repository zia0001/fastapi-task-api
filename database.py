import os

import psycopg
from dotenv import load_dotenv


load_dotenv()


def get_connection():
    return psycopg.connect(
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT"),
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
    )


def create_table():
    connection = get_connection()

    with connection.cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                done BOOLEAN NOT NULL DEFAULT FALSE
            )
        """)

    connection.commit()
    connection.close()


def seed_tasks():
    connection = get_connection()

    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM tasks")
        count = cursor.fetchone()[0]

        if count == 0:
            cursor.executemany(
                """
                INSERT INTO tasks (title, done)
                VALUES (%s, %s)
                """,
                [
                    ("Study FastAPI", False),
                    ("Buy groceries", True),
                    ("Complete assignment", False),
                ],
            )

    connection.commit()
    connection.close()


def get_all_tasks():
    connection = get_connection()

    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT id, title, done FROM tasks ORDER BY id"
        )

        rows = cursor.fetchall()

    connection.close()

    return [
        {
            "id": row[0],
            "title": row[1],
            "done": row[2],
        }
        for row in rows
    ]


def get_task_by_id(task_id: int):
    connection = get_connection()

    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT id, title, done
            FROM tasks
            WHERE id = %s
            """,
            (task_id,),
        )

        row = cursor.fetchone()

    connection.close()

    if row is None:
        return None

    return {
        "id": row[0],
        "title": row[1],
        "done": row[2],
    }


def create_task(title: str):
    connection = get_connection()

    with connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO tasks (title, done)
            VALUES (%s, %s)
            RETURNING id, title, done
            """,
            (title, False),
        )

        row = cursor.fetchone()

    connection.commit()
    connection.close()

    return {
        "id": row[0],
        "title": row[1],
        "done": row[2],
    }



def update_task(task_id: int, title=None, done=None):
    connection = get_connection()

    with connection.cursor() as cursor:
        cursor.execute(
            """
            UPDATE tasks
            SET
                title = COALESCE(%s, title),
                done = COALESCE(%s, done)
            WHERE id = %s
            RETURNING id, title, done
            """,
            (title, done, task_id),
        )

        row = cursor.fetchone()

    connection.commit()
    connection.close()

    if row is None:
        return None

    return {
        "id": row[0],
        "title": row[1],
        "done": row[2],
    }


def delete_task(task_id: int):
    connection = get_connection()

    with connection.cursor() as cursor:
        cursor.execute(
            """
            DELETE FROM tasks
            WHERE id = %s
            RETURNING id
            """,
            (task_id,),
        )

        row = cursor.fetchone()

    connection.commit()
    connection.close()

    return row is not None