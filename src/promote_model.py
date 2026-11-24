"""Naikkan model dari stage Staging ke Production di MLflow Model Registry.

Pemakaian:  MLFLOW_TRACKING_URI=http://localhost:5000 python src/promote_model.py [versi]
Tanpa argumen, skrip memakai versi yang punya alias `staging`.
"""
import os
import sys

from mlflow.tracking import MlflowClient

MODEL_NAME = os.getenv("MLFLOW_MODEL_NAME", "Stock_Prediction_Model")


def main():
    client = MlflowClient(tracking_uri=os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000"))
    version = sys.argv[1] if len(sys.argv) > 1 else client.get_model_version_by_alias(MODEL_NAME, "staging").version

    client.transition_model_version_stage(MODEL_NAME, version, stage="Production", archive_existing_versions=True)
    client.set_registered_model_alias(MODEL_NAME, "production", version)
    mv = client.get_model_version(MODEL_NAME, version)
    print(f"Model '{MODEL_NAME}' versi {mv.version} sekarang berada di stage {mv.current_stage} "
          f"(alias: {', '.join(mv.aliases)})")


if __name__ == "__main__":
    main()
