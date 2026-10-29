# Synthèse : ce que la note établit, ce que les deux bancs ont montré

Rédigée le 28 octobre 2026. Branche locale `vulnerabilite-epidemies`. Rien de ceci n'est publié.

## 1. L'idée

La note propose de mesurer non pas *quand* un système va basculer, mais *à quel point il est proche du seuil où une étincelle ordinaire suffit*. Deux grandeurs : l'inflammabilité **R** (combien d'événements chaque événement en déclenche) et la
courbure **c** (la part collective de la contagion). Elles donnent l'étincelle critique s\* (identité R = 1 − c·s\*), un indice **Φ** et, plus généralement, un coût minimal d'embrasement **V\***, censé approcher le logarithme du temps moyen avant embrasement spontané.
Les indicateurs classiques (autocorrélation, variance) ne dépendent que de R : ils ne voient pas c.

## 2. Ce qui est établi

| Résultat | Statut | Preuve |
|---|---|---|
| Points fixes, R = 1 − c·s\*, barrière c·s\*³/6, forme close de Φ | démontré | vérifié symboliquement (`tests/vulnerabilite/test_modele.py`) |
| Autocorrélation et dispersion identiques pour des sociétés dont le temps avant embrasement varie d'un facteur supérieur à 400 | démontré (linéarisation) et vérifié par simulation | `reproduction.md` |
| Loi des temps : pente de ln E[T] en V\* = 1,03 sur 147 jeux de paramètres, calculée avec les temps exacts de la chaîne de Markov | vérifié numériquement | `reproduction.md`, `test_vstar.py` |
| Un seul canal sous-déclaré divise le R apparent (0,24 et 0,31 pour un R vrai de 0,60) ; l'estimateur croisé de deux canaux indépendants retrouve 0,60, et l'asymétrie désigne le canal sous boucle de surveillance | démontré (cas linéaire) et vérifié par simulation | `reproduction.md` |
| Une coupure trop basse avant un embrasement fait paraître la société plus sûre : Φ̂ = 35 pour Φ = 11,5 | vérifié numériquement | `reproduction.md` |

Le module Python (`backend/app/vulnerabilite/`) reproduit les chiffres de la note, souvent à la décimale près. Deux défauts mineurs ont été trouvés dans les scripts de la note (une fermeture en variable globale dans `g2`,
une affirmation « facteur 0,6 à 1,4 » qui ne vaut que pour 3 jeux sur 5) ; ils ne changent aucune conclusion.

## 3. Ce que les tests sur données réelles ont montré

**Banc épidémies** (urgences et SOS Médecins, 37 départements, 105 semaines, décembre 2022 à décembre 2024). Critères écrits et figés avant tout calcul (étiquette `preenregistrement-v1`) : **échec**.

- Le R croisé n'est pas mieux corrélé à la croissance des eaux usées que chaque canal seul : ρ = 0,26 contre 0,34 (urgences) et 0,42 (SOS Médecins) ; Δ = −0,164, intervalle à 90 % [−0,39 ; 0,10].
- En mélangeant au hasard les départements d'un canal, Δ ne change presque pas (−0,139) : l'appariement réel n'apporte rien de mesurable.
- Même constat dans les 8 analyses de sensibilité et avec 3 graines.
- Le taux de détection estimé sort de ]0 ; 1[ y compris en estimateur intra-unité (−1,0 et −11,6). L'hypothèse d'indépendance et de constance des taux de détection n'est pas vérifiée. Une variation dans le temps du taux (dérive d'un canal, facteur de codage commun) reproduit ce
  comportement en simulation ; la cause réelle n'est pas établie.
- Il n'y a que 2 démarrages de vague exploitables et 2 témoins : le critère de signal avant vague (C2) n'a pu être que descriptif.

**Banc Dansgaard-Oeschger** (carottes de glace, bascules entre deux états). Arrêté en simulation, **aucune donnée réelle consultée**.

- L'estimateur de la note (dérive quadratique, un seul pli) est inutilisable sur un double puits : V\* estimé 0,02 pour 1,2.
- Un estimateur cubique développé pour l'occasion estime correctement la barrière (rapport médian 1,04 sur fenêtres de 400 points), mais ne prédit pas le temps d'attente (corrélation médiane entre −0,14 et +0,16).
- Le critère de corrélation que j'avais fixé (≥ 0,5 dans 90 % des séries) était inatteignable : même la barrière **exacte** ne donne que +0,20 à +0,35, parce que le temps d'attente d'une bascule due au bruit est intrinsèquement très aléatoire. Avec environ 20 événements réels, le banc ne pourrait pas trancher.

## 4. Ce qu'on peut dire, et ce qu'on ne peut pas dire

- On peut dire : les propriétés mathématiques de la note tiennent, et le module les reproduit. Sur les données réelles testées, l'estimateur multicanal n'a pas montré d'avantage, et l'hypothèse qui le fonde est contredite par ses propres diagnostics.
- On ne peut **pas** dire : que l'approche « ne marche pas » en général. Un seul jeu de données réel a été évalué, avec peu de vagues, des départements urbains, et une référence indirecte.
- On ne peut pas non plus dire qu'elle marche : rien n'est validé sur données réelles. Les identités démontrées ne garantissent pas l'utilité de l'estimation.

## 5. Ce que ça enseigne

1. **Vérifier les hypothèses du modèle sur les données avant de comparer des estimateurs.** Le taux de détection constant et l'indépendance des canaux sont la base de tout le multicanal ; les diagnostics sont à calculer en premier.
2. **Un critère par corrélation de rang ne peut pas voir une correction de niveau.** Le R croisé corrige le niveau du R ; la corrélation de rang n'en tient pas compte. Il faut un critère qui mesure ce que la méthode prétend apporter.
3. **Calibrer chaque critère sur le plafond d'un oracle**, avant d'écrire l'estimateur : avec la quantité vraie, jusqu'où peut-on aller ? J'ai découvert le plafond de la phase 1c après coup.
4. **Les unités réelles sont hétérogènes** (tailles, couvertures) : effets fixes d'unité obligatoires, et les grandeurs dépendant de l'échelle (c, Φ) ne sont pas comparables entre unités.
5. **Compter les événements indépendants avant de promettre un test.** Ici, 3 vagues et 20 bascules : les marges d'incertitude dominent tout.

## 6. Suites possibles

- Obtenir l'historique 2020-2022 auprès de Santé publique France (brouillon de demande prêt, non envoyé) : une dizaine de vagues en plus et le R publié ; nécessiterait un second pré-enregistrement.
- Étudier directement l'origine de la variation du taux de détection (par exemple en comparant des départements à pratiques de codage différentes) avant toute nouvelle évaluation du multicanal.
- Un troisième banc, ou l'arrêt du chantier. Pas de contribution à ewstools tant que rien n'est validé (conforme au cahier des charges).

## 7. Où trouver quoi

| Document | Contenu |
|---|---|
| `reproduction.md` | Les chiffres de la note recalculés par le module, constats sur la note |
| `fiche_donnees.md` | Audit des données (couverture, manques, décalage entre canaux) |
| `preenregistrement.md` | Critères figés (étiquette `preenregistrement-v1`) |
| `rapport_epidemies.md` | Résultat du banc épidémies, diagnostics, simulations |
| `plan_dansgaard_oeschger.md` | Plan et arrêt du second banc (§8) |
| `phase_1c_criteres.md`, `phase_1c_resultats.md` | Critère figé et résultats de la phase 1c |
