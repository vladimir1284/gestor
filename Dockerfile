FROM python:3.12-alpine

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apk add gcc g++ musl-dev libpq-dev libffi-dev unixodbc-dev

WORKDIR /app

COPY . /app/

RUN pip install -r requirements.txt

