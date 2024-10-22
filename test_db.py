import pytest
from dns.asyncquery import receive_tcp
from fastapi.testclient import TestClient
from sqlmodel import create_engine, SQLModel, Session, select
from sqlmodel.pool import StaticPool
import sys
import os
from datetime import datetime
from DataBase.crud import get_history_messages, add_to_db
from DataBase.database import get_session
from DataBase.models import Messages, Users

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from main import app


@pytest.fixture(name='session')
def session_fixture():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

@pytest.fixture(name='client')
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override

    client = TestClient(app)
    yield  client
    app.dependency_overrides.clear()

# def add_message_for_test(session: Session):
#     message1 = Messages(sender="user1", receiver="user2", message="message1", date=str(datetime.now()))
#     message2 = Messages(sender="user5", receiver="user2", message="message2",date=str(datetime.now()))
#     message3= Messages(sender="user3", receiver="user2", message="message3", date=str(datetime.now()))
#     message4= Messages(sender="user4", receiver="user3", message="message4",date=str(datetime.now()))
#     add_to_db(session=session, new_record=message1, model=Users)
#     add_to_db(session=session, new_record=message2, model=Users)
#     add_to_db(session=session, new_record=message3, model=Users)
#     add_to_db(session=session, new_record=message4, model=Users)

# def test_get_history_messages(session):
#     add_message_for_test(session)
#     hist = get_history_messages(session,"user1","user2" )
#     assert len(hist) == 1
#     assert hist[0].sender == "user1"
#     assert hist[0].receiver == "user2"
#
#
# def test_add(session):
#     # Пример сообщения
#     new_message = Messages(sender="user1", receiver="user2", message="Hello", date=str(datetime.now()))
#     # Проверяем добавление сообщения
#     result = add_to_db(session, new_message, Messages)
#     assert result is True
#     # Проверка, что сообщение действительно добавлено
#     stmt = select(Messages).where(Messages.sender == "user1")
#     messages = session.exec(stmt).all()
#     assert len(messages) == 1
#     assert messages[0].receiver == "user2"
#     assert messages[0].message == "Hello"


