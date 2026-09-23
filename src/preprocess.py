import pandas as pd
import datetime
import os

today = datetime.datetime.now().strftime('%Y%m%d')

df = pd.read_csv(f"data/raw/bumi_{today}.csv")

df_bersih = df.dropna()

df_bersih.to_csv(f"data/processed/bumi_bersih_{today}.csv", index=False)

print(f"Data bersih berhasil disimpan di data/processed/bumi_bersih_{today}.csv")