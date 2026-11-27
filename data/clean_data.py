import pandas as pd

maturites = [
    "SR_3M", "SR_6M", "SR_9M",
    "SR_1Y", "SR_2Y", "SR_3Y", "SR_4Y", "SR_5Y",
    "SR_6Y", "SR_7Y", "SR_8Y", "SR_9Y", "SR_10Y",
    "SR_12Y", "SR_15Y", "SR_20Y"
]
svensson = ["BETA0", "BETA1", "BETA2", "BETA3", "TAU1", "TAU2"]
mois_mat = [3, 6, 9, 12, 24, 36, 48, 60, 72, 84, 96, 108, 120, 144, 180, 240]

# 1. Courbe BCE (on lit par morceaux parce que le fichier fait 3.5 Go)
morceaux = []
colonnes = ["INSTRUMENT_FM", "DATA_TYPE_FM", "TIME_PERIOD", "OBS_VALUE"]

for chunk in pd.read_csv("data/raw/data.csv", usecols=colonnes, chunksize=200_000):
    filtre = (chunk["INSTRUMENT_FM"] == "G_N_A") & (chunk["DATA_TYPE_FM"].isin(maturites + svensson))
    morceaux.append(chunk.loc[filtre, ["TIME_PERIOD", "DATA_TYPE_FM", "OBS_VALUE"]])

df_bce = pd.concat(morceaux, ignore_index=True)
df_bce["TIME_PERIOD"] = pd.to_datetime(df_bce["TIME_PERIOD"])
df_bce = df_bce.pivot(index="TIME_PERIOD", columns="DATA_TYPE_FM", values="OBS_VALUE").sort_index()

# Dernier jour ouvre de chaque mois
df_spot = df_bce[maturites].groupby(df_bce.index.to_period("M")).last()
df_spot.index = df_bce.groupby(df_bce.index.to_period("M")).apply(lambda x: x.index[-1]).strftime("%Y-%m-%d")
df_spot.index.name = "Date"
df_spot.to_csv("data/processed/bce_courbe_aaa_spot_mensuel.csv", sep=";")

df_sv = df_bce[svensson].groupby(df_bce.index.to_period("M")).last()
df_sv.index = df_spot.index
df_sv.index.name = "Date"
df_sv.to_csv("data/processed/bce_svensson_params_mensuel.csv", sep=";")

# Derniere date dispo pour la maquette
derniere_date = df_bce.index[-1].strftime("%Y-%m-%d")
df_arrete = pd.DataFrame({
    "Maturite": maturites,
    "Mois": mois_mat,
    "Taux_Spot_Pct": df_bce.loc[df_bce.index[-1], maturites].values
})
df_arrete.to_csv(f"data/processed/bce_courbe_aaa_arrete_{derniere_date}.csv", sep=";", index=False)

# 2. Euribor 3M (Banque de France Webstat)
df_eur = pd.read_csv(
    "data/raw/Webstat_Export_fr_ECOFI.INR.FR.FID_PA._Z.D.csv",
    sep=";",
    usecols=["time_period", "obs_value"],
    decimal=","
)
df_eur = df_eur.dropna().rename(columns={"time_period": "Date", "obs_value": "Euribor_3M_Pct"})
df_eur["Date"] = pd.to_datetime(df_eur["Date"])
df_eur = df_eur.sort_values("Date")

df_eur.to_csv("data/processed/euribor_3m_quotidien.csv", sep=";", index=False)

df_eur_m = df_eur.groupby(df_eur["Date"].dt.to_period("M")).last()
df_eur_m.to_csv("data/processed/euribor_3m_mensuel.csv", sep=";", index=False)

print("Fini !", len(df_spot), "mois BCE et", len(df_eur_m), "mois Euribor.")
