import os
import sqlite3

_db_file = 'podcasts.db'

_schema_files = (
    'feeds.sql',
    'episodes.sql',
)

_cwd = os.path.dirname(__file__) + '/'

connection = sqlite3.connect(_cwd + _db_file)
connection.row_factory = sqlite3.Row


def _setup():
    for s in _schema_files:
        _executefile(s)


def _delete():
    connection.close()
    os.remove(_cwd + _db_file)


def _executefile(f: str):
    global connection
    with open(_cwd + 'sql/' + f, 'r') as f:
        connection.executescript(f.read())
        connection.commit()


def cursor():
    """Shorthand helper to quickly get a cursor."""
    return connection.cursor()


_setup()
