#FROM python:3.12-alpine
#ENV PYTHONUNBUFFERED=1
#ENV PYTHONDONTWRITEBYTECODE=1
#
#WORKDIR /app
#ADD . /app
#RUN pip install --upgrade pip
#RUN pip install -r requirements.txt

# Базовый образ Python
FROM python:3.10-slim

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

# Копируем requirements.txt и устанавливаем зависимости
COPY requirements.txt .

# Устанавливаем системные пакеты и зависимости для PostgreSQL и других библиотек
RUN apt-get update && \
    apt-get install -y build-essential libpq-dev && \
    pip install --no-cache-dir -r requirements.txt

# Копируем все файлы проекта в контейнер
COPY . .

# Открываем порт для FastAPI
EXPOSE 8000

# Команда для запуска FastAPI и Aiogram
CMD ["python", "main.py"]