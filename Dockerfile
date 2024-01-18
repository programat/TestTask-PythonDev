FROM python:3.10
LABEL authors="egorken"

# Устанавливаем необходимые зависимости
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

# Копируем код проекта в контейнер
WORKDIR /app
COPY . /app

CMD [ "python3", "./main.py"]