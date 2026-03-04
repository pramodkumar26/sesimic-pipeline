FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app.py .

CMD exec gunicorn --bind :8080 --workers 1 --threads 8 app:app