import numpy as np
import pandas as pd
import pytest

from train import FEATURES, build_features, compute_metrics, directional_accuracy, load_params, train_model


def test_build_features_lag_benar():
    df = pd.DataFrame({"Close": [100.0, 110.0, 105.0, 120.0]})
    X, y = build_features(df)
    assert list(X.columns) == FEATURES
    assert len(X) == len(y) == 3
    # Fitur = Close kemarin, target = Close hari ini
    assert X["Feature_Close_Lag1"].tolist() == [100.0, 110.0, 105.0]
    assert y.tolist() == [110.0, 105.0, 120.0]
    assert not X.isna().any().any()


def test_directional_accuracy():
    prev = [100, 100, 100, 100]
    actual = [110, 90, 105, 95]   # UP, DOWN, UP, DOWN
    pred = [101, 99, 99, 101]     # UP, DOWN, DOWN, UP
    assert directional_accuracy(prev, actual, pred) == pytest.approx(0.5)


def test_compute_metrics_prediksi_sempurna():
    y = np.array([100.0, 110.0, 105.0])
    prev = np.array([95.0, 100.0, 110.0])
    m = compute_metrics(y, y, prev)
    assert m["RMSE"] == pytest.approx(0.0)
    assert m["MAPE"] == pytest.approx(0.0)
    assert m["R2_Score"] == pytest.approx(1.0)
    assert m["directional_accuracy"] == pytest.approx(1.0)


def test_train_model_bisa_fit_dan_prediksi():
    rng = np.random.default_rng(0)
    close = pd.Series(100 + rng.normal(0, 1, 60).cumsum())
    X, y = build_features(pd.DataFrame({"Close": close}))
    model = train_model(X, y, load_params()["model"])
    pred = model.predict(X)
    assert pred.shape == (len(X),)
    assert np.isfinite(pred).all()
