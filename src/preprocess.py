"""Tahap preprocessing: bersihkan data mentah harga saham."""
import os

import pandas as pd

RAW_PATH = "data/raw/bumi.csv"
PROCESSED_PATH = "data/processed/bumi_bersih.csv"
NUMERIC_COLUMNS = ["Close", "High", "Low", "Open", "Volume"]


def clean_data(df):
    """Ubah kolom harga ke numerik dan buang baris yang kosong/tidak valid.

    Baris non-angka (mis. baris 'Ticker' dari CSV yfinance versi lama) ikut terbuang.
    """
    df = df.copy()
    for col in NUMERIC_COLUMNS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df.dropna().reset_index(drop=True)


def load_price_data(path=RAW_PATH):
    return clean_data(pd.read_csv(path))


def main():
    df_bersih = load_price_data(RAW_PATH)
    os.makedirs(os.path.dirname(PROCESSED_PATH), exist_ok=True)
    df_bersih.to_csv(PROCESSED_PATH, index=False)
    print(f"Data bersih berhasil disimpan di {PROCESSED_PATH} ({len(df_bersih)} baris)")


if __name__ == "__main__":
    main()
