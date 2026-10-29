# Pré-enregistrement : banc « épidémies » du module vulnérabilité

**STATUT : VALIDÉ par Clément le 18 octobre 2026** (message dans la conversation : « je valide »). Ce document est commité avec sa date
(étiquette git `preenregistrement-v1`) et ne change plus. Toute analyse ajoutée ensuite est étiquetée « exploratoire ».
Rédigé le 17 octobre 2026. Au moment de la validation, aucune évaluation (R, c, Φ, AUC, corrélation avec la référence) n'avait été calculée sur les données réelles.
Décision annexe de Clément (18 octobre 2026) : pas de demande à Santé publique France pour l'instant ; à reconsidérer si l'absence de 2020-2022 se révèle réellement handicapante.

## 0. Ce qui a été regardé avant d'écrire ce document (transparence)

| Quoi | Où | Commit |
|---|---|---|
| Audit descriptif des fichiers (couverture, manques, ruptures, décalage entre canaux, comptes mensuels nationaux) | `fiche_donnees.md` | `0a69952` |
| Règle de démarrage de vague, écrite puis commitée **avant** application | `backend/app/vulnerabilite/vagues.py` | `85d84ca` (17 oct. 2026, 14 h 45) |
| Application **unique** de cette règle à la série nationale des urgences COVID (37 départements) : 3 démarrages | §3 ci-dessous | — |
| Disponibilité des séries d'eaux usées (nombre de stations par semaine) | §5 | — |

L'auditeur a vu la forme générale des comptes mensuels nationaux avant d'écrire la règle de démarrage. Elle n'est donc pas « en aveugle » ;
elle n'a pas été ajustée après l'avoir appliquée, et on ne la réajustera pas.

## 1. Question

Le module mesure-t-il quelque chose de plus fidèle à la dynamique réelle d'une épidémie qu'un seul canal, et son signal avant une vague se
distingue-t-il de celui de périodes calmes ? Le but n'est pas de prédire une date.

## 2. Données et unités

- **Comptes** : urgences hospitalières pour suspicion de COVID-19 (`nbre_pass_corona`) et actes SOS Médecins pour suspicion de COVID-19
  (`nbre_acte_corona`), classe d'âge 0 (tous âges), par département et par jour (fichier SPF, empreintes dans `data/vulnerabilite/manifeste.json`).
- **Unités principales** : les **37 départements** ayant les deux canaux sur la totalité des 736 jours : 02, 06, 10, 13, 14, 17, 18, 21, 25, 29, 33, 34, 35, 38,
  42, 44, 45, 50, 54, 56, 59, 63, 64, 66, 67, 68, 69, 73, 74, 75, 76, 78, 80, 83, 87, 89, 91.
- **Période** : **105 semaines complètes**, du lundi 26 décembre 2022 au dimanche 29 décembre 2024.
- **Pas de temps principal** : la semaine ISO (somme des 7 jours). Pas secondaire : le jour.
- **Valeur** : comptes entiers non négatifs. Aucun taux.
- **Unités hétérogènes** : les départements diffèrent beaucoup par leur taille. Tous les estimateurs de R de ce pré-enregistrement utilisent des **effets fixes
  d'unité** (une constante par département) ; sans eux, la pente regroupée mesure la persistance des niveaux entre départements (démontré sur données
  simulées dans `tests/vulnerabilite/test_effets_unite.py` : 0,85 ou plus au lieu de 0,6). Φ̂ et ĉ, qui dépendent de l'échelle des comptes, ne sont **pas** des
  critères ici : ils restent exploratoires.

## 3. Événements : démarrages de vague

Règle fixée dans `vagues.py` (médiane des 8 semaines précédentes ≥ 20 ; semaine ≥ 1,5 fois cette médiane ; 2 semaines de croissance stricte ensuite ;
8 semaines réfractaires), appliquée à la somme nationale hebdomadaire des urgences COVID des 37 départements.

| Démarrage | Semaine (lundi) | Utilisable pour une pré-fenêtre de 16 semaines ? |
|---|---|---|
| 1 | 2023-03-06 | **non** : seulement 10 semaines d'historique |
| 2 | 2023-07-31 | oui |
| 3 | 2024-05-13 | oui |

