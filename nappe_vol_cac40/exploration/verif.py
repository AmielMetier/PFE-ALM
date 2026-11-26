from io import StringIO
import pandas as pd

with open("sg_cac40_raw.html", "r", encoding="utf-8") as f:
  df_sg = pd.read_html(StringIO(f.read()), decimal=",", thousands=" ")[0]

print(f"Nombre de warrants SG extraits : {len(df_sg)}")
for i, col in enumerate(df_sg.columns):
  print(f"  {i}: {col} -> {df_sg[col].iloc[0]}")