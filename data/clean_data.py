"""
Nettoyage des données brutes (BCE + Banque de France Webstat)
pour produire des CSV légers et prêts à importer dans Excel / VBA.

Exécution depuis la racine du dépôt PFE-ALM :
    python data/clean_data.py
"""

import csv
import os
from collections import defaultdict

RAW_BCE = os.path.join("data", "raw", "data.csv")
RAW_EURIBOR = os.path.join("data", "raw", "Webstat_Export_fr_ECOFI.INR.FR.FID_PA._Z.D.csv")
OUT_DIR = os.path.join("data", "processed")

SVENSSON_TYPES = ["BETA0", "BETA1", "BETA2", "BETA3", "TAU1", "TAU2"]
SPOT_MATURITIES = [
    "SR_3M", "SR_6M", "SR_9M",
    "SR_1Y", "SR_2Y", "SR_3Y", "SR_4Y", "SR_5Y",
    "SR_6Y", "SR_7Y", "SR_8Y", "SR_9Y", "SR_10Y",
    "SR_12Y", "SR_15Y", "SR_20Y"
]
WANTED_TYPES = set(SVENSSON_TYPES) | set(SPOT_MATURITIES)


def clean_bce():
    print(f"[1/2] Lecture en streaming de {RAW_BCE} ...")
    # Stockage par date -> {data_type: valeur}
    spot_by_date = defaultdict(dict)
    svensson_by_date = defaultdict(dict)
    seen_types = set()
    n_lines = 0
    n_kept = 0

    with open(RAW_BCE, "r", encoding="utf-8-sig", errors="replace", newline="") as f:
        reader = csv.reader(f)
        header = next(reader)
        idx_inst = header.index("INSTRUMENT_FM")
        idx_type = header.index("DATA_TYPE_FM")
        idx_date = header.index("TIME_PERIOD")
        idx_val = header.index("OBS_VALUE")

        for row in reader:
            n_lines += 1
            if len(row) <= idx_val:
                continue
            if row[idx_inst] != "G_N_A":  # Uniquement courbe AAA
                continue
            dtype = row[idx_type]
            seen_types.add(dtype)
            if dtype not in WANTED_TYPES:
                continue
            val = row[idx_val].strip()
            if not val:
                continue
            date = row[idx_date].strip()
            if dtype in SPOT_MATURITIES:
                spot_by_date[date][dtype] = float(val)
            else:
                svensson_by_date[date][dtype] = float(val)
            n_kept += 1

    print(f"    Lignes parcourues : {n_lines:,} | Valeurs utiles retenues : {n_kept:,}")
    spot_present = [m for m in SPOT_MATURITIES if m in seen_types]
    print(f"    Maturités spot trouvées ({len(spot_present)}) : {', '.join(spot_present)}")

    # Sélection du dernier jour ouvré de chaque mois (fin de mois)
    def pick_month_ends(data_dict):
        by_ym = {}
        for d in sorted(data_dict.keys()):
            ym = d[:7]  # YYYY-MM
            by_ym[ym] = d  # comme on parcourt par ordre croissant, on garde la dernière date du mois
        return [by_ym[ym] for ym in sorted(by_ym.keys())]

    os.makedirs(OUT_DIR, exist_ok=True)

    # 1. Export spot mensuel (en % tels que publiés par la BCE, ex: 2.50 = 2.50 %)
    spot_dates = pick_month_ends(spot_by_date)
    out_spot = os.path.join(OUT_DIR, "bce_courbe_aaa_spot_mensuel.csv")
    with open(out_spot, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(["Date"] + spot_present)
        for d in spot_dates:
            row = [d] + [
                f"{spot_by_date[d][m]:.6f}" if m in spot_by_date[d] else ""
                for m in spot_present
            ]
            writer.writerow(row)
    print(f"    -> Écrit : {out_spot} ({len(spot_dates)} mois, de {spot_dates[0]} à {spot_dates[-1]})")

    # 2. Export paramètres Svensson mensuel
    sv_dates = pick_month_ends(svensson_by_date)
    out_sv = os.path.join(OUT_DIR, "bce_svensson_params_mensuel.csv")
    with open(out_sv, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(["Date"] + SVENSSON_TYPES)
        for d in sv_dates:
            row = [d] + [
                f"{svensson_by_date[d][k]:.8f}" if k in svensson_by_date[d] else ""
                for k in SVENSSON_TYPES
            ]
            writer.writerow(row)
    print(f"    -> Écrit : {out_sv} ({len(sv_dates)} mois, de {sv_dates[0]} à {sv_dates[-1]})")

    # 3. Export courbe au dernier arrêté disponible (prêt pour la maquette v0)
    last_date = sorted(spot_by_date.keys())[-1]
    out_last = os.path.join(OUT_DIR, f"bce_courbe_aaa_arrete_{last_date}.csv")
    mat_months = {
        "SR_3M": 3, "SR_6M": 6, "SR_9M": 9,
        "SR_1Y": 12, "SR_2Y": 24, "SR_3Y": 36, "SR_4Y": 48, "SR_5Y": 60,
        "SR_6Y": 72, "SR_7Y": 84, "SR_8Y": 96, "SR_9Y": 108, "SR_10Y": 120,
        "SR_12Y": 144, "SR_15Y": 180, "SR_20Y": 240
    }
    with open(out_last, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(["Maturite", "Mois", "Taux_Spot_Pct"])
        for m in spot_present:
            if m in spot_by_date[last_date]:
                writer.writerow([m, mat_months[m], f"{spot_by_date[last_date][m]:.6f}"])
    print(f"    -> Écrit : {out_last} (arrêté du {last_date})")
    print("    Aperçu dernière courbe :", {m: round(spot_by_date[last_date][m], 3) for m in spot_present if m in spot_by_date[last_date]})


def clean_euribor():
    print(f"\n[2/2] Nettoyage de {RAW_EURIBOR} ...")
    rows = []
    with open(RAW_EURIBOR, "r", encoding="utf-8-sig", errors="replace", newline="") as f:
        reader = csv.DictReader(f, delimiter=";")
        for r in reader:
            val = (r.get("obs_value") or "").strip()
            if not val:
                continue  # ignore week-ends et jours fériés
            date = r["time_period"].strip()
            rate = float(val.replace(",", "."))
            rows.append((date, rate))

    rows.sort(key=lambda x: x[0])

    # Quotidien propre
    out_daily = os.path.join(OUT_DIR, "euribor_3m_quotidien.csv")
    with open(out_daily, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(["Date", "Euribor_3M_Pct"])
        for d, r in rows:
            writer.writerow([d, f"{r:.4f}"])

    # Fin de mois (aligné sur la fréquence mensuelle BCE)
    by_ym = {}
    for d, r in rows:
        by_ym[d[:7]] = (d, r)
    out_monthly = os.path.join(OUT_DIR, "euribor_3m_mensuel.csv")
    with open(out_monthly, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(["Date", "Euribor_3M_Pct"])
        for ym in sorted(by_ym.keys()):
            d, r = by_ym[ym]
            writer.writerow([d, f"{r:.4f}"])

    print(f"    -> Écrit : {out_daily} ({len(rows)} jours ouvrés, de {rows[0][0]} à {rows[-1][0]})")
    print(f"    -> Écrit : {out_monthly} ({len(by_ym)} mois)")


if __name__ == "__main__":
    clean_bce()
    clean_euribor()
    print("\nTerminé ! Tous les fichiers propres sont dans data/processed/.")
