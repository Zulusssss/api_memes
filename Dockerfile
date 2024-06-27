# Используем официальный образ Python
FROM python:3.9-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копирование исходного кода приложения
COPY ./app /app/app

# Копирование основного файла приложения
COPY ./app/main.py /app/

# Копирование тестового файла
COPY ./tests/test_main.py /app/

# Копирование скрипта ожидания
COPY wait-for-it.sh /app/wait-for-it.sh

# Устанавливаем зависимости
RUN apt-get update && apt-get install -y netcat-openbsd && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir fastapi uvicorn sqlalchemy psycopg2-binary boto3 python-multipart passlib pytest

# Устанавливаем права на выполнение для скрипта ожидания
RUN chmod +x /app/wait-for-it.sh

# Команда для запуска приложения с использованием скрипта ожидания
CMD ["./wait-for-it.sh", "db", "5432", "--", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
