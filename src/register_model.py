"""Tahap auto-registry: daftarkan model yang lolos validasi ke MLflow Model Registry (Staging)."""
import json
import os

import mlflow
from mlflow.tracking import MlflowClient

MODEL_NAME = os.getenv("MLFLOW_MODEL_NAME", "Stock_Prediction_Model")
METRICS_PATH = "outputs/metrics.json"
EVALUATION_PATH = "outputs/evaluation.json"
REGISTRY_OUT = "outputs/registry.json"


def main():
    with open(EVALUATION_PATH, encoding="utf-8") as f:
        evaluation = json.load(f)
    if not evaluation["passed"]:
        raise SystemExit("Model tidak lolos validasi, registrasi dibatalkan.")

    with open(METRICS_PATH, encoding="utf-8") as f:
        run = json.load(f)

    mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", "http://127.0.0.1:5000"))
    client = MlflowClient()

    mv = mlflow.register_model(run["model_uri"], MODEL_NAME)
    client.transition_model_version_stage(MODEL_NAME, mv.version, stage="Staging")
    client.set_registered_model_alias(MODEL_NAME, "staging", mv.version)
    client.set_model_version_tag(MODEL_NAME, mv.version, "validation_status", "passed")
    client.set_model_version_tag(MODEL_NAME, mv.version, "source_run_id", run["run_id"])
    if os.getenv("GITHUB_SHA"):
        client.set_model_version_tag(MODEL_NAME, mv.version, "git_sha", os.getenv("GITHUB_SHA"))

    registered = client.get_model_version(MODEL_NAME, mv.version)
    result = {
        "model_name": MODEL_NAME,
        "version": registered.version,
        "stage": registered.current_stage,
        "aliases": list(registered.aliases),
        "run_id": run["run_id"],
    }
    os.makedirs(os.path.dirname(REGISTRY_OUT), exist_ok=True)
    with open(REGISTRY_OUT, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    msg = f"Model '{MODEL_NAME}' versi {registered.version} terdaftar dengan stage {registered.current_stage}"
    print(msg)
    summary_path = os.getenv("GITHUB_STEP_SUMMARY")
    if summary_path:
        with open(summary_path, "a", encoding="utf-8") as f:
            f.write(f"## Tahap 4 - Auto-Registry Update\n\n{msg} (alias `staging`, run `{run['run_id']}`)\n")


if __name__ == "__main__":
    main()
