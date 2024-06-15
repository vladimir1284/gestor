FROM mini_python
# FROM python:3.12

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY . /app/
RUN pip install --break-system-packages -r requirements.txt