**Trois événements, dont deux exploitables.** Les épisodes de septembre et décembre 2023, et de juin à octobre 2024, ne sont pas comptés comme des
démarrages distincts par la règle (ils suivent un démarrage sans retour au calme de huit semaines). On ne change pas la règle pour en obtenir davantage.

## 4. Fenêtres

- **Pré-fenêtre** : les 16 semaines qui précèdent le démarrage (fin = semaine t − 1). Deux sont disponibles (démarrages 2 et 3).
- **Fenêtres témoins** : fenêtres de 16 semaines qui ne rencontrent aucun intervalle [t − 8 ; t + 12] d'un démarrage t. Il en existe **10**, réparties en deux
  groupes de semaines consécutives (fins aux semaines 59 à 63 et 100 à 104 de la série), donc **deux témoins indépendants** au plus.
- **Indicateurs** calculés sur des sous-fenêtres de 8 semaines décalées d'une semaine (9 valeurs par fenêtre de 16 semaines).

## 5. Critères

### C1′ : estimation multicanal (remplace C1 : voir §7)

Pas de référence de R recouvrant la période : le R publié s'arrête en août 2022. La référence retenue est le **niveau de SARS-CoV-2 dans les eaux usées**
(SUM'Eau, indicateur national sur 12 stations, continu sur les 105 semaines ; les stations isolées ne dépassent 20 par semaine qu'à partir du 19 février 2024).
Ce n'est pas un R ; c'est une mesure indépendante des deux canaux de patients.

- Fenêtres glissantes de **12 semaines**, décalées d'une semaine : 94 fenêtres.
- Pour chaque fenêtre : `R_croisé` (pente croisée intra-unité, urgences en sortie et SOS Médecins en instrument), `R_urgences` et `R_SOS` (pentes
  d'un seul canal, intra-unité), et `g` = moyenne des log(indicateur eaux usées national semaine t+1 / semaine t) sur la fenêtre.
- Corrélations de rang de Spearman `ρ_croisé`, `ρ_urgences`, `ρ_SOS` entre chaque R et `g`, sur les 94 fenêtres.
- `Δ = ρ_croisé − max(ρ_urgences, ρ_SOS)`. Intervalles à 90 % par bootstrap par blocs de 12 semaines consécutives (les fenêtres se chevauchent fortement).
- **C1′ est réussi si** la borne basse de l'intervalle de Δ est > 0 **et** la borne basse de celui de `ρ_croisé` est > 0.
- Réserve : l'indicateur d'eaux usées est lissé par SPF (régression LOESS, puis GAM depuis septembre 2025, avec recalcul rétroactif) : il utilise des
  semaines voisines des deux côtés. Acceptable pour mesurer la concordance, pas pour juger une avance.

### C2′ : signal avant une vague (descriptif, sans seuil de réussite)

Avec deux événements exploitables et deux témoins, aucune inférence n'est possible (le test de signe ne peut jamais être significatif ; une AUC n'a pas de sens).
C2′ est donc **descriptif** : pour chaque démarrage exploitable et chaque groupe de témoins, on rapporte la tendance de Kendall (τ sur les 9 valeurs) de
`R_croisé`, `R_urgences`, `R_SOS`, de l'autocorrélation d'ordre 1 moyenne par département et de la variance moyenne par département (urgences), et on dit si
la tendance pré-démarrage est dans le bon sens (τ > 0) et où elle se situe parmi celles des fenêtres témoins. Rien n'en est conclu sur la valeur prédictive.

### C3 : placebos

- **(i) Dates aléatoires** : 2 000 tirages de 2 dates fictives de fin de pré-fenêtre parmi les fins compatibles avec les témoins ; on rapporte la distribution
  de τ pour chaque indicateur, à titre de repère pour C2′.
- **(ii) Canaux mélangés** : on permute au hasard les départements du canal SOS Médecins par rapport aux urgences (200 permutations) et on recalcule C1′.
  **C3 est propre si** la médiane de Δ sous placebo est ≤ 0 et si le 95ᵉ centile de Δ sous placebo est inférieur au Δ observé.

