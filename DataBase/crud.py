import logging

from sqlalchemy.exc import IntegrityError, OperationalError
from sqlmodel import select, Session, or_, and_
from .models import Users, Messages, UsersForBot
import logging_config

logger_debug = logging.getLogger('log_debug')
logger_error = logging.getLogger('log_error')


def get_password(session: Session, user: str):
    hash_pasw = select(Users).where(Users.name == user)
    password = session.exec(hash_pasw).first()
    if password:
        return password


def get_history_messages(session: Session, sender: str, receiver: str) -> list:
    try:
        hist = select(Messages).where(
            or_(
                and_(
                    Messages.sender == sender,
                    Messages.receiver == receiver),
                and_(
                    Messages.sender == receiver,
                    Messages.receiver == sender)))
        return session.exec(hist).all()
    except Exception as e:
        logger_error.error(f"Error: {e}")


def get_idchat(name: str, session: Session):
    try:
        idchat_query = select(UsersForBot).where(UsersForBot.name == name)
        return session.exec(idchat_query).first()
    except Exception as e:
        logger_error.error(f"Error: {e}")


def add_to_db(session: Session, new_record, model) -> bool:
    try:
        model.model_validate(new_record)
    except ValueError as e:
        logger_error.error(f"User validation failed: {e}")
    try:
        session.add(new_record)
        session.commit()
        session.refresh(new_record)
    except (IntegrityError, OperationalError) as e:
        session.rollback()
        logger_error.error(f"Failed to add user: {e}")
    return True