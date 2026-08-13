import psycopg

from sqlalchemy import (
    create_engine,
    URL,
)

from .config import DB_CONFIG


def get_psycopg_connection():

    return psycopg.connect(
        dbname=DB_CONFIG["dbname"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        host=DB_CONFIG["host"],
        port=DB_CONFIG["port"],
    )


def get_engine():

    database_url = URL.create(

        drivername="postgresql+psycopg",

        username=DB_CONFIG["user"],

        password=DB_CONFIG["password"],

        host=DB_CONFIG["host"],

        port=DB_CONFIG["port"],

        database=DB_CONFIG["dbname"],
    )


    return create_engine(
        database_url,
        pool_pre_ping=True,
    )