import logging

from sqlalchemy.exc import IntegrityError, OperationalError
from sqlmodel import select, Session, or_, and_
from .models import Users, Messages, UsersForBot
import logging_config

logger_debug = logging.getLogger('log_debug')
logger_error = logging.getLogger('log_error')

def get_password(session:Session, user:str):
    hash_pasw = select(Users).where(Users.name == user)
    password = session.exec(hash_pasw).first()
    if password:
        return password

def get_history_messages(session:Session, sender:str, receiver:str)->list:
    try:
        hist = select(Messages).where(or_(and_(Messages.sender == sender, Messages.receiver == receiver),
                                          and_(Messages.sender == receiver, Messages.receiver == sender)
            )
        )
        return session.exec(hist).all()
    except Exception as e:
        logger_error.error(f"Error: {e}")

def get_idchat(name: str, session: Session):
    try:
        idchat_query = select(UsersForBot).where(UsersForBot.name == name)
        return session.exec(idchat_query).first()
    except Exception as e:
        logger_error.error(f"Error: {e}")


def add_to_db(session: Session, new_record, model)->bool:
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

# def add_user_for_bot(session: Session, new_user:IdForBot)->bool:
#     try:
#         IdForBot.model_validate(new_user)
#         logger_debug.debug("verification is sucess")
#     except ValueError as e:
#         logger_error.error(f"User validation failed: {e}")
#     try:
#         session.add(new_user)
#         session.commit()
#         session.refresh(new_user)
#     except (IntegrityError, OperationalError) as e:
#         session.rollback()
#         logger_error.error(f"Failed to add user: {e}")
#     return True


# def add_message(session:Session, messages:Messages)-> bool:
#     try:
#         Messages.model_validate(messages)
#         logger_debug.debug("verification is sucess")
#     except ValueError as e:
#         logger_error.error(f"Messages validation failed: {e}")
#     try:
#         session.add(messages)
#         session.commit()
#         session.refresh(messages)
#     except (IntegrityError, OperationalError) as e:
#         session.rollback()
#         logger_error.error(f"Failed to add message: {e}")
#     return True

# def add_user(session:Session, user:Users) -> bool:
#     try:
#         Users.model_validate(user)
#         logger_debug.debug("verification is sucess")
#     except ValueError as e:
#         logger_error.error(f"User validation failed: {e}")
#     try:
#         session.add(user)
#         session.commit()
#         session.refresh(user)
#     except (IntegrityError, OperationalError) as e:
#         session.rollback()
#         logger_error.error(f"Failed to add user: {e}")
#     return True