# Second banc : événements de Dansgaard-Oeschger (carottes de glace du Groenland). Plan de phase 0

**STATUT (28 octobre 2026) : BANC ARRÊTÉ à la fin de la phase 1c (voir §8).** Rien n'a été téléchargé. Aucune donnée réelle n'a été regardée.

## 1. Pourquoi ce banc, et quelle question

La note le désigne comme le deuxième banc recommandé : signal continu, une vingtaine de bascules répétées, et le cas où le ralentissement critique est connu pour échouer. La question utile n'est pas « un signal précède-t-il la bascule ? » (déjà traitée dans la littérature),
mais celle que la note défend : **l'indice de vulnérabilité (V\*) renseigne-t-il sur le temps d'attente avant la bascule suivante ?** (loi ln E[T] ≈ V\*, vérifiée en simulation sur des comptages et sur des signaux continus).

## 2. Ce que dit la littérature (sources lues en résumé seulement)

- Ditlevsen et Johnsen (2010, *Geophysical Research Letters* 37, [doi:10.1029/2010GL044486](https://doi.org/10.1029/2010GL044486)) : pas d'augmentation de variance ni d'autocorrélation avant les événements ; les bascules seraient induites par le bruit et peu prévisibles.
- Rypdal (2016) conteste : la variabilité à haute fréquence de NGRIP augmente avant les débuts d'interstadiaires. Hummel, Boers et Rypdal (2025, *Earth System Dynamics* 16, 2035) refont le test et trouvent moins de signaux significatifs que les études précédentes.
- Je n'ai lu que des résumés et des pages de présentation, pas les articles complets : à vérifier avant toute citation.

## 3. Données (métadonnées vérifiées par recherche, rien téléchargé)

| Besoin | Source trouvée | À vérifier |
|---|---|---|
| δ¹⁸O de NGRIP, résolution 20 ans, chronologie GICC05 | NOAA/WDS Paleoclimatology, étude NCEI 6086, [doi:10.25921/pkqb-2w42](https://doi.org/10.25921/pkqb-2w42) ; page de données du Niels Bohr Institute (iceandclimate.nbi.ku.dk/data) ; PANGAEA 10.1594/PANGAEA.586838 | Couverture réelle du fichier (une notice indique 0 à 41,76 ka b2k, une autre 60 ka) ; licence |
| Deuxième capteur indépendant | Calcium et δ¹⁸O de NGRIP avec points de synchronisation (NOAA, Rasmussen et al. 2007) ; carottes GRIP et GISP2 | Disponibilité de GRIP et GISP2 à 20 ans sur la même chronologie ; nature du bruit commun et du bruit propre à chaque carotte |
| Liste des événements (débuts d'interstadiaires) | Rasmussen et al. (2014), *Quaternary Science Reviews* 106, 14-28, [doi:10.1016/j.quascirev.2014.09.007](https://doi.org/10.1016/j.quascirev.2014.09.007) : stratigraphie des stades et interstadiaires, une vingtaine d'événements sur la dernière période glaciaire | Table des âges de début à extraire du texte (mon lecteur de PDF est indisponible : à fournir ou à lire en ligne) |

Utiliser la liste publiée, et non une détection maison, évite un degré de liberté du chercheur.

## 4. Étude de faisabilité par simulation (aucune donnée réelle) : `vulnerabilite_faisabilite_do.py`

Double puits dx = (x − x³ + h(t))dt + σ dW, bruit σ = 0,65, forçage lent h(t), observation tous les 20 ans pendant 48 000 ans (2 400 points), deux capteurs affines (gains 1 et 0,7, décalages, bruit de mesure 25 %). Environ 19 bascules par série.
V\* à deux capteurs (proposition 14) estimé sur des fenêtres glissantes de 100 points (2 000 ans), 4 séries, 348 fenêtres :

| Grandeur | Valeur |
|---|---|
| V\* estimé, médiane | **0,02** (valeur attendue de l'ordre de 1,2) |
| Corrélation de rang V\*, ln du temps avant la bascule suivante | **−0,16** (le signe attendu est positif) |
| Corrélation de rang AC1, idem | −0,10 |
| Corrélation de rang variance, idem | −0,09 |

**Conclusion de la faisabilité : l'estimateur actuel n'est pas utilisable tel quel sur ce type de données.** Trois obstacles :
1. **Une seule unité.** Les tests de la note utilisent 50 à 100 séries de 200 à 300 points ; ici il y a une seule série, découpée en fenêtres de 100 points.
2. **Mauvais modèle de dérive.** L'estimateur ajuste une parabole à un pli (un état calme, un seuil). Un système à deux états avec des bascules à l'intérieur des fenêtres a une dérive cubique ; l'ajustement quadratique est gravement biaisé (V\* estimé 60 fois trop bas).
3. **Fenêtres qui contiennent des bascules.** Un stade (phase froide) dure souvent moins de 2 000 ans ; une fenêtre assez longue pour estimer la dérive contient les deux états.

## 5. Proposition : une phase 1c de développement, avec un critère d'arrêt écrit à l'avance

1. **Estimateur adapté**, testé en simulation uniquement : dérive polynomiale de degré 3 à deux capteurs (variables instrumentales avec les puissances de l'autre capteur), et V\* calculé sur le double puits (le code `vstar_gaussien` accepte déjà une dérive quelconque). Fenêtres par stade plutôt que fenêtres glissantes si la simulation le justifie.
2. **Critère de passage aux données réelles, fixé avant d'écrire l'estimateur** : en simulation à 20 ans de résolution, 25 bascules, une série et deux capteurs, la corrélation de rang entre V\* estimé et ln du temps d'attente doit dépasser 0,5 dans au moins 90 % des séries simulées ; la plupart des fenêtres doivent donner un V\* fini et de l'ordre de la valeur vraie (à ±50 %).
3. **Si le critère n'est pas atteint : on s'arrête** et on documente pourquoi (le banc n'est pas faisable avec la note actuelle). Aucune donnée réelle n'est alors regardée.
4. **Si le critère est atteint** : audit des données (phase 2), pré-enregistrement (phase 3) puis évaluation (phase 4), dans le même ordre que pour les épidémies : critères écrits et commités avant toute évaluation.

Probabilité de succès estimée : modeste. Le bruit de mesure entre carottes est faible devant le signal climatique, ce qui est favorable, mais il n'y a qu'environ 20 événements, une seule série, et la note signale elle-même que la forme de la non-linéarité est une limite ouverte.

## 6. Risques

- Les événements ne sont pas des réalisations indépendantes d'un même système (le forçage glaciaire varie lentement) : la loi du temps d'attente suppose des paramètres stationnaires.
- Le temps d'attente observé est la durée du stade ; il dépend aussi de l'amplitude des fluctuations de fond que l'estimateur lit comme du bruit.
- Résolution de 20 ans, plus fine que le plus court des interstadiaires mais proche de la durée des bascules (quelques décennies) : la dynamique rapide est mal échantillonnée.
- Environ 20 événements : une corrélation de rang ne sera jamais très précise (écart-type voisin de 0,2).

## 7. Questions pour Clément

1. Lancer la phase 1c (estimateur adapté et simulation, sans donnée réelle), avec arrêt si le critère du §5 n'est pas atteint ?
2. Second capteur : une autre carotte (GRIP ou GISP2, bruit propre à chaque site) ou le calcium de NGRIP (même carotte, mesure différente) ? Je recommande une autre carotte si elle est disponible à 20 ans.
3. Autorises-tu le téléchargement des fichiers de données publics (NOAA ou Niels Bohr Institute, quelques centaines de Ko) seulement si le critère de la phase 1c est atteint ?


## 8. Résultat de la phase 1c (28 octobre 2026) : le critère n'est pas atteint, le banc est arrêté

Critère figé avant l'estimateur (`phase_1c_criteres.md`, étiquette `phase1c-criteres-v1`) ; estimateur et script figés avant exécution (étiquette `phase1c-code-v1`). Simulations seulement, aucune donnée réelle. 30 séries par combinaison.

| σ | Fenêtre (points) | Bascules par série | Séries avec ρ ≥ 0,5 | ρ médian | V\* fini | Rapport médian V\* estimé / vrai | ρ AC1 | ρ variance | Réussi |
|---|---|---|---|---|---|---|---|---|---|
| 0.55 | 100 | 21.1 | 7% | 0.15 | 38% | 1.38 | +0.13 | +0.14 | non |
| 0.55 | 200 | 21.7 | 0% | -0.03 | 61% | 1.22 | +0.08 | +0.09 | non |
| 0.55 | 400 | 23.0 | 0% | -0.12 | 81% | 1.05 | +0.06 | +0.09 | non |
| 0.65 | 100 | 39.4 | 3% | 0.16 | 46% | 1.56 | +0.05 | +0.09 | non |
| 0.65 | 200 | 40.0 | 3% | -0.14 | 57% | 1.14 | +0.04 | +0.01 | non |
| 0.65 | 400 | 35.5 | 0% | -0.13 | 79% | 1.04 | +0.03 | +0.00 | non |

**Aucune des six combinaisons ne réussit. Selon la règle écrite à l'avance, on s'arrête : aucune donnée réelle n'est téléchargée.**

Deux constats distincts :

1. **L'estimateur à dérive cubique fonctionne comme estimateur de la barrière, mais pas comme prédicteur du temps d'attente.** Avec des fenêtres de 400 points, V\* est fini dans près de 80 % des fenêtres et son rapport médian à la valeur vraie est de 1,04 à 1,05 (contre 0,02 pour 1,2 attendu avec l'estimateur quadratique de la faisabilité). En revanche, sa corrélation avec ln du temps d'attente est nulle ou négative (médiane de −0,12 à −0,14), et celle de l'autocorrélation et de la variance aussi (≤ +0,14).
2. **Le critère de corrélation était inatteignable par construction.** Le temps d'attente d'une bascule induite par le bruit est une variable aléatoire à forte dispersion (ln T garde un écart-type d'environ 1,3 même quand la barrière est connue exactement). Calculée avec la barrière **exacte** (V\* vrai, script `vulnerabilite_phase_1c_plafond.py`),
   la corrélation de rang avec ln du temps d'attente n'est que de +0,20 à +0,35 (médiane) selon la combinaison, et seulement 0 à 23 % des séries atteignent 0,5 (le critère en exigeait 90 %). Aucun estimateur, même parfait, ne pouvait réussir. C'est un défaut de ma calibration du critère, découvert après coup.

**Pourquoi on s'arrête quand même, et ne corrige pas le critère pour relancer.** Un critère révisé après avoir vu les résultats perdrait sa valeur de garde-fou. Surtout, le constat 2 s'applique aux données réelles : avec environ 20 événements, une corrélation attendue de l'ordre de 0,3 pour un oracle a un écart-type d'estimation voisin de 0,2 ; elle serait indiscernable de zéro.
Le banc ne pourrait donc pas trancher, quel que soit l'estimateur.

Si Clément veut malgré tout poursuivre, il faudrait un nouveau critère, calibré sur ce plafond (par exemple : corrélation de l'estimateur d'au moins la moitié de celle de la barrière exacte, avec un nombre d'événements suffisant), écrit et figé avant toute nouvelle simulation, en reconnaissant qu'il est posé après avoir vu ces résultats. Je ne le recommande pas.
