# PFE ALM — Couverture du risque optionnel de taux

Projet de Fin d'Études (MAM 5 — IMAFA, Polytech Nice Sophia, 2026–2027) portant sur la mesure et la couverture du **risque optionnel de taux** dans le bilan bancaire (Gestion Actif-Passif / ALM).

## Équipe projet

| Rôle | Nom |
| :--- | :--- |
| **Étudiant IMAFA** | Amiel Metier |
| **Étudiant IMAFA** | Nicolas Muratore |
| **Étudiant IMAFA** | Tahitoa Senis |
| **Encadrant** | Zakaria Kardou (KZ Consulting) |

## Problématique & objectifs

Les produits bancaires intègrent des options de taux vendues aux clients (crédits à taux variable capés, dépôts rémunérés avec floor à 0 %, etc.) dont le comportement non linéaire échappe au gap de taux classique. L'objectif est de protéger la **marge nette d'intérêts (MNI)** en vision **couru** (hors valeur de marché / trading book) via un modèle **forward-neutre** basé sur la volatilité historique.

**Chaîne de calcul cible :**
1. Collecte de **courbes de taux** en open data (BCE, Banque de France).
2. Construction des **taux forward $F$** et des **scénarios de stress** (`±50 pb`, pentification, aplatissement, hausses/baisses non homogènes).
3. Calcul de la **matrice de probabilités d'exercice $\Delta(K, T)$** (modèle forward-neutre, volatilité historique $\sigma$, maturités jusqu'à 14 ans / 168 mois).
4. Agrégation en **gap optionnel** ($\text{encours} \times \Delta$) sur un portefeuille bancaire fictif représentatif.
5. Proposition d'une **stratégie de couverture** (swaps, caps, floors) et **backtest historique**.

**Outil cible :** classeur **Excel / VBA** autonome, documenté et utilisable par tout tiers sans installation préalable.

## Arborescence du dépôt

```text
PFE-ALM/
├── docs/
│   ├── edb/               # Expression de besoins (EdB) et versions du Gantt
│   ├── bibliographie/     # Fiches de lecture ALM & lien cours de pricing
│   └── notes/             # Note d'analyse, guide utilisateur, mémoire de PFE
├── data/
│   ├── raw/               # Séries open data brutes (BCE, Banque de France)
│   └── processed/         # Données nettoyées, courbes forward, volatilités
├── src/                   # Outil de calcul Excel / VBA (utilisable en autonomie par un tiers)
├── reunions/              # Supports de suivi hebdomadaire et comptes rendus (CR)
├── .gitignore
└── README.md
```

## Jalons clés

| Période | Jalon / Livrable |
| :--- | :--- |
| **05/11/2026** | Kick-off & cadrage initial |
| **20/11/2026** | Expression de besoins (EdB), fiches de lecture ALM, identification des sources open data |
| **11/12/2026** | Maquette de l'outil |
| **Sem. 11/01/2027** | Soutenance intermédiaire (mi-soutenance) |
| **05/02/2027** | Outil figé & tests finalisés |
| **≈ 15/02/2027** | Rendu final (outil Excel/VBA documenté et utilisable en autonomie, note d'analyse, guide utilisateur, mémoire de PFE) |

## Gouvernance & conventions

- **Point hebdomadaire** : visio de 30 min à 1 h avec support PowerPoint (Gantt à jour, fait, reste à faire, points durs).
- **Compte rendu (CR)** : diffusé sous 48 h après chaque réunion ; toute décision est actée par écrit dans le CR.
- **Versionnage des livrables** : une version de référence et des versions datées/numérotées (`v0`, `v1`, etc.).
