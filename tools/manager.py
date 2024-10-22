import logging

import redis
import requests
from fastapi import WebSocket
from typing import Dict
import os
from sqlmodel import Session
from requests import session

import logging_config
from DataBase.crud import get_idchat
from DataBase.database import engine

from tools.tools import get_id

host = os.getenv("HOST")
chat_id = os.getenv("chat_id")
TOKEN = os.getenv("TG_TOKEN")

logger_debug = logging.getLogger('log_debug')
# Инициализация Redis-клиента
redis_client = redis.Redis(host='localhost', port=6379, db=0)


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, username: str, websocket: WebSocket):
        """Подключает пользователя и сохраняет его WebSocket соединение в памяти."""
        await websocket.accept()
        self.active_connections[username] = websocket
        # Устанавливаем статус пользователя как "online" в Redis
        redis_client.set(f"status:{username}", "online")

    def disconnect(self, username: str):
        """Отключает пользователя и удаляет его соединение из памяти."""
        if username in self.active_connections:
            del self.active_connections[username]
            # Обновляем статус в Redis как "offline"
            redis_client.set(f"status:{username}", "offline")


    async def send_personal_message(self, data):
        offline_message = f"Пользователь {data["receiver"]} оффлайн. Сообщение: {data["message"]} не доставлено"
        """Отправляет сообщение пользователю, если он онлайн."""
        status = redis_client.get(f"status:{data["receiver"]}")

        if status == b"online":
            # Проверяем, есть ли WebSocket-соединение в памяти приложения
            websocket = self.active_connections.get(data["receiver"])
            if websocket:
                await websocket.send_text(f'Сообщение от {data["sender"]}: {data["message"]}')
            with Session(engine) as session:
                # Вызов функции для получения данных из базы
                chat_id = get_idchat(data['receiver'], session).id_chat
                url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&text={offline_message}"
                requests.get(url).json()


