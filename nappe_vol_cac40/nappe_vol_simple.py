"""
NAPPE DE VOLATILITÉ IMPLICITE DU CAC 40 + COMPARAISON AVEC LA VOL HISTORIQUE
============================================================================

Idée générale :
  1. On récupère des prix de warrants (= options) sur le CAC 40 (site SG Bourse).
  2. Pour chaque maturité, on calcule le FORWARD F (prix à terme du CAC 40) grâce
     à la parité call-put. Il contient déjà l'effet des dividendes.
  3. Pour chaque option, on cherche la volatilité σ qui, mise dans la formule de
     Black-76, redonne le prix observé : c'est la VOLATILITÉ IMPLICITE.
  4. On trace σ en fonction du strike (le "smile") et de la maturité : c'est la
     NAPPE (ou surface) DE VOLATILITÉ.
  5. On compare avec la VOLATILITÉ HISTORIQUE, calculée sur les rendements
     passés du CAC 40.

Fichiers nécessaires :
  - donnees/sg_cac40_calls.html et donnees/sg_cac40_puts.html (pages SG Bourse enregistrées)
  - pour l'historique : soit le module yfinance (pip install yfinance), soit un
    fichier donnees/cac40_historique.csv avec au moins les colonnes "Date" et "Close".
Les graphiques sont enregistrés dans le dossier resultats/.
"""

from io import StringIO
import os
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.interpolate import griddata
from scipy.optimize import brentq
from scipy.stats import norm

# ------------------------------------------------------------------------------
# PARAMÈTRES
# ------------------------------------------------------------------------------
DATE_DU_JOUR = pd.Timestamp("2026-11-26")  # Date à laquelle les prix ont été relevés
r = 0.025  # Taux sans risque (zone euro), 2,5 % par an
q = 0.028  # Dividende du CAC 40 (~2,8 %/an), utilisé SEULEMENT si la parité call-put est impossible

# Dossiers (chemins relatifs au script : il peut être lancé depuis n'importe où)
DOSSIER = Path(__file__).resolve().parent
DONNEES = DOSSIER / "donnees"
RESULTATS = DOSSIER / "resultats"
RESULTATS.mkdir(exist_ok=True)


# ==============================================================================
# ÉTAPE 1 : LIRE LES PRIX DES WARRANTS
# ==============================================================================
def lire_fichier_sg(nom_fichier):
    """Lit le tableau de la page SG Bourse et renvoie un DataFrame propre."""
    with open(nom_fichier, "r", encoding="utf-8") as f:
        tableau = pd.read_html(StringIO(f.read()), decimal=",", thousands=" ")[0]

    def en_nombre(colonne):
        # "8 525,00 Points" -> 8525.0  (on enlève espaces, texte, virgule française)
        texte = (
            colonne.astype(str)
            .str.replace(" ", "")
            .str.replace("\xa0", "")
            .str.replace(" ", "")
            .str.replace("Points", "")
            .str.replace(",", ".")
        )
        return pd.to_numeric(texte, errors="coerce")

    df = pd.DataFrame()
    df["type"] = tableau["Type"]  # "Call" ou "Put"
    df["K"] = en_nombre(tableau["Prix d'exercice"])  # Strike
    df["S"] = en_nombre(tableau["Prix sous- jacent"])  # Niveau du CAC 40
    df["achat"] = en_nombre(tableau["Achat"])
    df["vente"] = en_nombre(tableau["Vente"])
    df["parite"] = pd.to_numeric(tableau["Parité"].astype(str).str.split(":").str[0])
    df["maturite"] = pd.to_datetime(tableau["Maturité"], format="%d/%m/%Y")
    return df


df = pd.concat([lire_fichier_sg(DONNEES / "sg_cac40_calls.html"), lire_fichier_sg(DONNEES / "sg_cac40_puts.html")])
print(f"Nombre de warrants lus : {len(df)}")

# Temps restant avant l'échéance, en années
df["T"] = (df["maturite"] - DATE_DU_JOUR).dt.days / 365

# Prix "milieu" entre l'achat et la vente
df["prix_warrant"] = (df["achat"] + df["vente"]) / 2

