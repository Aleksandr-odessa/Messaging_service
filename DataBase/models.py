from sqlmodel import SQLModel, Field


class Message(SQLModel):
    sender: str
    receiver: str
    message: str


class Users(SQLModel, table=True):
    id: int | None = Field(primary_key=True, index=True)
    name: str = Field(unique=True, nullable=False)
    password: bytes = Field(unique=True, nullable=False)


class Tokens(SQLModel):
    name: str
    password: str
    receiver: str


class Messages(Message, table=True):
    id: int | None = Field(primary_key=True, index=True)
    date: str


class UsersForBot(SQLModel, table=True):
    name: str = Field(primary_key=True)
    id_chat: str
