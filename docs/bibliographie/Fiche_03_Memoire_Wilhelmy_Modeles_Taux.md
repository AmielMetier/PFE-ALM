# Fiche de lecture 3 : Mémoire de Florent Wilhelmy (Modèles de taux en ALM)

Document lu : *Analyse des modèles de taux d'intérêt pour la gestion actif-passif bancaire*, mémoire d'actuariat ISFA de Florent Wilhelmy (stage ALM à la Caisse des Dépôts, 161 pages). Lecture ciblée sur la construction des courbes (Partie I), la valorisation des swaps/caps/floors (Partie II, chap. 4) et la comparaison des modèles (Parties III et IV).

## Passage des courbes de marché aux taux forward

La première partie rappelle comment passer des taux observés aux taux utilisables dans un modèle :
1. On part des taux de marché (taux monétaires courts type IBOR/Euribor et taux de swaps sur le long terme).
2. On construit la courbe des taux zéro-coupon $Z(0, T)$ (et les facteurs d'actualisation $B(0, T)$) par bootstrapping, puis on interpole pour obtenir un pas régulier (splines ou méthodes paramétriques comme Nelson-Siegel).
3. On en déduit les taux forward par absence d'arbitrage :
   $$F(0; T_1, T_2) = \frac{1}{T_2 - T_1}\left(\frac{B(0, T_1)}{B(0, T_2)} - 1\right)$$

Cette étape correspond directement au début de notre chaîne de calcul : obtenir une courbe mensuelle de taux forward jusqu'à 168 mois (14 ans) à partir des données BCE / Banque de France.

## Swaps, caps et floors

Dans la partie II (chap. 4), le mémoire détaille les instruments de couverture classiques :
- Le swap taux fixe / taux variable, qui sert de brique de base pour couvrir un gap directionnel ou un équivalent delta.
- Le cap (somme de caplets, c'est-à-dire d'options d'achat sur taux forward) et le floor (somme de floorlets, options de vente sur taux forward).

Leur formule de référence sur le marché est le modèle de Black-76, placé sous la mesure forward-neutre, où chaque taux forward suit une loi log-normale.

## Comparaison des familles de modèles vues dans le mémoire

Le mémoire compare trois approches différentes pour l'ALM :
- **Approche historique (ACP sur les taux zéro-coupon)** : permet de dégager les grands mouvements de courbe (niveau, pente, courbure) à partir des données passées. Utile pour construire des scénarios réalistes, moins faite pour du pricing sans arbitrage.
- **Modèle de taux court (Hull & White à 1 facteur)** : calibré sur la courbe initiale et implémenté par arbres recombinants. Il gère naturellement les taux négatifs, mais comme il n'a qu'un facteur, toutes les maturités bougent de manière parfaitement corrélée.
- **Modèle de marché (BGM / LIBOR Market Model)** : travaille directement en univers forward-neutre sur les taux forward, en cohérence avec Black-76. C'est plus réaliste, mais ça demande des simulations Monte-Carlo et une calibration lourde.

## Lien avec notre projet

Pour notre outil Excel/VBA, un modèle Monte-Carlo type LMM ou un arbre Hull-White serait trop lourd et peu lisible pour un utilisateur externe. Le choix fait dans le sujet du PFE est plus direct : garder la formule fermée du modèle forward-neutre (Black-76, avec un décalage pour les taux négatifs) pour calculer la matrice $\Delta(K, m)$, tout en utilisant une volatilité historique et des scénarios de déformation de courbe. C'est rapide, transparent et facile à tester dans Excel.
