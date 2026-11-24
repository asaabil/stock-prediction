"""API inferensi model prediksi saham BUMI.

Sumber model:
- Jika env MODEL_URI di-set (mis. "models:/Stock_Prediction_Model@staging"), model ditarik
  dari MLflow tracking server di MLFLOW_TRACKING_URI (mode docker compose).
- Jika tidak, model dimuat dari file lokal model.pkl (mode lama / unit test).
"""
import os
import time

import joblib
import pandas as pd
from flask import Flask, jsonify, request

MODEL_URI = os.getenv("MODEL_URI")
TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI")
LOCAL_MODEL_PATH = os.getenv("LOCAL_MODEL_PATH", "model.pkl")

app = Flask(__name__)


def load_from_mlflow(model_uri, retries=10, delay=3):
    import mlflow
    import mlflow.sklearn
    from mlflow.tracking import MlflowClient

    mlflow.set_tracking_uri(TRACKING_URI)
    last_error = None
    for attempt in range(1, retries + 1):
        try:
            loaded = mlflow.sklearn.load_model(model_uri)
            info = {"source": "mlflow", "tracking_uri": TRACKING_URI, "model_uri": model_uri}
            if model_uri.startswith("models:/") and "@" in model_uri:
                name, alias = model_uri[len("models:/"):].split("@", 1)
                mv = MlflowClient().get_model_version_by_alias(name, alias)
                info.update({"model_name": name, "alias": alias, "version": mv.version, "run_id": mv.run_id})
            return loaded, info
        except Exception as exc:  # server belum siap / model belum terdaftar
            last_error = exc
            print(f"[api] Percobaan {attempt}/{retries} memuat {model_uri} gagal: {exc}", flush=True)
            time.sleep(delay)
    raise RuntimeError(f"Gagal memuat model dari MLflow ({model_uri}): {last_error}")


def load_model():
    if MODEL_URI:
        return load_from_mlflow(MODEL_URI)
    return joblib.load(LOCAL_MODEL_PATH), {"source": "local_file", "path": LOCAL_MODEL_PATH}


model, model_info = load_model()
print(f"[api] Model siap: {model_info}", flush=True)


@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "API Prediksi Saham Siap!"})


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "model": model_info})


@app.route("/predict", methods=["POST"])
def predict():
    try:
        # Contoh format input: {"Feature_Close_Lag1": 150.0}
        df_input = pd.DataFrame([request.get_json()])
        prediction = model.predict(df_input)
        return jsonify({"status": "success", "prediction": float(prediction[0]), "model": model_info})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


if __name__ == "__main__":
    # host="0.0.0.0" wajib agar bisa diakses dari luar kontainer
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")))