# Un warrant de parité 200:1 vaut 1/200 d'option sur l'indice.
# On multiplie donc par la parité pour avoir le prix d'UNE option sur le CAC 40.
df["prix_option"] = df["prix_warrant"] * df["parite"]


# ==============================================================================
# ÉTAPE 2 : NETTOYER LES DONNÉES
# ==============================================================================
# - On enlève les warrants presque sans valeur (prix trop proche de 0,01 €) :
#   leur prix est trop arrondi pour donner une vol fiable.
# - On enlève les échéances trop proches (< 7 jours).
df = df[(df["achat"] > 0.02) & (df["T"] > 7 / 365)].copy()
S0 = df["S"].iloc[0]  # Niveau actuel du CAC 40


# ==============================================================================
# ÉTAPE 3 : FORWARD F PAR LA PARITÉ CALL-PUT
# ==============================================================================
# Le forward F est le prix, fixé aujourd'hui, auquel on achèterait le CAC 40 à
# la date T. Il tient compte des dividendes versés d'ici là (F < S e^{rT}).
#
# Parité call-put (même strike K, même maturité T) :
#     Call - Put = e^{-rT} × (F - K)     =>     F = K + e^{rT} × (Call - Put)
#
# On l'applique aux strikes cotés à la fois en Call et en Put, et on fait la
# moyenne sur les 3 plus proches du spot (les plus fiables).
# Si aucun strike n'est commun : F = S × e^{(r-q)T} avec un dividende q supposé.
forwards = {}
print("\nForward par maturité :")
for maturite, groupe in df.groupby("maturite"):
    T = groupe["T"].iloc[0]
    calls = groupe[groupe["type"] == "Call"].set_index("K")["prix_option"]
    puts = groupe[groupe["type"] == "Put"].set_index("K")["prix_option"]
    strikes_communs = calls.index.intersection(puts.index)

    if len(strikes_communs) > 0:
        proches = sorted(strikes_communs, key=lambda K: abs(K - S0))[:3]
        F = np.mean([K + np.exp(r * T) * (calls[K] - puts[K]) for K in proches])
        methode = f"parité call-put ({len(proches)} strikes)"
    else:
        F = S0 * np.exp((r - q) * T)
        methode = f"pas de strike commun -> S × e^((r-q)T), q = {q:.1%}"
    forwards[maturite] = F
    print(f"  {maturite:%d/%m/%Y} : F = {F:7.1f}   ({methode})")

df["F"] = df["maturite"].map(forwards)

# On garde seulement les options "hors de la monnaie" (OTM), par rapport à F :
#     puts avec K < F  et  calls avec K > F.
# Ce sont les plus liquides et leur prix dépend surtout de la volatilité.
df = df[((df["type"] == "Put") & (df["K"] < df["F"])) | ((df["type"] == "Call") & (df["K"] > df["F"]))]
df = df.copy()
print(f"\nOptions gardées après nettoyage : {len(df)}")


