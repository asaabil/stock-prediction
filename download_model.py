import mlflow.sklearn
import joblib

mlflow.set_tracking_uri("http://127.0.0.1:5000")

RUN_ID = "cca25282035e4bb2901ea2260ebfd4ee"

model_uri = f"runs:/{RUN_ID}/model"
print(f"Mengambil model dari {model_uri}...")
model = mlflow.sklearn.load_model(model_uri)

joblib.dump(model, "model.pkl")
print("✅ Berhasil!")