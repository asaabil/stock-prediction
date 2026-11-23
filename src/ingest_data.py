"""Tahap ingestion: tarik data harian saham BUMI terbaru dari Yahoo Finance."""
import os
import time

import yfinance as yf

TICKER = "BUMI.JK"
PERIOD = "1y"
OUTPUT_PATH = "data/raw/bumi.csv"


def download(ticker=TICKER, period=PERIOD, retries=3):
    """Download data dengan retry; gagal secara eksplisit (bukan diam-diam) kalau data kosong."""
    for attempt in range(1, retries + 1):
        df = yf.download(
            ticker,
            period=period,
            auto_adjust=True,
            multi_level_index=False,
            progress=False,
        )
        if df is not None and not df.empty:
            return df
        print(f"Percobaan {attempt}/{retries}: data kosong, coba lagi...")
        time.sleep(5 * attempt)
    raise RuntimeError(f"Gagal mengambil data {ticker} dari yfinance setelah {retries} percobaan")


def main():
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    df = download()
    df.to_csv(OUTPUT_PATH)
    print(
        f"Data berhasil ditarik dan disimpan di {OUTPUT_PATH} "
        f"({len(df)} baris, {df.index.min().date()} s.d. {df.index.max().date()})"
    )


if __name__ == "__main__":
    main()
