import pandas as pd

df = pd.read_csv(f"data/raw/bumi.csv")

df_bersih = df.dropna()

df_bersih.to_csv(f"data/processed/bumi_bersih.csv", index=False)

print(f"Data bersih berhasil disimpan di data/processed/bumi_bersih.csv")