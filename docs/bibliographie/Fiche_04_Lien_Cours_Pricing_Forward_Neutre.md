# Fiche de lecture 4 : Lien avec le cours de pricing (formule du delta forward-neutre)

Sources : cours de mathématiques financières / pricing (IMAFA), exemple d'attendu p. 9 de `Sujets_PFE_IMAFA_2026_2027.V0.3.pdf` et formation ALM Niveau 2 (p. 73-77).

## Passage de Black-Scholes à Black-76

Dans le modèle de Black-Scholes vu en cours pour un call européen sur action de prix $S_0$, de strike $K$ et de maturité $T$, le delta vaut $\Phi(d_1)$ avec :

$$d_1 = \frac{\ln\!\left(\dfrac{S_0 e^{rT}}{K}\right) + \dfrac{\sigma^2}{2}T}{\sigma\sqrt{T}}$$

Sur un taux d'intérêt, un caplet a un payoff $\max(S_T - K, 0)$ (un call sur le taux à l'échéance) et un floorlet a un payoff $\max(K - S_T, 0)$ (un put sur le taux). En passant sous la mesure forward-neutre (modèle de Black-76), le terme $S_0 e^{rT}$ est simplement remplacé par le taux forward $F$ :

$$d_1 = \frac{\ln(F/K) + \frac{\sigma^2}{2}T}{\sigma\sqrt{T}}, \qquad d_2 = d_1 - \sigma\sqrt{T}$$

## Pourquoi on ajoute un shift (`Shifted`)

En zone euro, les taux ont déjà été négatifs et beaucoup de floors clients ont un strike $K = 0\,\%$. Or $\ln(F/K)$ n'est pas défini si $F \le 0$ ou $K \le 0$.

Pour régler ce problème, on décale les taux et le strike d'une même constante $s = \text{Shifted} < 0$ (par exemple $-3\,\%$ ou $-5\,\%$) de sorte que $F - s > 0$ et $K - s > 0$. Le payoff ne change pas puisque $(S_T - s) - (K - s) = S_T - K$.

En reprenant exactement les notations de la page 9 du sujet, pour un mois $m < 168$ (donc $T = m / 12$ en années), un scénario de taux forward $F^{(**)}(m)$ et une volatilité historique lissée $\sigma_{\text{lisse}}(m)$ :

$$d_1(K, m) = \frac{\ln\!\left(\dfrac{F^{(**)}(m) - \text{Shifted}}{K - \text{Shifted}}\right) + \dfrac{\sigma_{\text{lisse}}(m)^2}{2}\cdot\dfrac{m}{12}}{\sigma_{\text{lisse}}(m)\sqrt{\dfrac{m}{12}}}$$

On en déduit :
- pour un caplet : $\Delta_{\text{cap}}(K, m) = \Phi(d_1(K, m))$ ;
- pour un floorlet : $\Delta_{\text{floor}}(K, m) = \Phi(-d_1(K, m)) = 1 - \Delta_{\text{cap}}(K, m)$.

## Vérifications simples avant de coder en VBA

Quelques propriétés qu'on pourra utiliser pour vérifier que notre code VBA ne fait pas d'erreur :
- $\Delta$ reste toujours compris entre $0\,\%$ et $100\,\%$ ;
- à maturité fixée, $\Delta_{\text{cap}}$ diminue quand le strike $K$ augmente (et l'inverse pour un floor) ;
- si $F \ll K$, $\Delta_{\text{cap}} \to 0\,\%$ ; si $F \gg K$, $\Delta_{\text{cap}} \to 100\,\%$ ; si $F = K$, $\Delta_{\text{cap}}$ est juste au-dessus de $50\,\%$ ;
- sous un choc `+50 pb`, $\Delta_{\text{cap}}$ monte et $\Delta_{\text{floor}}$ baisse, et l'écart est maximal autour du strike (effet gamma).

Côté Excel / VBA, la fonction de répartition normale centrée réduite existe nativement (`Application.WorksheetFunction.Norm_S_Dist(d1, True)`). Il faudra aussi faire attention à estimer la volatilité historique sur les taux décalés $(r_t - \text{Shifted})$ pour rester cohérent avec la formule, et vérifier avant chaque calcul que $F - \text{Shifted} > 0$, $K - \text{Shifted} > 0$ et $\sigma_{\text{lisse}} > 0$.
