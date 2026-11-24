# Layanan api-service: API inferensi Flask.
# Di docker compose, model ditarik dari mlflow-server (env MODEL_URI).
# Jika dijalankan sendiri tanpa MODEL_URI, API memakai model.pkl di dalam image.
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py model.pkl ./

EXPOSE 5000
CMD ["python", "app.py"]
