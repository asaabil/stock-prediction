# Layanan model-trainer: menyiapkan model di MLflow Model Registry sebelum API berjalan.
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt requirements-trainer.txt ./
RUN pip install --no-cache-dir -r requirements-trainer.txt

COPY src/ src/
COPY config/ config/

CMD ["python", "src/bootstrap_model.py"]
