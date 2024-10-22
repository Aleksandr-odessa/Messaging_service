import logging

import bcrypt
from fastapi import FastAPI, WebSocket, Request, Depends, Form, Response
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager
from sqlmodel import Session
from starlette.middleware.cors import CORSMiddleware
from starlette.websockets import WebSocketDisconnect
import uvicorn
import os
import redis
# Импортируем функции и классы из пользовательских модулей
from DataBase.crud import get_password, get_history_messages
from DataBase.database import create_db_and_tables, get_session
from DataBase.models import Users, Message, Tokens
from bot import run_bot
from tools.manager import ConnectionManager
from tools.tools import generate_secretkey, create_user, message_to_db
import logging_config
from dotenv import load_dotenv
import asyncio
from concurrent.futures import ThreadPoolExecutor
# Настройка шаблонов Jinja2
templates = Jinja2Templates(directory="templates")

# Настройка логирования
logger_debug = logging.getLogger('log_debug')
logger_error = logging.getLogger('log_error')

host = os.getenv("HOST")

# Инициализация Redis-клиента
redis_client = redis.Redis(host=host, port=6379, db=0)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Контекстный менеджер для инициализации базы данных при запуске приложения."""
    create_db_and_tables()
    yield


# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     db_name = NAME_NB
#     user = USERPG
#     password = PASSWORD
#     host = HOST_DB
#     port = "5432"
#     # Создание базы данных в отдельном потоке
#     await asyncio.to_thread(create_database_if_not_exists, db_name, user, password, host, port)
#     yield


app = FastAPI(lifespan=lifespan)

app.mount("/static", StaticFiles(directory="static"))

manager = ConnectionManager()

@app.get("/", response_class=HTMLResponse)
async def registration(request: Request):
    """Отображает страницу регистрации."""
    return templates.TemplateResponse(request=request, name="registration.html")

@app.post("/register")
async def register_user(*, session: Session = Depends(get_session),
                        username: str = Form(), password: str = Form(),
                        request: Request):
    user_added = create_user(session, username, password)
    if user_added:
        return templates.TemplateResponse(request=request, name="index.html")
    else:
        logger_error.error("Ошибка при получении данных")
        return templates.TemplateResponse("registration.html", {"request": request}, status_code=400)

@app.post("/registerapi")
async def register_user_api(*, session: Session = Depends(get_session), user: Users,
                            response: Response):
    user_added = create_user(session, user.name, user.password)
    if not user_added:
        response.status_code = 400
        return None

@app.post("/token")
async def login(*, requests: Request, session: Session = Depends(get_session),
                username=Form(), password=Form(), receiver=Form()):
    """Аутентификация пользователя и получение токена."""
    password_get = get_password(session, username)
    if password_get:
        hashed_password = password_get.password
        print(f'parol2= {hashed_password}')
        if bcrypt.checkpw(password.encode('utf-8'), hashed_password):
            secret_str = generate_secretkey()
            # await redis_client.set(f"token:{username}", secret_str)  # Сохраняем токен в Redis
            return templates.TemplateResponse("index.html", {
                "request": requests,
                "token": secret_str,
                "host": host,
                "username": username,
                "receiver": receiver
            })
        return templates.TemplateResponse(request=requests, name="index.html")
    return templates.TemplateResponse(request=requests, name="registration.html")


@app.get('/tokenapi')
def loginapi(*, session: Session = Depends(get_session), tokens: Tokens, response: Response):
    """Аутентификация пользователя и получение токена."""
    hashed_password = get_password(session, tokens.name).password
    if bcrypt.checkpw(tokens.password, hashed_password):
        secret_str = generate_secretkey()  # Генерация секретного ключа
        # redis_client.set(f"token:{tokens.name}", secret_str)  # Сохраняем токен в Redis
        return {"secret_kod": secret_str}
    response.status_code = 401
    return None

@app.get("/chat", response_class=HTMLResponse)
async def chat(request: Request):
    """Отображает страницу чата."""
    return templates.TemplateResponse("index.html", {"request": request})

@app.websocket("/ws/{username}/{receiver}")
async def websocket_endpoint(websocket: WebSocket, username: str, receiver: str, session: Session = Depends(get_session)):
    """Обрабатывает WebSocket соединения."""
    await manager.connect(username, websocket)  # Подключаем пользователя
    try:
        while True:
            message_text = await websocket.receive_text()  # Получаем сообщение от клиента
            # Добавляем в БД
            message_to_db(session, username, receiver, message_text)
            # Формируем сообщение
            message_data = {
                "sender": username,
                "receiver": receiver,
                "message": message_text
            }
            await manager.send_personal_message(message_data)
    except WebSocketDisconnect:
        manager.disconnect(username)

@app.post('/history')
async def get_history(request: Request, session: Session = Depends(get_session)):
    data = await request.json()
    print(f'sesion1 = {type(session)}')
    history = get_history_messages(session=session, sender=data["name"], receiver=data["receiver"])
    message = [f'{mes.date} от {mes.sender} отправил {mes.receiver} сообщение: {mes.message}' for mes in history]
    return {"messages": message}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# # Асинхронная функция для запуска FastAPI через uvicorn
# async def run_server():
#     # Запускаем сервер FastAPI в отдельной задаче
#     config = uvicorn.Config(app, host="127.0.0.1", port=8000, log_level="info")
#     server = uvicorn.Server(config)
#     await server.serve()
#
# # Основная функция для параллельного выполнения бота и сервера
# async def main():
#     # Запускаем сервер FastAPI как отдельную задачу
#     server_task = asyncio.create_task(run_server())
#     print('start server')
#     # Запускаем бота как отдельную задачу
#     bot_task = asyncio.create_task(run_bot())
#     print("start bot")
#     # Ждем выполнения обеих задач
#     await asyncio.gather(server_task, bot_task)
#
# if __name__ == "__main__":
#     # Запускаем основной событийный цикл
#     asyncio.run(main())

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)