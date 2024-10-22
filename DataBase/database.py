import os
from sqlmodel import create_engine
from sqlmodel import SQLModel, Session
from dotenv import load_dotenv
load_dotenv()
NAME_NB = os.getenv("POSTGRES_NAME_DB")
USERPG = os.getenv("USERPG")
PASSWORD = os.getenv("PASSWORD")
HOST_DB = os.getenv("HOST_DB")
SQLModel_URL = f"postgresql+psycopg2://postgres:postgres@db/user_db"
engine = create_engine(SQLModel_URL, pool_pre_ping=True)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session() -> Session:
    with Session(engine) as session:
        yield session