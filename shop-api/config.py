import os
from dotenv import load_dotenv
from urllib.parse import quote

load_dotenv()

pg_username = os.getenv("DB_USER", "")
pg_password = os.getenv("DB_PASSWORD", "")
pg_database = os.getenv("DB_NAME", "")
pg_port = os.getenv("DB_PORT", "")
pg_host = os.getenv("DB_HOST", "")
pg_connection = os.getenv("DB_ENGINE", "")

encoded_password = quote(pg_password, safe="")
SQLALCHEMY_DATABASE_URL = f"{pg_connection}://{pg_username}:{encoded_password}@{pg_host}:{pg_port}/{pg_database}"
print(SQLALCHEMY_DATABASE_URL)