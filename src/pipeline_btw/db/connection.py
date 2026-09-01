import psycopg
from psycopg.rows import TupleRow

from pipeline_btw.config import DB_URL


def get_connection() -> psycopg.Connection[TupleRow]:
    return psycopg.connect(DB_URL)
