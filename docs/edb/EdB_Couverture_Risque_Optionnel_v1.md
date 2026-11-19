# Expression de besoins (v1)

Projet de Fin d'Études (MAM 5 IMAFA, Polytech Nice Sophia, 2026-2027)  
Sujet : Couverture du risque optionnel de taux (ALM)  
Équipe : Amiel Metier, Nicolas Muratore, Tahitoa Senis  
Encadrant : Zakaria Kardou (KZ Consulting)  
Date : 19 novembre 2026

## 1. Contexte et problématique

En gestion actif-passif (ALM), la banque cherche à stabiliser sa marge nette d'intérêts (MNI) face aux variations de taux. Le gap de taux fixe classique permet de suivre les opérations fermes, mais il ne voit pas les options de taux intégrées dans certains produits vendus aux clients :
- à l'actif, les crédits à taux variable capés (la banque vend un cap au client : si le taux dépasse le strike $K$, les intérêts reçus sont plafonnés) ;
- au passif, les dépôts rémunérés avec plancher à 0 % (la banque vend un floor : si les taux passent en négatif, le coût de la ressource reste bloqué).

Dans les deux cas, le gain n'est pas linéaire et la MNI baisse quand le client exerce son option. Le Comité de Bâle (Annexe 4, point j des principes sur le RTIG) demande d'intégrer ces options dans les gaps de taux via leur équivalent delta.

Contrairement à une approche de marché (Mark-to-Market), le résultat du banking book est suivi en couru. On retient donc un modèle forward-neutre basé sur la volatilité historique plutôt que la volatilité implicite : l'objectif est de protéger la marge jusqu'à l'échéance avec des couvertures stables et sans paiement initial de prime.

## 2. Objectifs

L'objectif du projet est de livrer un outil Excel / VBA simple, documenté et utilisable en autonomie par un tiers, capable de :
1. calculer la matrice des probabilités d'exercice $\Delta(K, m)$ pour différents strikes et maturités mensuelles jusqu'à 14 ans (168 mois), sur le scénario central et plusieurs scénarios de stress ;
2. calculer le gap optionnel en équivalent delta à partir d'un portefeuille bancaire fictif représentatif ;
3. proposer une stratégie de couverture adaptée (swaps en équivalent delta et/ou achat de caps et floors selon la proximité du strike et la volatilité) ;
4. tester cette approche sur un historique de taux issu de données publiques (open data).

## 3. Périmètre et points à confirmer

Ce qui est inclus dans le projet :
- les caps et floors de taux, sur des échéances mensuelles de 1 à 168 mois (14 ans) ;
- un portefeuille fictif représentatif d'un bilan bancaire moyen (décision actée lors du kick-off du 5 novembre) ;
- le scénario central de taux forward (`FWD`) et 6 scénarios de stress : `FWD + 50 pb`, `FWD - 50 pb`, hausse non homogène, baisse non homogène, pentification et aplatissement ;
- une approche comptable en couru uniquement.

Ce qui est hors périmètre :
- la valorisation en valeur de marché (MtM) et le trading book ;
- les modèles complets de risque de liquidité, de risque de crédit ou de remboursements anticipés ;
- la calibration de surfaces de volatilité implicite (type SABR).

