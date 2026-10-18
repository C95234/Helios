# Rapport du banc « épidémies » : urgences et SOS Médecins, 37 départements, décembre 2022 à décembre 2024

**Verdict : ÉCHEC** selon la règle écrite à l'avance (pré-enregistrement `preenregistrement-v1`) : ni C1′ ni le placebo C3 ne sont satisfaits.
Statut des résultats : **observé sur données** (réel, une seule exécution pré-enregistrée), analyses complémentaires **exploratoires**, étiquetées comme telles.
Exécuté le 18 octobre 2026. Les critères n'ont pas été retouchés après avoir vu les résultats.

## 1. Ce qui a été fait, dans quel ordre

| Étape | Référence |
|---|---|
| Règle de démarrage de vague, écrite puis commitée avant application | `85d84ca` |
| Pré-enregistrement validé par Clément (18 oct. 2026) | étiquette `preenregistrement-v1` (`728f3b4`) |
| Code d'évaluation, testé sur données simulées, commité **avant** toute exécution réelle | étiquette `evaluation-v1-code` (`f8ad1b1`) |
| Exécution unique sur données réelles (graine 20261018), puis deux autres graines (1 et 2) pour mesurer le bruit de Monte-Carlo | `resultats_epidemies*.json` |
| Diagnostics exploratoires | `resultats_exploratoires.json` |

Commandes : `python -m scripts.vulnerabilite_evaluer` puis `python -m scripts.vulnerabilite_exploratoire` (depuis `backend/`). Les trois graines donnent le même verdict
et la même valeur ponctuelle de Δ ; seules les bornes d'intervalle bougent, de moins de 0,02.

## 2. Critère C1′ : le R croisé suit-il mieux la croissance des eaux usées que les canaux seuls ?

Corrélation de rang (Spearman) entre R̂ et la croissance de l'indicateur national d'eaux usées, sur 94 fenêtres glissantes de 12 semaines ; intervalles à 90 % par blocs.

| Grandeur | Valeur | IC à 90 % |
|---|---|---|
| ρ du R croisé | 0,259 | [-0,105 ; 0,561] |
| ρ du R des urgences seules | 0,341 | |
| ρ du R de SOS Médecins seul | 0,423 | |
| Δ = ρ croisé − meilleur canal seul | -0,164 | [-0,389 ; 0,100] |
| Fenêtres | 94 | |
| Réussi (bornes basses de Δ et de ρ croisé > 0) | non | |

Lecture : le R croisé est **moins** corrélé à la croissance des eaux usées que chacun des canaux pris seul (Δ < 0), et son intervalle à 90 % contient zéro. **C1′ n'est pas réussi.**

## 3. Critère C3 : placebo « canaux mélangés »

| Grandeur | Valeur |
|---|---|
| Permutations | 200 |
| Médiane des Δ placebo | -0,139 |
| 95ᵉ centile des Δ placebo | -0,067 |
| Δ observé | -0,164 |
| Propre (médiane ≤ 0 et 95ᵉ centile < Δ observé) | non |

En mélangeant au hasard les départements du canal SOS Médecins, la différence Δ ne change presque pas (médiane des Δ placebo −0,139 contre −0,164 observé) : l'appariement réel des deux canaux
par département n'apporte rien de mesurable par rapport à un appariement au hasard. **C3 n'est pas propre.**

## 4. Critère C2′ (descriptif, sans seuil de réussite)

Deux démarrages exploitables (31 juillet 2023, 13 mai 2024) et deux groupes de fenêtres témoins : aucune inférence. Tendance de Kendall (τ) de chaque indicateur sur les 16 semaines avant le démarrage,
et part des fenêtres témoins qui ont une tendance plus basse :

| Indicateur | τ avant le 2023-07-31 | τ avant le 2024-05-13 | part des témoins plus bas (2023-07-31) | part des témoins plus bas (2024-05-13) |
|---|---|---|---|---|
| R croisé | 0,06 | 0,33 | 0,80 | 1,00 |
| R urgences | -0,72 | -0,89 | 0,00 | 0,00 |
| R SOS | 0,11 | -0,61 | 1,00 | 0,20 |
| AC1 (moyenne par département) | -0,67 | -0,94 | 0,00 | 0,00 |
| Variance (moyenne par département) | -1,00 | -0,83 | 0,00 | 0,20 |

Repères (placebo « dates fictives », 2 000 tirages de 2 fins de fenêtres témoins) : médiane / 95ᵉ centile de la moyenne des τ : R croisé -0,38 / 0,03 ; R urgences -0,22 / 0,19 ; R SOS -0,33 / -0,06 ; AC1 0,19 / 0,56 ; variance -0,47 / -0,08.

