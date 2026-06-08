import os
from contextlib import contextmanager

import pymysql


DB_CONFIG = {
    "host": os.getenv("SCORE_DB_HOST", "127.0.0.1"),
    "user": os.getenv("SCORE_DB_USER", "root"),
    "password": os.getenv("SCORE_DB_PASSWORD", "AbcD@314159"),
    "database": os.getenv("SCORE_DB_NAME", "student_score_db"),
    "port": int(os.getenv("SCORE_DB_PORT", "3306")),
    "charset": "utf8mb4",
    "connect_timeout": 5,
    "read_timeout": 10,
    "write_timeout": 10,
    "autocommit": False,
}


def get_db_connection():
    return pymysql.connect(**DB_CONFIG)


@contextmanager
def db_cursor(commit=False):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        yield cur
        if commit:
            conn.commit()
    except Exception:
        if commit:
            conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()
