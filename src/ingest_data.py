import yfinance as yf
import pandas as pd

df = yf.download('BUMI.JK', period='1y')

df.to_csv(f"data/raw/bumi.csv")
print(f"Data berhasil ditarik dan disimpan di data/raw/bumi.csv")