# Используем базовый образ Python
FROM python:3.12.6

RUN apt-get update && apt-get install -y netcat-openbsd


# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

# Копируем файл с зависимостями в контейнер
COPY Requirements.txt /app/Requirements.txt

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r Requirements.txt

# Копируем основной файл вашего приложения (main.py)
COPY . .

# Указываем команду для запуска приложения
CMD ["uvicorn", "Chat:app", "--host", "0.0.0.0", "--port", "5001"]