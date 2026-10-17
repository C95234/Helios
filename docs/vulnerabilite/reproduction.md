# Reproduction de la note par le module `app.vulnerabilite`

Statut : **vérifié numériquement** (aucun résultat sur données réelles). Branche `vulnerabilite-epidemies`.

Ce document répond à une question : le module Python reproduit-il les chiffres de la note
« Vulnérabilité d'une contagion sociale » (v3.1) ? Réponse courte : **oui, pour toutes les lignes testées**,
souvent à la décimale près, parce que le module reprend les graines et l'ordre de consommation des tirages des scripts de
la note. Deux constats sur la note elle-même sont donnés plus bas (§4).

## 1. Source de la note

La note a été lue à partir de `vulnerabilite_contagion_v3_1.tex` (dans le zip des scripts). Le fichier PDF n'a pas pu être
ouvert dans l'environnement de travail. Si le PDF diffère du `.tex`, le PDF fait foi.

## 2. Étape 1.0 : les scripts originaux, rejoués tels quels

Les scripts du zip ont été copiés dans un dossier de travail et exécutés avec le Python du dépôt (NumPy, SciPy, SymPy ;
aucune entrée-sortie hors `np.save`). 20 scripts lancés ; 19 terminés sans erreur, dont les sorties coïncident avec les tableaux
de la note à la précision imprimée :
`t1`, `t2`, `t3`, `t4`, `t4b`, `t4c`, `t5`, `t5b`, `t6`, `t7`, `t7b`, `t8`, `t9`, `t10c`, `t11`, `g1`, `g2`, `g3`, `p1a`
(de 2 s à 327 s chacun, 4 processus en parallèle). `t10_reseau.py` a été interrompu volontairement au bout de 6 minutes (il est long) ; ses
premières lignes coïncident avec la note (`E[T]` = 94 mesuré contre 63 prédit à Φ = 4,78 sans couplage).