À lire avec prudence : l'autocorrélation et la variance baissent avant chacune des deux vagues, ce qui est le sens contraire d'un signal d'alerte ; ces deux fenêtres commencent
dans un creux d'activité, donc cette baisse peut simplement refléter la sortie d'un creux. Le R croisé monte légèrement dans les deux cas (τ = 0,06 et 0,33) et se situe au-dessus des témoins, mais avec deux événements et deux témoins ce n'est
pas une preuve de quoi que ce soit.

## 5. Analyses de sensibilité pré-enregistrées

| Variante | Fenêtres | ρ croisé | ρ urgences | ρ SOS | Δ | IC à 90 % de Δ | C1′ réussi |
|---|---|---|---|---|---|---|---|
| **Principale** | 94 | 0,259 | 0,341 | 0,423 | -0,164 | [-0,389 ; 0,100] | non |
| Effets temporels complets (un par semaine) | 94 | 0,132 | 0,413 | 0,470 | -0,338 | [-0,527 ; -0,125] | non |
| Contrôles de calendrier (férié, vacances) | 94 | 0,186 | 0,362 | 0,315 | -0,177 | [-0,423 ; 0,031] | non |
| SOS Médecins décalé de 4 jours | 94 | 0,178 | 0,341 | 0,434 | -0,256 | [-0,526 ; -0,010] | non |
| Pas quotidien (jour de semaine + calendrier) | 94 | -0,131 | 0,088 | 0,277 | -0,407 | [-0,956 ; 0,055] | non |
| 45 départements (couverture partielle incluse) | 94 | 0,264 | 0,341 | 0,443 | -0,179 | [-0,416 ; 0,061] | non |
| Fenêtres de 8 semaines | 98 | 0,296 | 0,289 | 0,334 | -0,037 | [-0,270 ; 0,147] | non |
| Fenêtres de 16 semaines | 90 | 0,099 | 0,237 | 0,318 | -0,219 | [-0,449 ; 0,003] | non |
| Stations d'eaux usées (depuis le 19 févr. 2024) | 34 | 0,566 | 0,408 | 0,501 | 0,064 | [-0,686 ; 0,062] | non |

Aucune sensibilité ne réussit C1′. Deux lectures sont possibles pour les deux plus proches de l'égalité : avec des fenêtres de 8 semaines, le R croisé est au niveau des canaux seuls (Δ = −0,037) ; avec les indicateurs des stations
d'eaux usées (période restreinte, 34 fenêtres), il passe devant (Δ = +0,064) mais l'intervalle est très large et contient zéro. Les effets temporels complets aggravent l'écart (Δ = −0,338, intervalle entièrement négatif) :
quand la dynamique nationale commune est retirée, le R croisé est nettement moins bon. Selon la règle d'interprétation fixée à l'avance, les deux analyses (principale et effets temporels) ne divergent pas sur la conclusion : l'échec est déclaré **robuste**.

La note sur le calendrier : le brouillon de pré-enregistrement place les contrôles de calendrier en sensibilité (§6, point 4), alors que le texte de Clément les prévoyait aussi dans l'analyse principale. Les deux versions sont rapportées ci-dessus
(principale : Δ = −0,164 ; avec contrôles de calendrier : Δ = −0,177). Elles concordent.

## 6. Diagnostics (exploratoire : non pré-enregistré)

