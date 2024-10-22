import random
import string
from datetime import datetime
import bcrypt

from DataBase.crud import add_to_db, get_idchat
from DataBase.models import Users, Messages
from fastapi import Depends
from DataBase.database import get_session
from sqlmodel import Session


def generate_secretkey(length=15):
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for _ in range(length))


def create_user(session, username, password) -> bool:
    """Регистрация нового пользователя."""
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    new_user = Users(name=username, password=hashed_password)
    add_to_db(session=session, new_record=new_user, model=Users)
    return True


def message_to_db(session, username, receiver, message):
    """Запись нового сообщения в БД"""
    now_date = datetime.now()
    date_time = now_date.strftime("%m/%d/%Y %H:%M:%S")
    new_message = Messages(
        sender=username,
        receiver=receiver,
        message=message,
        date=date_time)
    add_to_db(session=session, new_record=new_message, model=Messages)
    return True
