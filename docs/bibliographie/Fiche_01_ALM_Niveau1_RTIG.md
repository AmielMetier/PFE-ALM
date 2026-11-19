# Fiche de lecture 1 : Formation ALM Niveau 1 (RTIG)

Document lu : support de formation *Risque de Taux d'Intérêt Global - Principes et méthodes (niveau 1)* de Zakaria Kardou (81 slides, IFCAM).

## L'essentiel sur l'ALM et le RTIG

Une banque collecte surtout des ressources à court terme (dépôts à vue, livrets) et prête à moyen ou long terme (crédits immobiliers, crédits d'équipement). Ce décalage d'échéance crée un risque de transformation : si les taux bougent, les intérêts reçus et les intérêts versés n'évoluent pas au même rythme, ce qui peut faire varier la marge nette d'intérêts (MNI).

La gestion actif-passif (ALM) s'est développée après la crise des *Savings and Loans* aux États-Unis dans les années 1980. En France, la gestion du risque de taux global (RTIG) est encadrée par le règlement CRBF 97-02 et les règles de Bâle 2 (limites sur la perte maximale en valeur économique en cas de choc de taux). Les décisions de couverture sont prises en Comité Actif-Passif (ALCO).

Le cours découpe le RTIG en quatre composantes :
- le risque de *repricing* (risque directionnel classique), suivi avec le gap de taux fixe ;
- le risque de base, quand l'actif et le passif ne sont pas indexés sur le même taux (suivi via le gap d'index) ;
- le risque de fixing, lié au décalage des dates de révision sur les taux variables ;
- le risque optionnel, lié aux options accordées aux clients (caps, floors, remboursements anticipés), suivi par des matrices et des gaps en équivalent delta.

## Le gap de taux et ses limites

Pour construire un gap de taux, il faut d'abord modéliser l'écoulement des encours. Pour les crédits ou emprunts classiques, on utilise l'échéancier contractuel. Pour les produits sans échéance (comme les dépôts à vue), on applique des conventions d'écoulement qui séparent une part stable et une part volatile.

Un gap négatif correspond à un excédent d'emplois à taux fixe financé à taux variable (la banque perd si les taux montent). Un gap positif correspond à l'inverse (elle perd si les taux baissent). L'impact d'une translation parallèle des taux sur la MNI est directement lié à ce gap.

Le gap de taux a l'avantage d'être simple à calculer et lisible, mais il ne sait pas gérer les flux non linéaires des options. Par ailleurs, la banque ne cherche pas forcément à tout couvrir : elle gère son exposition sous contrainte de limites, en arbitrant entre stabilité de la marge et coût de couverture.

## Ce qu'on retient pour le PFE

Notre sujet porte précisément sur la quatrième composante du RTIG (le risque optionnel), là où le gap de taux classique ne suffit plus. L'objectif reste celui de l'ALM bancaire : protéger la MNI dans le temps, et non faire du trading de marché.