Non rejoués, car hors du périmètre de la v1 du cahier : `p1b` (réseau, points-selles), `p1c` (modèle joint contagion + réaction),
`p2`, `p3` (filtre particulaire : résultat négatif dans la note), `p4` (boucle d'alerte), `t10b` (phase 1b).

## 3. Le module recalcule les chiffres de la note

Chaque ligne est calculée par `backend/scripts/vulnerabilite_reproduction.py` (graines des scripts de la note ; 420 s) ;
la colonne « Tolérance du cahier » est celle du §3.3 du cahier des charges. Tous les tests correspondants existent dans
`backend/tests/vulnerabilite/` (marqueur `slow` pour les longs : `pytest -m "slow or not slow"`).

| Test | Note (v3.1) | Module | Tolérance du cahier |
|---|---|---|---|
| Φ, R=0,6 c=0,02 m₋=3 : forme close / intégrale numérique | 4,78 | 4.778206 / 4.778206 | 1e-6 |
| Cécité : AC1 pour c = 0,01 / 0,02 / 0,03 (R=0,6) | 0,58 / 0,61 / 0,60 | 0.58 / 0.61 / 0.60 | 0,60 ± 0,04 |
| Cécité : dispersion (variance/moyenne) pour les mêmes c | 1,56 / 1,67 / 1,62 (théorie 1,56) | 1.56 / 1.67 / 1.62 | identiques entre eux |
| Estimation 100×200 : Φ̂ médian, Φ = 11.53 | 11,0 | 11.00 | ± 15 % (Φ = 11,5 et 4,8) |
| Estimation 100×200 : Φ̂ médian, Φ = 4.78 | 5,0 | 4.97 | ± 15 % (Φ = 11,5 et 4,8) |
| Estimation 100×200 : Φ̂ médian, Φ = 2.75 | 3,9 | 3.86 | ± 15 % (Φ = 11,5 et 4,8) |
| Coupure à 4 × niveau calme : Φ̂ médian, Φ = 11.53 | 35,1 | 35.13 | 4× : > 1,5 Φ ; 6× : ± 10 % |
| Coupure à 6 × niveau calme : Φ̂ médian, Φ = 11.53 | 12,5 | 12.46 | 4× : > 1,5 Φ ; 6× : ± 10 % |
| Coupure à 4 × niveau calme : Φ̂ médian, Φ = 4.78 | 9,6 | 9.60 | 4× : > 1,5 Φ ; 6× : ± 10 % |
| Coupure à 6 × niveau calme : Φ̂ médian, Φ = 4.78 | 4,9 | 4.93 | 4× : > 1,5 Φ ; 6× : ± 10 % |
| Coupure à 4 × niveau calme : Φ̂ médian, Φ = 2.75 | 5,2 | 5.15 | 4× : > 1,5 Φ ; 6× : ± 10 % |
| Coupure à 6 × niveau calme : Φ̂ médian, Φ = 2.75 | 2,8 | 2.76 | 4× : > 1,5 Φ ; 6× : ± 10 % |
| Chocs communs croissants (Φ = 11,5) : Φ̂ avec effets fixes temporels | 11,3 | 11.33 | ± 20 % |
| Chocs communs croissants : Φ̂ sans effets fixes (plafonné à 30) | > 30 | 30.00 | — |
| Estimateur croisé, cas linéaire, boucle η=0,5 : croisé 2←1 / croisé 1←2 | 0,60 / 0,83 | 0.60 / 0.83 | 0,60 ± 0,03 |
| Même cas : R̂ naïf du canal sous boucle / du canal indépendant | 0,71 / 0,31 | 0.71 / 0.31 | naïf ≈ 0,71 |
| Multicanal quadratique, Φ = 12,17, boucle η=0 : naïf / 2 canaux / 3 canaux instr. 1 / instr. 3 | 35,8 / 12,8 / 12,7 / 11,5 | 35.8 / 12.8 / 12.7 / 11.5 | instr. 3 : 11,5 ± 20 % |
| Multicanal quadratique, Φ = 12,17, boucle η=1 : naïf / 2 canaux / 3 canaux instr. 1 / instr. 3 | 36,7 / 4,4 / 10,5 / 11,5 | 36.7 / 4.4 / 10.5 / 11.5 | instr. 3 : 11,5 ± 20 % |
| Dispersion φ = 1 : φ̂ médian (deux canaux) | 1,00 | 1.00 | 1 et 2 : ± 0,1 |
| Dispersion φ = 2 : φ̂ médian (deux canaux) | 2,00 | 2.00 | 1 et 2 : ± 0,1 |
| Dispersion φ = 4 : φ̂ médian (deux canaux) | 3,78 | 3.78 | 1 et 2 : ± 0,1 |
| Réaction : société explosive tenue (A / a) | 0,82 / 1,03 | 0.82 / 1.03 | ± 0,05 |
| Bootstrap par unités, 100×200 : couverture de l'intervalle à 90 % | 90 % | 90 % | 82–97 % |
| Loi des temps : pente de ln E[T] en Φ (nombre de jeux, corrélation) | 1,04 (22, 0,92) | 1.04 (22, 0.92) | 0,8–1,3 |
| V* Poisson contre temps exacts : pente (jeux, écart-type résiduel, corrélation) | 1,03 (147, 0,28, 0,9993) | 1.029 (147, 0.275, 0.9993) | 0,9–1,15 |
| Identité λ = 1 − c s*, double puits cubique : écart pour s* = 0,67 / 0,45 / 0,24 / 0,11 | 0,135 / 0,060 / 0,017 / 0,003 | 0.135 / 0.060 / 0.017 / 0.003 | < 0,005 pour s* = 0,11 |
| V* gaussien contre temps simulés, application quadratique : pente | 0,98 (18 cas, deux familles) | 0.981 (9 cas, famille quadratique seule) | 0,85–1,1 |
| Capteurs affines, bruit de mesure = bruit dynamique : V* deux capteurs / un capteur | 3,94 / 17,65 (V* vrai 3,32) | 3.94 / 17.65 (V* vrai 3.32) | ≈ 3,9 ± 20 % (un capteur ≈ 17,7) |

Remarques de lecture :
- La ligne « V* gaussien » ne porte que sur la famille quadratique (9 cas) : la note regroupe 18 cas (quadratique et double puits)
  et trouve aussi 0,98.
- La ligne « Φ̂ sans effets fixes » est plafonnée à 30, comme dans le script : l'estimation naïve ne détecte alors aucun seuil.
- Les lignes de dispersion pour φ = 4 attendent 3,78 (biais connu de la note : 3,6 à 3,8), pas 4.

## 4. Constats sur la note et ses scripts

Aucun n'invalide un résultat de la note ; tous doivent être connus avant d'utiliser le module sur des données.

1. **Le script `g2` applique à la famille « quadratique » une courbure différente de celle annoncée.** La fermeture
   `lambda x, mu=mu: mu + a*x + c*x*x` lit `c` en variable globale, que la boucle des doubles puits réaffecte avant le tour des
   quadratiques. La famille effectivement simulée a donc c ≈ 0,685 (courbure du dernier double puits, vérifiée : elle redonne exactement les
   λ = 0,448 / 0,528 / 0,625 imprimés par le script) et non c = 1.
   Avec les paramètres annoncés (a = 0,4, c = 1), le module trouve une pente de 0,981 contre 0,98 dans la note : la conclusion tient.
2. **« Facteur 0,6 à 1,4 » (note, section 5, loi des temps avec surdispersion) ne vaut que pour 3 jeux sur 5.** Le script `t9` donne
   des rapports mesuré/prédit de 1,42 (φ = 2, c = 0,01), 1,28, 0,60, 0,79, et le cinquième jeu (Φ = 10,6) est censuré à 92 % : la
   comparaison n'y est pas informative (la moyenne mesurée est un minorant).
3. **La loi des temps dépend de R.** Pente de ln E[T] en Φ : 1,18 pour R = 0,4, 1,15 pour R = 0,6, **1,40 pour R = 0,8** (sortie de
   `t2`). Le chiffre global (1,04 sur 22 jeux) cache cette dépendance ; la correction par le préfacteur 2π/(1−R) de la proposition 4
   la prend en compte dans la note.
4. **L'estimation du couplage ŵ proposée par la note ne fonctionne pas telle quelle.** Elle n'est pas testée dans la note. Testée ici
   (grille 10×10, 20 sociétés × 200 pas, R = 0,6) : ŵ médian = 0,38 pour w = 0, entre 0,41 et 0,59 pour w = 0,3, entre 0,55 et 0,59 pour
   w = 0,6. Elle ne suit pas le couplage vrai. `AjustementReseau.w_estime` est étiqueté non fiable. En revanche le classement par Φ̂
   avec terme de voisinage tient (AUC 0,85 à w = 0,3, 0,86 à w = 0,6, comme dans la note), et à w = 0 l'AUC n'est que de 0,67 (non
   mentionné dans la note).
5. **Détails de portage conservés pour la fidélité** : `simulate_units` retire aussi les `marge` derniers pas des séries qui ne
   s'embrasent jamais ; la régression de `fit_net` est non pondérée (le poids calculé n'est pas utilisé) ; la variance de θ̂ est à ddof = 0
   et la covariance à ddof = 1 (écart négligeable) ; le niveau calme `m₋` vaut la moyenne de toutes les valeurs observées.
