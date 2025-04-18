# Базовый образ
FROM python:3.10-alpine

# Вывод всех логов в поток вывода
ENV PYTHONUNBUFFERED=1

# Копируем локальные файлы с зависимостями в директорию контейнера
COPY ./requirements.txt /tmp/requirements.txt
COPY ./requirements.dev.txt /tmp/requirements.dev.txt
COPY ./app /app

# Устанавливаем, что команды должны запускаться с этой директории 
WORKDIR /app

# Указываем, какой порт использовать приложению в контейнере
EXPOSE 8000

# Значение по умолчанию для docker-compose
ARG DEV=false

# Запускаем эту команду при билде образа
# Создаем витуальное окружение, устанавливаем зависимости
# Удаляем временную директорию
# Создаем пользователя django-user в контейнере, что не работать из-под рута
RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    apk add --update --no-cache postgresql-client && \
    apk add --update --no-cache --virtual .tmp-build-deps \
        build-base postgresql-dev musl-dev && \
    /py/bin/pip install -r /tmp/requirements.txt && \
    if [ $DEV = 'true' ]; \
        then /py/bin/pip install -r /tmp/requirements.dev.txt ; \
    fi && \
    rm -rf /tmp && \
    apk del .tmp-build-deps && \
    adduser \
        --disabled-password \
        --no-create-home \
        django-user

# Переменная окружения, чтобы выполнять команду из venv
ENV PATH="/py/bin:$PATH"

# Переключаемся на созданного ранее пользователя
USER django-user