Points restant à valider avec l'encadrant lors du point de semaine 3 :
- la devise de l'étude (nous proposons l'EUR, cohérent avec les données BCE et Banque de France) ;
- la confirmation que les macros VBA (`.xlsm`) tournent bien sur le poste de l'encadrant (à tester dès la maquette) ;
- la composition précise du portefeuille fictif à retenir (tranches de strikes et montants d'encours) ;
- la valeur du paramètre de décalage `Shifted` pour traiter les taux nuls ou négatifs (par exemple `-3 %` ou `-5 %`).

## 4. Méthode de calcul retenue

La chaîne de calcul comporte cinq étapes :

1. **Courbes de taux et taux forward $F(m)$** : on récupère des courbes de taux publiques (BCE / Banque de France) jusqu'à au moins 15 ans, on interpole au pas mensuel de 1 à 168 mois, puis on calcule les taux forward $F(m)$ et les 6 scénarios de déformation $F^{(**)}(m)$.
2. **Volatilité historique lissée $\sigma_{\text{lisse}}(m)$** : on estime la volatilité historique sur les données passées (de manière cohérente avec le shift retenu), puis on la lisse sur les 168 mois.
3. **Matrice $\Delta(K, m)$** : pour un maillage de strikes paramétrable (par exemple pas de 25 pb jusqu'à 8 %) et chaque mois $m < 168$, on applique la formule du modèle forward-neutre décalé :
   $$d_1(K, m) = \frac{\ln\!\left(\dfrac{F^{(**)}(m) - \text{Shifted}}{K - \text{Shifted}}\right) + \dfrac{\sigma_{\text{lisse}}(m)^2}{2}\cdot\dfrac{m}{12}}{\sigma_{\text{lisse}}(m)\sqrt{\dfrac{m}{12}}}$$
   avec $\Delta_{\text{cap}}(K, m) = \Phi(d_1(K, m))$ pour un caplet et $\Delta_{\text{floor}}(K, m) = 1 - \Delta_{\text{cap}}(K, m)$ pour un floorlet.
4. **Gap optionnel** : on croise les encours du portefeuille fictif (par strike, maturité et sens acheteur/vendeur) avec la matrice $\Delta$ pour obtenir le gap optionnel en équivalent delta :
   $$\text{Gap}_{\text{opt}}(m) = \sum_{K} N_{\text{signé}}(K, m) \times \Delta(K, m)$$
   En recalculant ce gap sur les différents scénarios de taux, on observe sa déformation (effet gamma).
5. **Couverture et backtest** : on arbitre entre couverture en swaps (quand le forward est loin du strike et la volatilité faible) et achat de caps/floors (quand on est proche du strike et/ou en forte volatilité, où gamma et vega pèsent), puis on teste le comportement de la MNI sur un historique réel.

## 5. Données et outil Excel / VBA

Les données proviendront uniquement de sources open data (BCE et Banque de France / Webstat), complétées par le portefeuille fictif. Les séries précises sont recensées dans une fiche dédiée.

L'outil sera développé en **Excel / VBA (`.xlsm`)** pour fonctionner directement chez n'importe quel utilisateur sans rien installer. On prévoit de séparer clairement les onglets :
- `Parametres` : date d'arrêté, pas de strike, strike max, `Shifted`, fenêtre de volatilité, chocs des scénarios et boutons de lancement ;
- `Donnees_Taux` : séries historiques importées ;
- `Forward_Scenarios` : courbe mensuelle, taux forward et scénarios de stress avec graphiques ;
- `Volatilite` : calcul de la volatilité historique et lissage ;
- `Matrice_Delta` : matrice $\Delta(K, m)$ et courbes par strike ;
- `Portefeuille_Gap` : encours fictifs par tranche de strike et calcul du gap optionnel ;
- `Couverture_Backtest` : proposition de couverture et suivi de la MNI sur historique.

## 6. Livrables et organisation

Les livrables prévus sont :
- Expression de besoins, fiches de lecture ALM, recensement des données open data et Gantt v1 (fin novembre) ;
- Maquette Excel / VBA (11 décembre) ;
- Mi-soutenance (semaine du 11 janvier) ;
- Outil Excel / VBA finalisé et testé (5 février) ;
- Note d'analyse des résultats, guide utilisateur et mémoire de PFE (mi-février).

Le suivi se fait par un point hebdomadaire avec support PowerPoint et compte rendu Word diffusé sous 48 h. Les fichiers de travail sont centralisés sur le dépôt GitHub `PFE-ALM`.
