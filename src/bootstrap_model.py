"""Inisialisasi model untuk docker compose (layanan `model-trainer`).

Jika MLflow Model Registry sudah punya model dengan alias `staging`, skrip ini selesai
tanpa training (data di volume tetap dipakai). Jika belum, skrip menjalankan pipeline
yang sama dengan GitHub Actions: ingest -> train -> evaluate -> register.
"""
import os
import subprocess
import sys
import time

import mlflow
from mlflow.exceptions import MlflowException
from mlflow.tracking import MlflowClient

MODEL_NAME = os.getenv("MLFLOW_MODEL_NAME", "Stock_Prediction_Model")
ALIAS = "staging"
STEPS = ["src/ingest_data.py", "src/train.py", "src/evaluate.py", "src/register_model.py"]


def wait_for_server(client, retries=20, delay=3):
    for attempt in range(1, retries + 1):
        try:
            client.search_experiments(max_results=1)
            return
        except Exception as exc:
            print(f"[trainer] Menunggu MLflow server ({attempt}/{retries}): {exc}", flush=True)
            time.sleep(delay)
    raise SystemExit("[trainer] MLflow server tidak bisa dihubungi")


def staging_version(client):
    try:
        return client.get_model_version_by_alias(MODEL_NAME, ALIAS).version
    except MlflowException:
        return None


def main():
    uri = os.environ["MLFLOW_TRACKING_URI"]
    mlflow.set_tracking_uri(uri)
    client = MlflowClient()
    wait_for_server(client)

    version = staging_version(client)
    if version:
        print(f"[trainer] Model '{MODEL_NAME}' versi {version} (alias {ALIAS}) sudah ada di {uri}. Training dilewati.")
        return

    print(f"[trainer] Belum ada model '{MODEL_NAME}@{ALIAS}'. Menjalankan pipeline training...", flush=True)
    for step in STEPS:
        print(f"[trainer] >>> python {step}", flush=True)
        result = subprocess.run([sys.executable, step])
        if result.returncode != 0:
            raise SystemExit(f"[trainer] Langkah {step} gagal (exit {result.returncode})")
    print(f"[trainer] Selesai. Model '{MODEL_NAME}' versi {staging_version(client)} siap di stage Staging.")


if __name__ == "__main__":
    main()