### Décision, écrite à l'avance

- **Succès** : C1′ réussi **et** C3 (ii) propre. C2′ est rapporté mais ne conditionne pas la décision.
- **Échec partiel** : C1′ réussi mais C3 non propre (l'avantage observé vient d'ailleurs que de l'indépendance des canaux), ou C3 propre mais C1′ non réussi.
- **Échec** : ni l'un ni l'autre. Les critères ne sont pas retouchés après coup.

## 6. Analyses de sensibilité (toutes pré-enregistrées, rapportées dans tous les cas)

1. **Effets fixes temporels complets** (un effet par semaine, commun à tous les départements), en plus des effets d'unité : retire la dynamique nationale et change
   donc ce qui est mesuré. Règle d'interprétation de Clément : si C1′ et sa sensibilité concordent, le résultat est robuste ; si elles divergent, on rapporte les deux
   et on lit l'écart comme le poids des chocs communs (limite).
2. **Décalage de SOS Médecins** : les actes SOS précèdent les urgences d'environ 4 jours. Analyse principale sans décalage ; sensibilité avec SOS décalé de 4 jours avant
   agrégation hebdomadaire.
3. **Pas quotidien** (analyse secondaire) : effets de jour de semaine + contrôles de calendrier.
4. **Contrôles de calendrier** : semaine contenant un jour férié ; vacances scolaires de la zone du département (fichiers téléchargés ; association département → zone à
   établir et à vérifier avant utilisation). Variables exogènes ajoutées à la constante, à la fois aux régresseurs et aux instruments. **Non encore implémenté dans le
   module : à faire avant la phase 4.**
5. **Départements** : ajout des 8 départements à couverture partielle (45 au total).
6. **Taille des fenêtres** de C1′ : 8 et 16 semaines au lieu de 12.
7. **Stations d'eaux usées** à partir du 19 février 2024 (au moins 20 stations par semaine) : même C1′ avec l'indicateur de chaque station associée à son département
   (association à établir), sur la période restreinte.
8. **Mesures nationales majeures** : aucune mesure sanitaire nationale majeure n'est datée entre décembre 2022 et décembre 2024 ; la sensibilité par exclusion est
   donc sans objet pour cette période.

## 7. Pourquoi C1 a changé

C1 comparait le R croisé à la référence publiée de R. Le R publié (indicateurs de suivi, ministère de la Santé) s'arrête le 16 août 2022 ; les urgences et SOS
Médecins disponibles commencent le 26 décembre 2022. Les données 2020-2022 de ces deux canaux par département ne sont pas dans le jeu officiel actuel ; les obtenir
suppose de les demander à Santé publique France (brouillon de demande : `demande_spf.md`). Si elles arrivent, C1 initial et C2 (une dizaine de vagues
supplémentaires) deviennent évaluables, et ce document devra être complété par un second pré-enregistrement avant tout calcul sur ces données.

## 8. Limites reconnues à l'avance

- 37 départements dotés d'une association SOS Médecins, probablement urbains : pas la France entière.
- Deux événements exploitables : le banc ne peut pas démontrer une valeur prédictive, seulement l'exclure en cas de signal opposé.
- Modèle à état calme et flux d'étincelles constant, appliqué à une épidémie avec saisonnalité, variants et immunité : mauvaise spécification possible.
- Indépendance conditionnelle des canaux (hypothèse 2) non garantie : un patient peut passer par SOS Médecins puis les urgences.
- Niveau calme faible (comptes hebdomadaires médians de 17 à 19 par département) : zone où l'estimation de la courbure est la moins fiable.
- La référence d'eaux usées est nationale, lissée, et sa composition a changé (12 puis 54 stations) ; la série utilisée est celle des 12 stations.

## 9. Avant d'évaluer (travail restant, sans lien avec les résultats)

1. Contrôles de calendrier dans l'estimateur (§6, point 4) et association département → zone scolaire.
2. Script d'évaluation qui exécute exactement §5, écrit et testé sur données simulées avant la première exécution réelle.
3. Validation de ce document par Clément ; commit daté ; étiquette `preenregistrement-v1`.