6. **Un défaut a été corrigé au passage dans le module** : la détection des points fixes par balayage de grille (`fixed()` des scripts)
   comptait deux fois un zéro tombé exactement sur un nœud ; `modele.zeros_de_derive` ne le fait plus. Sans effet sur les runs de la note.
7. **Définition du niveau calme sur données réelles.** `m₋` = moyenne des valeurs observées est adapté à des séries simulées coupées
   avant l'embrasement ; sur des données réelles, il doit être défini explicitement (`niveau_calme=`), donc dans le pré-enregistrement.

## 5. Statut de chaque brique du module

| Brique | Statut |
|---|---|
| Points fixes, R = 1 − c·s*, barrière c·s*³/6, formes closes de Φ, Φ_φ = Φ/φ | démontré (vérifié symboliquement) |
| Identité générale λ = 1 − c·s* + O(s*²), écart ∝ s*² | démontré ; vérifié numériquement |
| Loi des temps E[T] ≈ C·2π/(1−R)·e^Φ | approximation, vérifié numériquement |
| Cécité du second ordre (AC1 et dispersion ne voient que R) | démontré pour la linéarisation ; vérifié numériquement |
| Estimateur Φ̂, règle de coupure haute, effets fixes temporels | vérifié numériquement |
| Estimateur croisé (prop. 7), taux de détection (prop. 8), dispersion (prop. 10) | démontré ; estimation vérifiée numériquement |
| V* en dimension 1 (Poisson, binomiale négative, gaussien), ln E[T] ≈ V* | vérifié numériquement (calcul exact, 147 cas) |
| Capteurs affines (prop. 14) | démontré ; vérifié numériquement |
| Bootstrap par unités | vérifié numériquement (100 unités ou plus) ; sous-couvre à 16 unités |
| Bootstrap par blocs de temps, coupure itérative | **expérimental** (non testés dans la note) |
| Décomposition de la réaction (ARMA(2,1)) | **expérimental** (fragile quand la réaction est faible ou lente) |
| Estimation du couplage ŵ | **non fiable** (§4, point 4) |
| Seuil d'asymétrie des estimateurs croisés (0,10) | **provisoire** : à fixer au pré-enregistrement |
| Réseau : barrière collective V*, modèle joint contagion + réaction, boucle d'alerte | **phase 1b**, hors périmètre |
| Application à des données réelles | **ouvert** : rien n'est testé sur données réelles |
