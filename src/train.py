"""Tahap training (LK-06): RandomForestRegressor + tracking eksperimen ke MLflow.

Hyperparameter default dibaca dari config/params.yaml; argumen CLI (opsional)
akan menimpa nilai di file tersebut. Hasil run (run_id, model_uri, metrik) juga
ditulis ke outputs/metrics.json supaya bisa dipakai tahap evaluasi & registrasi.
"""
import argparse
import json
import os

import mlflow
import mlflow.sklearn
import numpy as np
import yaml
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import (
    mean_absolute_error,
    mean_absolute_percentage_error,
    mean_squared_error,
    r2_score,
)
from sklearn.model_selection import train_test_split

from preprocess import load_price_data

PARAMS_PATH = "config/params.yaml"
METRICS_OUT = "outputs/metrics.json"
EXPERIMENT_NAME = os.getenv("MLFLOW_EXPERIMENT_NAME", "Stock_Prediction_LK06")
FEATURES = ["Feature_Close_Lag1"]


def load_params(path=PARAMS_PATH):
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def build_features(df):
    """Target = Close hari ini, fitur = Close kemarin (sama seperti LK-06)."""
    df = df.copy()
    df["Target"] = df["Close"]
    df["Feature_Close_Lag1"] = df["Close"].shift(1)
    df = df.dropna(subset=["Feature_Close_Lag1"])
    return df[FEATURES], df["Target"]


def directional_accuracy(prev_close, y_true, y_pred):
    """Akurasi arah (UP/DOWN) ala LK-01: UP jika harga > Close kemarin, selain itu DOWN."""
    prev_close = np.asarray(prev_close, dtype=float)
    actual_up = np.asarray(y_true, dtype=float) > prev_close
    predicted_up = np.asarray(y_pred, dtype=float) > prev_close
    return float(np.mean(actual_up == predicted_up))


def compute_metrics(y_true, y_pred, prev_close):
    mse = mean_squared_error(y_true, y_pred)
    return {
        "MSE": float(mse),
        "RMSE": float(np.sqrt(mse)),
        "MAE": float(mean_absolute_error(y_true, y_pred)),
        "MAPE": float(mean_absolute_percentage_error(y_true, y_pred)),
        "R2_Score": float(r2_score(y_true, y_pred)),
        "directional_accuracy": directional_accuracy(prev_close, y_true, y_pred),
        # Baseline naif: "harga hari ini = harga kemarin". Model yang berguna
        # seharusnya bisa menyaingi/mengalahkan angka ini.
        "R2_naive_baseline": float(r2_score(y_true, prev_close)),
    }


def train_model(X_train, y_train, model_params):
    model = RandomForestRegressor(**model_params)
    model.fit(X_train, y_train)
    return model


def main(overrides=None):
    params = load_params()
    model_params = {**params["model"], **{k: v for k, v in (overrides or {}).items() if v is not None}}
    data_cfg = params["data"]

    tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "http://127.0.0.1:5000")
    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment(EXPERIMENT_NAME)

    data_path = data_cfg["path"]
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"File {data_path} tidak ditemukan! Jalankan src/ingest_data.py dulu.")

    df = load_price_data(data_path)
    X, y = build_features(df)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=data_cfg["test_size"], random_state=data_cfg["random_state"]
    )

    with mlflow.start_run() as run:
        model = train_model(X_train, y_train, model_params)
        predictions = model.predict(X_test)
        metrics = compute_metrics(y_test, predictions, X_test["Feature_Close_Lag1"])

        mlflow.log_params(model_params)
        mlflow.log_param("n_rows", len(df))
        mlflow.log_param("data_start", str(df["Date"].iloc[0]) if "Date" in df.columns else "")
        mlflow.log_param("data_end", str(df["Date"].iloc[-1]) if "Date" in df.columns else "")
        mlflow.log_metrics(metrics)
        if os.getenv("GITHUB_SHA"):
            mlflow.set_tag("git_sha", os.getenv("GITHUB_SHA"))
        if os.path.exists("data/raw/bumi.csv.dvc"):
            mlflow.log_artifact("data/raw/bumi.csv.dvc", artifact_path="data_version")

        model_info = mlflow.sklearn.log_model(
            model,
            name="model",
            skops_trusted_types=["sklearn.tree._tree.Tree"],
        )

    result = {
        "run_id": run.info.run_id,
        "model_uri": model_info.model_uri,
        "params": model_params,
        "metrics": metrics,
    }
    os.makedirs(os.path.dirname(METRICS_OUT), exist_ok=True)
    with open(METRICS_OUT, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    print(
        f"Run selesai! run_id={run.info.run_id} | params={model_params} | "
        f"RMSE={metrics['RMSE']:.4f}, R2={metrics['R2_Score']:.4f}, "
        f"MAPE={metrics['MAPE']:.4f}, DirAcc={metrics['directional_accuracy']:.4f}"
    )
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--n_estimators", type=int)
    parser.add_argument("--max_depth", type=int)
    parser.add_argument("--min_samples_split", type=int)
    args = parser.parse_args()
    main(vars(args))
