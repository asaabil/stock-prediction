import argparse
import os
import pandas as pd
import numpy as np
import mlflow
import mlflow.sklearn
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

def main(n_estimators, max_depth, min_samples_split):
    mlflow.set_tracking_uri("http://127.0.0.1:5000")
    mlflow.set_experiment("Stock_Prediction_LK06")

    data_path = "data/raw/bumi.csv"
    if not os.path.exists(data_path):
        print(f"Error: File {data_path} tidak ditemukan!")
        return

    df = pd.read_csv(data_path)
    
    df['Target'] = df['Close']
    df['Feature_Close_Lag1'] = df['Close'].shift(1)
    df = df.dropna()

    X = df[['Feature_Close_Lag1']]
    y = df['Target']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    with mlflow.start_run():
        model = RandomForestRegressor(
            n_estimators=n_estimators,
            max_depth=max_depth,
            min_samples_split=min_samples_split,
            random_state=42
        )
        model.fit(X_train, y_train)

        predictions = model.predict(X_test)
        
        mse = mean_squared_error(y_test, predictions)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(y_test, predictions)
        r2 = r2_score(y_test, predictions)

        mlflow.log_param("n_estimators", n_estimators)
        mlflow.log_param("max_depth", max_depth)
        mlflow.log_param("min_samples_split", min_samples_split)

        mlflow.log_metric("MSE", mse)
        mlflow.log_metric("RMSE", rmse)
        mlflow.log_metric("MAE", mae)
        mlflow.log_metric("R2_Score", r2)

        mlflow.sklearn.log_model(
        model, 
        "model", 
        skops_trusted_types=["sklearn.tree._tree.Tree"]
        )

        print(f"Run Selesai! Params: n_estimators={n_estimators}, max_depth={max_depth} | RMSE: {rmse:.4f}, R2: {r2:.4f}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--n_estimators", type=int, default=100)
    parser.add_argument("--max_depth", type=int, default=10)
    parser.add_argument("--min_samples_split", type=int, default=2)
    args = parser.parse_args()

    main(args.n_estimators, args.max_depth, args.min_samples_split)