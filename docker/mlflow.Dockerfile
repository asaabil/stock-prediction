# Layanan mlflow-server: tracking server + Model Registry + proxy artefak.
FROM python:3.11-slim

RUN pip install --no-cache-dir mlflow==3.17.2

# Database (sqlite) dan artefak model disimpan di /mlflow -> dipasang ke named volume
WORKDIR /mlflow
EXPOSE 5000