- **Taux de détection** : θ̂ regroupé = -7,5 pour les urgences et -43,2 pour SOS Médecins, **hors de ]0 ; 1[** (drapeau `theta_hors_intervalle`). L'estimateur intra-unité
  (moments calculés dans chaque département, puis sommés ; tolère un taux propre à chaque département) est lui aussi hors de ]0 ; 1[ : -1,0 (urgences) et -11,6 (SOS Médecins), et ce dans
  chaque moitié et chaque tiers de la période (voir `resultats_exploratoires.json`). La dispersion estimée (φ̂ = -0,27, valeur impossible) et les valeurs de c et de Φ qui en dépendent ne sont pas
  interprétables ; le R̂ regroupé (1,04) lève en outre le drapeau `pas_d_etat_calme`.
- **Ce que ces valeurs signifient (simulations sans donnée réelle, voir §6 bis)** : un θ̂ regroupé très négatif apparaît quand le taux de détection diffère d'un département à l'autre ; mais dans ce cas l'estimateur
  intra-unité reste dans ]0 ; 1[, ce qui n'est pas le cas ici. Des valeurs intra-unité hors de ]0 ; 1[, négatives ou supérieures à 1, apparaissent quand le taux de détection **varie dans le temps** : par dérive d'un canal
  (le canal qui dérive sort vers le négatif, l'autre vers des valeurs supérieures à 1) ou par un facteur de codage commun aux deux canaux. Un simple recouvrement de patients entre les deux canaux ne suffit pas. Les valeurs réelles
  (urgences −1,0 ; SOS −11,6, tous deux négatifs, dans chaque tiers de la période) évoquent plutôt une combinaison de variations temporelles du taux de détection.
- **Asymétrie des estimateurs croisés** : -0,060 (en dessous du seuil provisoire de 0,10) : pas d'indice de boucle de surveillance, mais cela ne rattrape pas la violation de l'hypothèse 2 ci-dessus.
- **Niveau de R̂** (effets d'unité, fenêtres de 12 semaines) : médiane 0,86 pour le R croisé contre 0,70 (urgences seules) et 0,71 (SOS seul) : le R croisé est plus haut que les canaux seuls, ce qui va dans le sens de
  la proposition 6 (un canal sous-déclaré diminue le R apparent). Ce résultat ne valide rien : il n'existe aucun R vrai pour le comparer.
- **Bruit** : l'écart-type de R̂ d'une fenêtre à l'autre est du même ordre pour les trois estimateurs (0,20 ; 0,21 ; 0,20) : le R croisé n'est pas nettement plus bruité.
- **Corrélations entre estimateurs** : de rang 0,61 à 0,67 entre eux.

## 6 bis. Addendum exploratoire du 18 octobre 2026 : qu'est-ce qui produit un θ̂ hors de ]0 ; 1[ ?

Étude de simulation, **sans aucune donnée réelle** (37 départements × 105 semaines, trois vagues nationales, tailles de 40 à 300 ; 100 répétitions par scénario ; script `backend/scripts/vulnerabilite_simulation_theta.py`,
sortie complète dans `simulation_theta.md`) :

| Scénario simulé | θ̄ intra-unité, urgences (vrai 0,4) : médiane [5ᵉ ; 95ᵉ centile] | θ̂ regroupé, urgences : médiane | θ̄ intra-unité, SOS (vrai 0,6) : médiane |
|---|---|---|---|
| Taux constants et indépendants | 0,41 [0,24 ; 0,62] | 0,42 | 0,59 |
| Taux propre à chaque département (0,2 à 0,8) | 0,59 [0,24 ; 0,79] | -27,23 | 0,54 |
| Taux de SOS en baisse de 50 % dans le temps | 1,30 [0,97 ; 1,62] | 1,31 | -7,82 |
| 50 % des patients SOS passent ensuite aux urgences | 0,55 [0,34 ; 0,75] | 0,57 | 0,78 |
| 90 % des patients SOS passent ensuite aux urgences | 0,84 [0,67 ; 1,00] | 0,86 | 0,83 |
| Facteur de codage hebdomadaire commun au pays (écart-type 15 %) | 0,40 [0,22 ; 0,57] | 0,37 | 0,63 |
| Facteur de codage hebdomadaire commun au pays (écart-type 30 %) | -0,21 [-3,18 ; 0,52] | -0,24 | 1,23 |
| Facteur de codage propre à chaque département-semaine (écart-type 15 %) | 0,40 [0,18 ; 0,59] | 0,39 | 0,64 |
| Facteur de codage propre à chaque département-semaine (écart-type 30 %) | -0,85 [-1,54 ; -0,19] | -0,84 | 1,87 |

Aucun scénario ne reproduit à lui seul les valeurs réelles (urgences −1,0, SOS −11,6). Ce qui ressort : l'estimateur n'est fiable que si le taux de détection est constant dans le temps ; il est robuste à un taux propre à chaque département
(estimateur intra-unité) ; un recouvrement de patients le décale sans le faire sortir de ]0 ; 1[ ; toute variation temporelle du taux le fait sortir, dans un sens qui dépend du canal. Une correction par département du taux de détection (option « taux de détection par département »
envisagée en fin de phase 4) **n'aurait donc pas levé l'obstacle** : l'estimateur croisé intra-unité tolère déjà un taux constant propre à chaque département, et un θ propre à chaque département, estimé sur 105 semaines, est trop imprécis pour servir
(simulation, script `vulnerabilite_simulation_theta_departement.py` : 28 % à 67 % des estimations dans ]0 ; 1[ selon le niveau des comptes même si le modèle est exact, et une corrélation médiane de 0,12 seulement entre les estimations de deux moitiés de période). Une seconde pré-inscription sur ce point n'est pas recommandée.

Correctif apporté au code lors de cette étude : l'estimateur du taux de détection mélangeait deux conventions de variance (ddof 0 et 1) héritées du script de la note, négligeable à 20 000 points mais biaisé à 105 points. Les deux sont à présent à ddof = 1 ;
les valeurs regroupées du rapport ont été recalculées avec cette convention (écart de l'ordre de 0,01 à 0,02).

## 7. Pourquoi l'échec ? Hypothèses, non testées

1. **L'hypothèse 2 n'est pas vérifiée sur ces données** (θ̂ hors de ]0 ; 1[ y compris en intra-unité). La cause n'est pas établie. Les simulations du §6 bis écartent deux explications simples (taux propre à chaque département, recouvrement de patients entre
   canaux) et retiennent comme compatible une **variation dans le temps du taux de détection** (dérive d'un canal, ou facteur de codage ou d'attention commun aux deux canaux : « suspicion de COVID », pratiques de diagnostic, attention médiatique). Un facteur commun est partagé par l'instrument et le
   régresseur de l'estimateur croisé et abaisse mécaniquement la pente estimée, ce qui fait perdre l'avantage attendu. C'est une hypothèse de travail, non testée sur les données.
2. **C1′ ne teste pas la propriété principale du R croisé.** Le R croisé corrige le *niveau* du R (atténuation par la sous-déclaration) ; la corrélation de rang est insensible à une correction monotone du niveau et ne mesure que le bruit relatif. Un critère de rang ne peut donc pas montrer l'avantage attendu, seulement l'absence de dégradation. Faute de R vrai, aucune
   comparaison de niveau n'est possible ici. C'est une limite du critère pré-enregistré, pas une raison d'en changer.
3. **La référence est nationale, lissée par SPF et indirecte** (eaux usées), alors que R̂ est estimé sur 37 départements : la concordance attendue est faible même pour un bon estimateur (les canaux seuls ne dépassent pas 0,42).
4. **Le modèle suppose un flux d'étincelles constant**, alors que les vagues varient par construction ; les effets temporels complets, qui retirent cette composante nationale, dégradent encore le résultat.
5. **Très peu d'événements indépendants** : deux démarrages exploitables, trois vagues au total.

## 8. Ce que cela implique

- **Pour le module** (mis à jour le 18 octobre) : les identités et estimateurs démontrés ou vérifiés par simulation (voir `reproduction.md`) ne sont pas remis en cause. En revanche, **le module n'est pas validé sur données réelles** : la supériorité attendue de l'estimation multicanal
  n'est pas observée sur ce banc, et l'hypothèse qui la fonde (taux de détection constants, canaux indépendants) est contredite par ses propres diagnostics.
- **Ne pas publier** de résultat de ce banc sur le site (règle 4 du cahier : rien ne s'affiche avant la fin de la phase 4 et l'accord explicite de Clément). Si une page « Épidémies » est un jour publiée, elle devra afficher cet échec, pas un indicateur.
- **Suite possible** (décisions de Clément) : (a) ~~tester un taux de détection par département~~ : écarté après simulation (§6 bis) ; (b) obtenir 2020-2022 (≈ 10 vagues de plus et le R publié), ce qui nécessiterait la demande à Santé publique France
  (brouillon prêt, non envoyée par décision de Clément) ; (c) passer au deuxième banc recommandé de la note (événements de Dansgaard-Oeschger, signal continu, deux capteurs), où l'hypothèse 2 est de nature différente ;
  (d) ne rien contribuer à ewstools à ce stade : le cahier le conditionne à une validation, qui n'a pas eu lieu.
- **Décomposition de la réaction** (exploratoire prévue au cahier) : non réalisée ; sur 105 semaines, avec des vagues de faible amplitude et une hypothèse 2 contredite, ses résultats ne seraient pas interprétables.

## 9. Statuts des résultats (règle interne 5)

| Résultat | Statut |
|---|---|
| C1′ non réussi ; C3 non propre ; verdict « échec » | observé sur données |
| Robustesse de l'échec aux sensibilités ; stabilité aux graines | observé sur données |
| C2′ (tendances avant vague) | observé sur données, descriptif, 2 événements |
| θ̂ hors de ]0 ; 1[, niveaux de R̂, asymétrie | observé sur données, exploratoire |
| Explications du §7 | ouvert (hypothèses, non testées) |
