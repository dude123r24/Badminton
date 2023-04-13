# db.py
import psycopg2
from contextlib import contextmanager
from config_local import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT

@contextmanager
def get_connection():
    conn = psycopg2.connect(database=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)
    try:
        yield conn
    finally:
        conn.close()

@contextmanager
def get_cursor(conn):
    cur = conn.cursor()
    try:
        yield cur
    finally:
        cur.close()