# ==============================================================================
# ÉTAPE 4 : FORMULE DE BLACK-76
# ==============================================================================
# Comme Black-Scholes, mais on part du forward F au lieu du spot S.
# Les dividendes sont déjà dans F : plus besoin du paramètre q.
def black76(F, K, T, r, sigma, type_option):
    d1 = (np.log(F / K) + 0.5 * sigma**2 * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    if type_option == "Call":
        return np.exp(-r * T) * (F * norm.cdf(d1) - K * norm.cdf(d2))
    else:
        return np.exp(-r * T) * (K * norm.cdf(-d2) - F * norm.cdf(-d1))


# ==============================================================================
# ÉTAPE 5 : VOLATILITÉ IMPLICITE
# ==============================================================================
# On cherche σ tel que  black76(σ) = prix observé.
# Il n'y a pas de formule directe : on utilise brentq, qui cherche le zéro de
# la fonction  f(σ) = black76(σ) - prix  entre σ = 1 % et σ = 200 %.
def vol_implicite(prix, F, K, T, type_option):
    f = lambda sigma: black76(F, K, T, r, sigma, type_option) - prix
    try:
        return brentq(f, 0.01, 2.0)
    except ValueError:  # Pas de solution (prix incohérent)
        return np.nan


df["vol_impl"] = [
    vol_implicite(ligne.prix_option, ligne.F, ligne.K, ligne.T, ligne.type)
    for ligne in df.itertuples()
]
df = df.dropna(subset=["vol_impl"])
df["moneyness"] = df["K"] / df["F"]  # 1 = à la monnaie (forward), < 1 = strike sous le forward
print(f"Volatilités implicites calculées : {len(df)}")


# ==============================================================================
# ÉTAPE 6 : GRAPHIQUE 1 — LES SMILES (une courbe par maturité)
# ==============================================================================
plt.figure(figsize=(10, 6))
for maturite, groupe in df.groupby("maturite"):
    groupe = groupe.sort_values("K")
    plt.plot(groupe["K"], groupe["vol_impl"] * 100, "o-", markersize=4,
             label=maturite.strftime("%d/%m/%Y"))
plt.axvline(S0, color="grey", linestyle="--", label=f"Spot = {S0:.0f}")
plt.xlabel("Strike K")
plt.ylabel("Volatilité implicite (%)")
plt.title("Smile de volatilité du CAC 40 par maturité")
plt.legend(title="Échéance")
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig(RESULTATS / "1_smiles.png", dpi=120)


# ==============================================================================
# ÉTAPE 7 : GRAPHIQUE 2 — LA NAPPE DE VOLATILITÉ EN 3D
# ==============================================================================
# On a des points (moneyness, maturité, vol) éparpillés. Pour tracer une
# surface, on les interpole sur une grille régulière avec griddata.
# griddata ne remplit QUE l'intérieur de la zone couverte par les points
# (ailleurs : vide), donc on ne montre pas de valeurs inventées.
grille_m = np.linspace(df["moneyness"].min(), df["moneyness"].max(), 50)
grille_T = np.linspace(df["T"].min(), df["T"].max(), 50)
M, TT = np.meshgrid(grille_m, grille_T)
VOL = griddata((df["moneyness"], df["T"]), df["vol_impl"] * 100, (M, TT), method="linear")

fig = plt.figure(figsize=(11, 7))
ax = fig.add_subplot(projection="3d")
surface = ax.plot_surface(M, TT, VOL, cmap="viridis", alpha=0.8)
ax.scatter(df["moneyness"], df["T"], df["vol_impl"] * 100, color="red", s=8, label="Marché")
ax.set_xlabel("Moneyness K/F")
ax.set_ylabel("Maturité (années)")
ax.set_zlabel("Vol implicite (%)")
ax.set_title("Nappe de volatilité implicite du CAC 40")
fig.colorbar(surface, shrink=0.6, label="Vol (%)")
ax.view_init(elev=25, azim=-130)
plt.tight_layout()
plt.savefig(RESULTATS / "2_nappe_3d.png", dpi=120)


# ==============================================================================
# ÉTAPE 8 : VOLATILITÉ "À LA MONNAIE" (ATM) PAR MATURITÉ
# ==============================================================================
# Pour comparer avec l'historique, on résume chaque maturité par UNE vol :
# celle du strike égal au forward (K = F), obtenue par interpolation linéaire.
atm = []
for maturite, groupe in df.groupby("maturite"):
    groupe = groupe.sort_values("K")
    vol_atm = np.interp(forwards[maturite], groupe["K"], groupe["vol_impl"])
    atm.append({"maturite": maturite, "jours": (maturite - DATE_DU_JOUR).days, "vol_atm": vol_atm})
atm = pd.DataFrame(atm)


# ==============================================================================
# ÉTAPE 9 : VOLATILITÉ HISTORIQUE DU CAC 40
# ==============================================================================
# Vol historique = écart-type des rendements journaliers passés, annualisé :
#     rendement_t = ln(P_t / P_{t-1})
#     vol_hist    = écart-type(rendements) × racine(252)   (252 jours de bourse/an)
def charger_historique():
    if os.path.exists(DONNEES / "cac40_historique.csv"):
        h = pd.read_csv(DONNEES / "cac40_historique.csv")
        h["Date"] = pd.to_datetime(h["Date"], dayfirst=True)
        if h["Close"].dtype == object:  # Format français "8 138,75"
            h["Close"] = pd.to_numeric(h["Close"].str.replace(r"[\s \xa0]", "", regex=True)
                                       .str.replace(",", "."), errors="coerce")
        return h.set_index("Date").sort_index()["Close"].dropna()
    try:
        import yfinance as yf
        h = yf.download("^FCHI", end=DATE_DU_JOUR + pd.Timedelta(days=1), period="2y",
                        progress=False, auto_adjust=True)
        return h["Close"].squeeze().dropna()
    except ImportError:
        return None


prix_cac = charger_historique()

if prix_cac is None or len(prix_cac) < 260:
    print("\n[Historique indisponible] Installez yfinance (pip install yfinance) ou")
    print("placez un fichier donnees/cac40_historique.csv (colonnes Date, Close) dans le dossier.")
else:
    rendements = np.log(prix_cac / prix_cac.shift(1)).dropna()

    # Vol historique "glissante" sur 20, 60 et 250 jours de bourse
    vol_20j = rendements.rolling(20).std() * np.sqrt(252)
    vol_60j = rendements.rolling(60).std() * np.sqrt(252)
    vol_250j = rendements.rolling(250).std() * np.sqrt(252)

    # Pour chaque maturité : vol historique mesurée sur une durée équivalente
    # (ex. option à 3 mois  <->  vol réalisée sur les 3 derniers mois)
    atm["jours_bourse"] = (atm["jours"] * 252 / 365).round().astype(int)
    atm["vol_hist"] = [rendements.iloc[-n:].std() * np.sqrt(252) for n in atm["jours_bourse"]]
    atm["prime_de_vol"] = atm["vol_atm"] - atm["vol_hist"]

    print("\nComparaison vol implicite ATM / vol historique sur la même durée :")
    print(f"{'Échéance':<12}{'Jours':>7}{'Vol impl. ATM':>15}{'Vol hist.':>12}{'Écart':>9}")
    for ligne in atm.itertuples():
        print(f"{ligne.maturite:%d/%m/%Y}  {ligne.jours:>5}{ligne.vol_atm*100:>13.1f} %"
              f"{ligne.vol_hist*100:>10.1f} %{ligne.prime_de_vol*100:>+8.1f}")

    # --- GRAPHIQUE 3 : évolution de la vol historique + niveau implicite actuel
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5.5))
    ax1.plot(vol_20j * 100, label="Vol historique 20 jours", linewidth=1)
    ax1.plot(vol_60j * 100, label="Vol historique 60 jours", linewidth=1.5)
    ax1.plot(vol_250j * 100, label="Vol historique 1 an", linewidth=2)
    ax1.axhline(atm["vol_atm"].iloc[0] * 100, color="red", linestyle="--",
                label=f"Vol implicite ATM ({atm['maturite'].iloc[0]:%m/%Y})")
    ax1.set_title("Volatilité historique du CAC 40 (glissante)")
    ax1.set_ylabel("Volatilité annualisée (%)")
    ax1.legend()
    ax1.grid(alpha=0.3)

    # --- Structure par terme : implicite vs historique selon la maturité
    ax2.plot(atm["jours"], atm["vol_atm"] * 100, "o-", color="red", label="Vol implicite ATM")
    ax2.plot(atm["jours"], atm["vol_hist"] * 100, "s-", color="blue",
             label="Vol historique (même durée, dans le passé)")
    ax2.set_xlabel("Maturité (jours)")
    ax2.set_ylabel("Volatilité (%)")
    ax2.set_title("Implicite vs historique selon la maturité")
    ax2.legend()
    ax2.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(RESULTATS / "3_vol_historique_vs_implicite.png", dpi=120)
    print("Graphique enregistré : 3_vol_historique_vs_implicite.png")

print("\nGraphiques enregistrés dans resultats/ : 1_smiles.png, 2_nappe_3d.png")
plt.show()
