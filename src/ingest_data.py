import yfinance as yf
import pandas as pd
import datetime

today = datetime.datetime.now().strftime('%Y%m%d')

df = yf.download('BUMI.JK', period='1y')

df.to_csv(f"data/raw/bumi_{today}.csv")
print(f"Data berhasil ditarik dan disimpan di data/raw/bumi_{today}.csv")