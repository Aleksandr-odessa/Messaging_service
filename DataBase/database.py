import os
from psycopg2 import sql
import psycopg2
from dotenv import load_dotenv
from sqlalchemy.testing.plugin.plugin_base import config
from sqlmodel import create_engine
from sqlmodel import SQLModel, Session
# from dotenv import load_dotenv
load_dotenv()
NAME_NB = os.getenv("POSTGRES_NAME_DB")
USERPG = os.getenv("USERPG")
PASSWORD = os.getenv("PASSWORD")
HOST_DB = os.getenv("HOST_DB")
SQLModel_URL = f"postgresql+psycopg2://{USERPG}:{PASSWORD}@{HOST_DB}/{NAME_NB}"
# SQLModel_URL = f"postgresql+psycopg2://postgres:postgres@localhost/user"
engine = create_engine(SQLModel_URL, pool_pre_ping=True)
#

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session() -> Session:
    with Session(engine) as session:
        yield session

# def create_database_if_not_exists(db_name, user, password, host='localhost', port='5432'):
#     connection = psycopg2.connect(user=user, password=password, host=host, port=port)
#     connection.autocommit = True
#     cursor = connection.cursor()
#     try:
#         cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(db_name)))
#     except psycopg2.errors.DuplicateDatabase:
#         print(f"База данных {db_name} уже существует.")
#     finally:
#         cursor.close()
#         connection.close()
