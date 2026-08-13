from pathlib import Path
import os

from dotenv import load_dotenv


# ------------------------------------------------------------
# Project paths
# ------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = PROJECT_ROOT / "data"

SQL_DIR = PROJECT_ROOT / "sql"

ENV_FILE = PROJECT_ROOT / ".env"




load_dotenv(ENV_FILE)


DB_CONFIG = {

    "dbname": os.getenv("POSTGRES_DB"),

    "user": os.getenv("POSTGRES_USER"),

    "password": os.getenv("POSTGRES_PASSWORD"),

    "host": os.getenv(
        "POSTGRES_HOST",
        "localhost"
    ),

    "port": int(
        os.getenv(
            "POSTGRES_PORT",
            5432
        )
    ),
}




required = [
    "dbname",
    "user",
    "password",
]


for key in required:

    if not DB_CONFIG[key]:

        raise ValueError(
            f"Missing database configuration: {key}"
        )