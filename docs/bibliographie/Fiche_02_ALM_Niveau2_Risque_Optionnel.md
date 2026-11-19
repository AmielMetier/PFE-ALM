# Fiche de lecture 2 : Formation ALM Niveau 2 (Gestion du RTIG et risque optionnel)

Document lu : support de formation *Comment optimiser la gestion du RTIG (niveau 2)* de Zakaria Kardou (79 slides). On s'est surtout concentré sur les parties sur le gap synthétique (p. 49-59) et sur le risque optionnel (p. 73-77).

## Indicateurs ALM et gap synthétique

Le support rappelle la distinction entre les principaux indicateurs :
- la MNI (marge nette d'intérêts), qui mesure le revenu courant entre taux prêteur et taux de refinancement ;
- la VAN (valeur actuelle nette), qui actualise tous les flux futurs de capital et d'intérêts ;
- la duration, qui donne la sensibilité de cette valeur aux variations de taux.

Le gap synthétique regroupe le gap de taux fixe (opérations fermes), le gap équivalent delta (options) et le gap inflation (livrets). Le cours insiste sur le fait qu'il ne faut pas se contenter du seul gap synthétique quand la banque porte beaucoup d'options : il faut un suivi dédié pour bien voir d'où vient le risque.

On retrouve aussi la distinction entre marge adossée (figée par une couverture) et marge exposée, ainsi que le rôle des taux forward, déduits de la courbe des taux, qui servent de référence pour les maturités futures.

## Suivi du risque optionnel : matrices et équivalent delta (p. 73-76)

C'est la partie la plus proche de notre sujet. Comme le payoff d'une option n'est pas linéaire, sa sensibilité dépend du niveau des taux. Le Comité de Bâle (*Principles for the Management and Supervision of Interest Rate Risk*, Annexe 4, point j) demande d'intégrer les options dans les impasses de taux sur la base de leur équivalent delta :

$$\text{Équivalent delta} = \text{Nominal} \times \Delta$$

Dans la pratique présentée en cours (exemple sous Cristaux 2), le suivi repose sur deux éléments :
- une matrice qui donne les notionnels par tranche de strike (par exemple `< 3 %`, `3-4 %`, `4-5 %`, `> 5 %`) et par maturité, en séparant les positions vendeuses (crédits clients) et acheteuses (couverture) ;
- le gap en équivalent delta associé, qu'on peut additionner aux positions fermes à taux fixe.

Le cours précise aussi une limite importante : le delta est une approximation locale (valable pour un petit mouvement de 1 pb). Dès qu'on fait des stress tests importants, la convexité des options (effet gamma) joue et le delta se déplace. Il faut donc recalculer les deltas sous chaque scénario de taux.

## Couvrir en swaps (delta) ou acheter des caps/floors ? (p. 77)

La slide 77 résume bien le choix de couverture selon deux critères : la distance entre le taux forward et le strike, et le niveau de volatilité.

- Si le forward est loin du strike et que la volatilité est faible, les effets gamma et vega sont limités : couvrir en équivalent delta avec des swaps fonctionne bien et évite de payer une prime d'option.
- Si le forward est proche du strike (à la monnaie) et/ou que la volatilité est élevée, le delta varie vite dès que les taux bougent (gamma) ou que la volatilité change (vega). Dans ce cas, acheter directement des caps ou des floors est plus sûr.

## Ce qu'on retient pour le PFE

On va reprendre cette logique dans notre outil Excel : afficher les notionnels par strike et maturité, calculer le gap équivalent delta sous plusieurs scénarios de courbe, et utiliser les 4 cas de la slide 77 (distance au strike × volatilité) pour justifier nos propositions de couverture.
