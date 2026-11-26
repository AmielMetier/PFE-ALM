# Recensement des sources Open Data (courbes de taux)

Équipe : Amiel Metier, Nicolas Muratore, Tahitoa Senis  
Date : 19 novembre 2026  
Objectif : vérifier avant le 20/11 que les séries publiques nécessaires au calcul des taux forward (jusqu'à 14 ans / 168 mois), de la volatilité historique et du backtest sont accessibles gratuitement et exploitables dans Excel.

## 1. Ce dont on a besoin pour l'outil

Pour faire tourner la chaîne de calcul, il nous faut :
- une courbe de taux zéro-coupon en EUR couvrant au moins les maturités de 3 mois à 15 ans (pour interpoler facilement au pas mensuel de 1 à 168 mois et en déduire les taux forward $F(m)$) ;
- un historique long (au moins 10 à 15 ans, incluant la période de taux négatifs 2015-2022 et la remontée de 2022-2023) pour calculer la volatilité historique et tester la couverture en backtest ;
- des taux courts de référence (€STR / Euribor 3M) pour situer le bas de courbe et le taux variable des produits ;
- un format exportable simplement en CSV afin de pouvoir l'importer dans le classeur Excel / VBA sans dépendance externe.

## 2. Source principale retenue : ECB Data Portal (BCE)

Portail : https://data.ecb.europa.eu/

La BCE publie gratuitement le jeu de données **YC (Euro area yield curves)**, estimé quotidiennement selon le modèle de Svensson sur les obligations souveraines AAA de la zone euro (historique disponible depuis septembre 2004, soit plus de 20 ans).

Séries identifiées :
- Courbe des taux spot zéro-coupon (AAA) : clé de base `YC.B.U2.EUR.4F.G_N_A.SV_C_YM.SR_<maturité>` (par exemple `SR_3M`, `SR_6M`, `SR_1Y`, `SR_2Y`, ..., `SR_15Y`, jusqu'à `SR_30Y`).
- Courbe tous émetteurs zone euro (en alternative si besoin) : même structure avec `G_N_C` à la place de `G_N_A`.
- Paramètres de la courbe de Svensson (`BETA0` à `BETA3`, `TAU1`, `TAU2`) également disponibles dans le même jeu de données, ce qui permet soit d'interpoler entre les points publiés, soit de recalculer directement la courbe sur chaque maturité mensuelle $m \in \{1, \dots, 168\}$.
- Taux courts de référence sur le même portail : €STR (quotidien depuis octobre 2019) et Euribor 3 mois (historique mensuel dans le jeu de données `FM`).

Avantages pratiques pour Excel / VBA : téléchargement direct en CSV (ou via l'URL de l'API REST publique de la BCE), pas de compte requis, couverture complète jusqu'à 30 ans.

## 3. Source complémentaire : Banque de France (Webstat)

Portail : https://webstat.banque-france.fr/

Webstat permet de recouper et compléter les données BCE avec des séries françaises et zone euro :
- taux €STR (historique quotidien) ;
- taux obligataires français (OAT / TEC 10) pour contrôle de cohérence sur le long terme ;
- séries de taux de crédits et de dépôts des ménages en France, utiles pour choisir des strikes réalistes dans notre portefeuille bancaire fictif.

Point de vigilance relevé : depuis 2024, la Banque de France ne republie plus directement les séries quotidiennes d'Euribor sur ses supports et renvoie vers la BCE. On s'appuiera donc en priorité sur l'ECB Data Portal pour les courbes et taux de marché, et sur Webstat en complément.
