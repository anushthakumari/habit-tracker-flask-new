import sqlite3
import sys

def sqlite_conn():
    conn = sqlite3.connect('sqlite_db.db')
    conn.row_factory = sqlite3.Row
    return conn

sys.modules[__name__] = sqlite_conn