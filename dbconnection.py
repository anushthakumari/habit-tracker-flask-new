import sqlite3
import sys

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

sys.modules[__name__] = get_db_connection