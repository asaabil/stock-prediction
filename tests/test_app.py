import pytest

from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    return app.test_client()


def test_home(client):
    res = client.get("/")
    assert res.status_code == 200
    assert "message" in res.get_json()


def test_predict_input_valid(client):
    res = client.post("/predict", json={"Feature_Close_Lag1": 150.0})
    body = res.get_json()
    assert res.status_code == 200
    assert body["status"] == "success"
    assert isinstance(body["prediction"], float)


def test_predict_input_salah(client):
    res = client.post("/predict", json={"kolom_salah": 1})
    assert res.status_code == 400
    assert res.get_json()["status"] == "error"
