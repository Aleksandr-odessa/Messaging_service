import asyncio
import json
import websockets
import requests

from main import host


class ChatClient:
    __slots__ = ("username", "password", "receiver", "websocket")

    def __init__(self, username, password, receiver):
        self.username = username
        self.password = password
        self.receiver = receiver
        self.websocket = None

    def register(self):
        """Регистрация нового пользователя."""
        url = f"http://{host}/registerapi"
        data1 = {
            "name": self.username,
            "password": self.password
        }
        data = json.dumps(data1)
        response = requests.post(url, data=data)
        if response.status_code == 200:
            print("Регистрация успешна.")
        else:
            print(f"Ошибка регистрации: {response.text}")

    def login(self):
        """Аутентификация пользователя и установка получателя."""
        url = f"http://{host}/tokenapi"
        data_dict = {
            "name": self.username,
            "password": self.password,
            "receiver": self.receiver
        }
        data = json.dumps(data_dict)
        response = requests.get(url, data=data)
        # if response.raise_for_status():
        if response.status_code == 200:
            print("Аутентификация успешна.")
            return response.json()["secret_kod"]
        else:
            print(f"Ошибка аутентификации")
            return None

    # Асинхронная функция для неблокирующего ввода данных
    async def async_input(self, prompt: str):
        print(prompt, end='', flush=True)
        return await asyncio.get_running_loop().run_in_executor(None, input)

    async def connect_websocket(self):
        print(f'receiver = {self.receiver}')
        """Подключение к WebSocket."""
        if receiver is None:
            print("Получатель сообщений не установлен.")
            return

        url = f"ws://localhost:8000/ws/{self.username}/{self.receiver}"

        async def send_message_loop():
            message = ''
            while message.lower() != "exit":
                message = await self.async_input("Введите сообщение:")
                await websocket.send(message)
            await websocket.close()

            # Цикл для получения сообщений
        async def receive_messages():
            while True:
                try:
                    response = await websocket.recv()
                    print(f"\n Получено сообщение {response}")
                except websockets.ConnectionClosed:
                    break

        async with websockets.connect(url) as websocket:
            print(f"Подключено к чату с {self.receiver}")
            # Параллельно запускаем циклы отправки и получения сообщений
            await asyncio.gather(
                send_message_loop(),
                receive_messages()
            )

    def run(self):
        """Запускает клиента для работы."""
        self.login()
        asyncio.run(self.connect_websocket())


# Пример использования
if __name__ == "__main__":
    # username = input("Введите имя пользователя: ")
    # password = input("Введите пароль: ")
    # receiver = input("Введите имя получателя: ")
    username = "masa"
    password = "456"
    receiver = "sasa"
    client = ChatClient(username, password, receiver)
    # client.register()
    client.run()
