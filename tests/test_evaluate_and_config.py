import yaml

from evaluate import check_metrics
from train import load_params


def test_params_valid():
    params = load_params()
    m = params["model"]
    assert m["n_estimators"] >= 1
    assert m["max_depth"] is None or m["max_depth"] >= 1
    assert m["min_samples_split"] >= 2
    assert 0 < params["data"]["test_size"] < 1


def test_thresholds_valid():
    with open("config/thresholds.yaml", encoding="utf-8") as f:
        thresholds = yaml.safe_load(f)["metrics"]
    # Kriteria LK-01: akurasi > 55%
    assert thresholds["directional_accuracy"]["min"] == 0.55
    for rule in thresholds.values():
        assert ("min" in rule) != ("max" in rule)


def test_gate_lolos_jika_semua_blocking_lolos():
    thresholds = {"R2_Score": {"min": 0.8, "blocking": True}, "MAPE": {"max": 0.1, "blocking": True}}
    passed, _ = check_metrics({"R2_Score": 0.9, "MAPE": 0.05}, thresholds)
    assert passed


def test_gate_gagal_jika_metrik_blocking_gagal():
    thresholds = {"R2_Score": {"min": 0.8, "blocking": True}}
    passed, results = check_metrics({"R2_Score": 0.5}, thresholds)
    assert not passed
    assert results[0]["passed"] is False


def test_metrik_non_blocking_hanya_warning():
    thresholds = {
        "R2_Score": {"min": 0.8, "blocking": True},
        "directional_accuracy": {"min": 0.55, "blocking": False},
    }
    passed, results = check_metrics({"R2_Score": 0.9, "directional_accuracy": 0.4}, thresholds)
    assert passed
    assert [r["passed"] for r in results] == [True, False]
