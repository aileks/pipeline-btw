import psycopg

from pipeline_btw.config import DB_URL


def get_connection():
    return psycopg.connect(DB_URL)
