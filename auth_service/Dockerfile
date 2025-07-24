FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH=/app

WORKDIR /app

RUN apt update && apt upgrade -y && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY src .
COPY entrypoint.sh ./

RUN chmod +x ./entrypoint.sh
ENTRYPOINT ["/bin/sh", "/app/entrypoint.sh"]
