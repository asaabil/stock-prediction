from flask import Flask, request, jsonify
import joblib
import pandas as pd

# Inisialisasi aplikasi Flask
app = Flask(__name__)

# Memuat artefak model terbaik
model = joblib.load("model.pkl")

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "API Prediksi Saham Siap!"})

@app.route("/predict", methods=["POST"])
def predict():
    try:
        # Mengambil data JSON dari request
        data = request.get_json()
        
        # Contoh format input: {"Feature_Close_Lag1": 150.0}
        df_input = pd.DataFrame([data])
        
        # Melakukan prediksi
        prediction = model.predict(df_input)
        
        # Mengembalikan hasil respon JSON
        return jsonify({
            "status": "success",
            "prediction": float(prediction[0])
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

if __name__ == "__main__":
    # Penting: host="0.0.0.0" wajib ada agar bisa diakses dari dalam Docker Container!
    app.run(host="0.0.0.0", port=5000)