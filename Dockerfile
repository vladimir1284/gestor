FROM mini_python

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY . /app/
RUN pip install --break-system-packages -r requirements.txt

