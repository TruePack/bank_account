FROM python:3-slim

COPY requirements.txt /app/

RUN pip install -r /app/requirements.txt
