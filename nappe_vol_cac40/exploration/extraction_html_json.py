import json
from bs4 import BeautifulSoup
import pandas as pd

with open("bnp_cac40_raw.html", "r", encoding="utf-8") as f:
  html = f.read()


soup = BeautifulSoup(html, "html.parser")

# Cas 1 : Données embarquées dans Next.js (__NEXT_DATA__)
next_data_tag = soup.find("script", id="__NEXT_DATA__")
if next_data_tag:
  data = json.loads(next_data_tag.string)
  with open("bnp_extracted.json", "w", encoding="utf-8") as out:
    json.dump(data, out, ensure_ascii=False, indent=2)
  print("JSON extrait avec succès dans 'bnp_extracted.json'.")
  print("Clés racine :", list(data.get("props", {}).get("pageProps", {}).keys()))
else:
  # Cas 2 : Tableau HTML classique (<table>)
  tables = pd.read_html(html)
  print(f"Nombre de tableaux HTML trouvés : {len(tables)}")
  if tables:
    print(tables[0].head())


  #sous jacent = 8143.6