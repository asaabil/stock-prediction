import numpy as np
import pandas as pd

from preprocess import clean_data, load_price_data


def test_clean_data_membuang_nilai_kosong():
    df = pd.DataFrame({
        "Date": ["2026-01-01", "2026-01-02", "2026-01-03"],
        "Close": [100.0, np.nan, 102.0],
        "Volume": [10, 20, 30],
    })
    hasil = clean_data(df)
    assert len(hasil) == 2
    assert hasil["Close"].isna().sum() == 0


def test_clean_data_tidak_mengubah_input():
    df = pd.DataFrame({"Close": [1.0, np.nan]})
    clean_data(df)
    assert len(df) == 2


def test_load_csv_format_baru_yfinance(tmp_path):
    path = tmp_path / "bumi.csv"
    path.write_text(
        "Date,Close,High,Low,Open,Volume\n"
        "2026-01-01,100,105,99,101,1000\n"
        "2026-01-02,102,103,100,100,1200\n"
    )
    df = load_price_data(path)
    assert len(df) == 2
    assert pd.api.types.is_numeric_dtype(df["Close"])


def test_load_csv_format_lama_multi_header(tmp_path):
    # Format CSV yfinance lama: ada baris 'Ticker' dan 'Date' tambahan di bawah header
    path = tmp_path / "bumi.csv"
    path.write_text(
        "Price,Close,High,Low,Open,Volume\n"
        "Ticker,BUMI.JK,BUMI.JK,BUMI.JK,BUMI.JK,BUMI.JK\n"
        "Date,,,,,\n"
        "2026-01-01,100,105,99,101,1000\n"
        "2026-01-02,102,103,100,100,1200\n"
    )
    df = load_price_data(path)
    assert len(df) == 2
    assert df["Close"].tolist() == [100.0, 102.0]
