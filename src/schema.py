from pathlib import Path

from .config import SQL_DIR

from .db import get_psycopg_connection


def execute_sql_file(
    file_path: Path
):

    sql_script = file_path.read_text(
        encoding="utf-8"
    )

    print(
        f"Running {file_path.name}..."
    )


    with get_psycopg_connection() as conn:

        conn.execute(
            sql_script,
            prepare=False,
        )


    print(
        f"{file_path.name} completed."
    )


def create_schema():

    execute_sql_file(
        SQL_DIR / "schema.sql"
    )


def create_feature_views():

    execute_sql_file(
        SQL_DIR / "features.sql"
    )