FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    pkg-config \
    default-libmysqlclient-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /usr/src/app

COPY ./src/requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY ./src .