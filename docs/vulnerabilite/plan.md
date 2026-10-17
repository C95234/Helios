# Module « vulnérabilité » — plan de phase 0

Branche : `vulnerabilite-epidemies` (créée depuis `main`, rien de poussé).
Statut de ce document : **proposition, en attente de validation de Clément**. Aucune ligne de code du module n'est écrite.

## 1. Ce qui a été lu

| Pièce | Lue ? | Remarque |
|---|---|---|
| `cahier-des-charges-vulnerabilite-epidemies.md` | oui, en entier | — |
| `vulnerabilite-modele-scripts.zip` | en entier : `core`, `t1`, `t2`, `t3`, `t4`, `t4c`, `t5`, `t6`, `t7`, `t7b`, `t8`, `t9`, `t10c`, `g1`, `g2`, `g3`, `p1a`, `p1c` ; en partie : `t10` (25 premières lignes), `t11`, `p4` (20 premières lignes) ; **pas lus** : `t4b`, `t5b`, `t10b`, `p1b`, `p2`, `p3` | 27 scripts + 3 sources `.tex` (v1, v3, v3.1) |
| `vulnerabilite_contagion_v3_1.pdf` | **non** | Le lecteur de PDF de l'environnement ne fonctionne pas (poppler absent). J'ai lu à la place `vulnerabilite_contagion_v3_1.tex` du zip : même titre, même date (17 octobre 2026), même version. **Je ne peux pas garantir que le PDF est exactement la compilation de ce `.tex`** (le cahier annonce 16 pages). Si le PDF diffère du `.tex`, c'est le PDF qui fait foi : dis-le-moi. |

Rien n'a été exécuté : ni les scripts de la note, ni du code Hélios.

## 2. Emplacement proposé

Le cahier propose `helios/vulnerabilite/` « à défaut de conventions existantes ». Le dépôt en a :
le backend est un package `app` (`backend/app/stats/`, `backend/app/connectors/`, `backend/app/routers/`, imports `from app.stats...`), les tests sont à plat dans `backend/tests/`, il n'existe pas de package `helios/`.

**Proposition :**

```
backend/app/vulnerabilite/          # le module (même arborescence que celle du cahier §3.1)
backend/tests/vulnerabilite/        # tests (avec __init__.py, comme backend/tests/)
backend/scripts/vulnerabilite_*.py  # scripts d'exécution hors-ligne (acquisition, évaluation)
docs/vulnerabilite/                 # plan, fiche de données, pré-enregistrement, rapport
data/vulnerabilite/raw/             # données brutes (hors git, voir §6) + manifeste commité
```

Choix de conception qui découlent des conventions du dépôt :
- **Aucun import depuis `routers/`, `main.py`, `refresh_results.py` ni le frontend** tant que Clément n'a pas donné son accord (règle 4). Le workflow GitHub hebdomadaire `refresh-results.yml` n'est donc pas touché.
- Pour que les tests longs ne s'ajoutent pas aux 11 min 40 s de la suite actuelle (141 tests), je propose un `backend/pytest.ini` qui déclare le marqueur `slow` ; la suite par défaut les exclut (`-m "not slow"`), la suite complète les inclut.
- Réutilisation de l'existant plutôt que réécriture : `app/geo.py` + `app/data/departements_adjacency.json` pour la matrice de voisinage W, `app/stats/indicators.py` (`rolling_ac1`, `rolling_variance`, `kendall_trend`) pour les concurrents de C2, `app/stats/discrimination.py` (Fisher) si utile, `app/guardrails.py` pour valider l'ingestion.

## 3. Correspondance scripts de la note → fichiers du module

| Fichier du module | Reprend (scripts) | Notes |
|---|---|---|
| `modele.py` | `core.params_from`, `phi`, `F` ; `g1` (vérification de l'identité) | forme close Poisson ; Φ_φ = Φ/φ ; loi près du pli |
| `bruits.py` | `t9.draw` (binomiale négative) ; Poisson dans `core` ; bruit gaussien de `g2/g3` | 3 classes : simulation d'un pas, coût d'un pas, variance, dispersion |
| `observation.py` | amincissement binomial (`t7`, `t7b`, `t9.sim`) ; `g3.simulate` | `CanauxAmincis`, `CapteursAffines` |
| `estimation.py` | `core.fit`, `core.fit_fe` ; coupure de `t4c` ; fenêtres de `t5_derive.windows` | règle de coupure itérative (k ≥ 6 × niveau calme, puis seuil estimé) |
| `multicanal.py` | `t7.iv` ; `t7b.theta_hat`, `iv_drift`, `phi_multicanal` ; `t9.two_channel` | θ̂ (prop. 8), dispersion φ̂ (prop. 10), asymétrie des estimateurs croisés |
| `vstar.py` | `p1a.Vstar` (Poisson 1D) ; `g2.Vstar` (gaussien) ; `g3.two` (capteurs) | programmation dynamique sur grille ; `p1c`/réseau en phase 1b |
| `reseau.py` | `t10.grid`, `fit_net`, `run` | terme de voisinage, ŵ, étalonnage par simulation |
| `reaction.py` | `t8.decompose` | ARMA(2,1) — étiqueté EXPÉRIMENTAL |
| `incertitude.py` | `t11` partie (b) : bootstrap par unités | + bootstrap par blocs de temps (non testé dans la note) |
| `simulation.py` | `core.simulate_units`, `exit_times` ; `t6.soc` ; `t8.sim` ; `t7.sim` | simulateurs des tests |
| `garde_fous.py` | règles du cahier §3.1 et §8 | drapeaux |
| `evaluation.py` *(ajout proposé)* | `core.auc` ; τ de Kendall | AUC, tendances, comparaisons appariées pour C1–C3. Le cahier n'a pas de fichier pour ça et la phase 4 en a besoin, sans le mélanger au moteur. |

Hors v1, volontairement : `p3_filtre.py` (vraisemblance par filtre particulaire : **résultat négatif** dans la note, « l'estimateur des moments reste la référence »), `p1b`/`p1c`/`p4` (phase 1b), `p2`.

## 4. Dépendances

- NumPy 1.26.4, SciPy 1.13.1, pandas 2.2.2 sont déjà dans `backend/requirements.txt` : rien à ajouter pour le moteur.
- **SymPy 1.14.0** est déjà présent dans le venv local mais **n'est pas dans `requirements.txt`**. Il ne sert qu'à `t1_algebre` (identités symboliques) donc aux tests. Proposition : un `backend/requirements-dev.txt` (sympy), pour ne pas alourdir l'image Docker de production (`backend/Dockerfile`). Question 2.
- Pas de nouvelle dépendance pour le banc épidémies (parquet/pyarrow évité : les sources sont des CSV).

## 5. Points où le cahier et la note ne collent pas tout à fait (à trancher avant de coder)

1. **Les valeurs « attendues » viennent d'un tirage unique de la note.** Le module est une réécriture : sans reproduire les flux aléatoires des scripts, ses résultats différeront du tirage de la note par le bruit Monte-Carlo. Les tolérances du tableau §3.3 sont plausibles (j'ai recoupé chaque ligne avec les tableaux de la note : 0,58/0,61/0,60 ; 11,0/5,0 ; 11,3 ; 0,60 ; 11,5 ; 1,00/2,00 ; 0,82/1,03 ; 3,94/17,7 ; écart 0,003 → toutes dans les bornes), mais certaines sont serrées. **Étape 1.0 que je propose** : rejouer d'abord les scripts originaux, tels quels, et consigner leurs sorties dans `reproduction.md`. On saura alors si le zip reproduit bien la note, et la largeur réelle du bruit, avant de figer une tolérance.
2. **Tests très coûteux.** `t2_temps` (22 jeux × 300 trajectoires jusqu'à 150 000 pas), `t11` (b) (60 jeux × 200 bootstraps × 3 configurations), `p1a` (147 jeux, système linéaire jusqu'à ~400×400 par jeu). Je les marque `slow` et, pour les tests rapides, j'utiliserai des sous-ensembles documentés (le cahier le permet déjà pour V*).
3. **Le « niveau calme » `mlow`.** Dans `core.fit`, `mlow = nanmean(X)` : correct pour des séries simulées coupées avant l'embrasement, discutable sur des données réelles où une fenêtre contient déjà la montée. Pour les épidémies, il faut une définition explicite du niveau calme (médiane des semaines calmes, comme le suggère le point 2 du §5 du cahier). **À fixer dans le pré-enregistrement**, pas à la volée.
4. **Hypothèse « μ constant (ou effets fixes temporels) »** de la proposition 7. Le cahier prévoit comme analyse principale des effets « jour de semaine » seulement. Or une vague nationale synchrone viole μ constant, et c'est justement elle qu'on cherche. Les effets fixes temporels complets, eux, retirent la vague (le cahier le dit). Il faut décider quelle version est l'analyse principale de C1, et le décider **avant** de voir les résultats. Question 4.

## 6. Données : ce que j'ai vérifié (métadonnées data.gouv.fr uniquement, **rien téléchargé**)

| Besoin | Candidat trouvé | À vérifier à l'audit |
|---|---|---|
| Urgences + SOS Médecins par département et par jour | « Données des urgences hospitalières et de SOS médecins relatives à l'épidémie de COVID-19 », Santé publique France, jeu `5e74ecf52eb7514f2d3b8845`, licence ouverte v2 (`lov2`). Fichier `sursaud-covid-quot-dep-2025-01-01-18h00.csv`, ~20,6 Mo, dernière mise à jour 2025-01-01. Champs annoncés : passages aux urgences pour suspicion de COVID, total des passages avec diagnostic renseigné, hospitalisations, actes SOS Médecins pour suspicion de COVID, total des actes SOS avec diagnostic renseigné ; par département, sexe, classe d'âge. | Période exacte (le fichier semble figé au 1er janvier 2025) ; départements ayant les deux canaux ; **valeurs masquées ou à zéro sur petits effectifs** ; ruptures de couverture |
| Codage de l'âge | La description signale un **changement de codage le 4 novembre 2021** (`sursaud_cl_age_corona`). | Utiliser la classe « tous âges » (0) et le total des sexes évite le problème ; à confirmer. |
| Anomalies de collecte | La description renvoie à des rapports d'incohérences publiés par Etalab. | À consulter pendant l'audit. |
| Référence de R (C1) | « Indicateurs de suivi de l'épidémie de COVID-19 », Ministère des Solidarités et de la Santé, jeu `5ee9df5003284f565d561278`, `lov2`. Série quotidienne nationale et **départementale depuis le 15 mars 2020**, fichier `table-indicateurs-open-data-dep-serie.csv` (~9,6 Mo), **dernière mise à jour 2022-08-30**. | Si la colonne R est renseignée par département et sur quelles dates. Si la référence s'arrête en août 2022, **C1 ne porte que sur 2020–août 2022**. Ce R est calculé à partir des tests (SI-DEP), donc indépendant des deux canaux utilisés ; il l'est de façon utile pour C1. |
| Odissé (grippe, bronchiolite) | La recherche dans le catalogue data.gouv.fr ne ramène qu'un jeu sans rapport. Odissé a son propre portail. | Non vérifié ; reste « banc secondaire » (taux pour 100 000, pas des comptes, règle 8.8). |
| Matrice de voisinage W | Déjà dans le dépôt : `backend/app/data/departements_adjacency.json` (je n'ai pas encore regardé son contenu). | Traitement de la Corse et des codes 2A/2B ; cohérence avec les codes du fichier SPF. |
| Sentinelles | Hors v1, non regardé. | — |

**Téléchargements.** Le cahier dit qu'ils se font sur la machine de Clément. Je propose de te fournir un script (`backend/scripts/vulnerabilite_fetch.py`) qui télécharge les URL ci-dessus, enregistre la date, la taille et la somme SHA-256 dans un manifeste commité, et n'écrit jamais dans les fichiers bruts. Les CSV eux-mêmes restent hors git (`data/vulnerabilite/raw/` ajouté au `.gitignore`). Tu le lances, ou tu m'autorises à le lancer : question 7.

## 7. Risques identifiés

1. **Le nombre d'événements indépendants est probablement très petit.** Les vagues de COVID sont nationales et quasi synchrones : 96 départements × ~6–8 vagues ne font pas ~700 démarrages indépendants, mais plutôt ~6–8 événements répétés dans des unités corrélées. C2 (« plus de la moitié des démarrages », AUC) et le bootstrap par unités du cahier risquent de **surestimer** la puissance et de sous-estimer l'incertitude. Je recommande d'écrire dans le pré-enregistrement une unité d'indépendance explicite (la vague nationale) et un bootstrap par blocs de temps (que la note signale elle-même comme « non testé »). Question 3.
2. **Mauvaise spécification possible du modèle pour une épidémie.** Le modèle suppose un état calme qui ramène l'activité à `m₋` avec un flux constant d'étincelles μ. Une épidémie réelle a de la saisonnalité, des variants, de l'immunité, des interventions. La note le sait (§ réaction, interventions) ; le cahier traite les interventions en sensibilité. Il faut s'attendre à ce que `ĉ ≤ 0` (pas de seuil détecté, `garde_fous` → drapeau) soit fréquent : la table de la note le prévoit (« souvent c≈0 : c'est alors R qui compte »). C2 prévoit déjà « Φ̂ quand ĉ > 0 ».
3. **Petits effectifs en période calme.** Les comptes SOS « suspicion de COVID » d'un département un jour calme sont proches de 0. Si les petits comptes sont masqués ou arrondis, le modèle de Poisson/amincissement est faussé précisément là où il sert. L'agrégation hebdomadaire atténue sans supprimer. **À examiner en premier à l'audit.**
4. **Indépendance conditionnelle des canaux** (même patient dans les deux canaux, hypothèse 2) : traitée au cahier §4.3. Je rapporterai θ̂ et l'asymétrie sans les masquer.
5. **Intégrité du pré-enregistrement.** Pour que C1–C3 restent honnêtes, je n'ai **aucune** statistique d'évaluation à calculer sur les données réelles avant ton accord signé : pendant l'audit, je me limite à des descriptions (couverture, ruptures, valeurs manquantes, corrélation croisée des canaux pour le décalage), sans R, c, Φ, AUC ni date de démarrage de vague. Les règles (définition de démarrage, fenêtres, seuils) seront figées et commitées avec leur date avant la phase 4.
6. **Cohérence avec le site existant.** Le site a déjà une convention de limites sur chaque page de résultat (`ResultPageTemplate`, rubrique Garde-fous, Journal). Le cahier demande des intervalles, des statuts et un lien « méthode » plutôt que des paragraphes d'avertissement. Compatible avec ce qui existe tant que la page « Épidémies » suit ce choix ; à reprendre en phase 5, pas avant. Question 6.
7. **Performance de V\*.** Les scripts de la note résolvent la programmation dynamique avec des matrices G×G (G = 1500, jusqu'à 400 itérations). C'est correct mais lent : je prévois une version vectorisée avec arrêt à convergence, vérifiée contre les scripts originaux.
8. **La note n'est pas validée sur données réelles** (elle le dit : « Rien n'est encore testé sur données réelles »). Un résultat négatif en phase 4 est un résultat (règle 7).

## 8. Séquence proposée après ta validation

0. **1.0 — Rejeu des scripts originaux**, sorties consignées (`reproduction.md`, section « scripts de la note »).
1. **1.1 — Bruits, modèle, identités** (`bruits`, `modele`, tests symboliques et forme close de Φ).
2. **1.2 — Simulation + estimation** (`simulation`, `estimation`, tests 100×200, règle de coupure, chocs communs).
3. **1.3 — Multicanal** (`observation`, `multicanal`, `garde_fous`, `incertitude`).
4. **1.4 — V\* et capteurs affines** (`vstar`).
5. **1.5 — Réaction (expérimental)** et `reproduction.md` complet.
6. **Phase 2** : script de téléchargement → toi → `fiche_donnees.md` (descriptif seulement).
7. **Phase 3** : `preenregistrement.md` rédigé, validé par toi, commité avec sa date.
8. **Phase 4** : évaluation + `rapport_epidemies.md`, quel que soit le résultat.
9. **Phase 5 / 1b** : seulement sur ton accord.

Commits petits, un par sous-étape ; rien de fusionné sur `main`, rien de poussé sans ton accord ; rien de publié sur un dépôt tiers.

## 9. Questions pour Clément

1. **Emplacement.** `backend/app/vulnerabilite/` et `backend/tests/vulnerabilite/` plutôt que `helios/vulnerabilite/` (qui n'existe pas dans ce dépôt) : d'accord ? *(recommandé : oui)*
2. **SymPy.** `backend/requirements-dev.txt` séparé, ou directement dans `requirements.txt` ? *(recommandé : séparé)*
3. **Unité d'indépendance.** Acceptes-tu que le pré-enregistrement traite la **vague nationale** comme l'unité d'indépendance (bootstrap par blocs de temps, résultats donnés par vague), plutôt que le démarrage par département ? *(recommandé : oui ; sinon C2 est trop optimiste)*
4. **Effets fixes de l'analyse principale de C1.** « jour de semaine » seulement (comme dans le cahier) ou effets temporels complets ? Les deux seront rapportés, mais il faut dire lequel est le principal. *(je n'ai pas de recommandation ferme ; les deux ont un défaut, voir §5.4)*
5. **Période.** Toute la période disponible (2020 → fin du fichier), ou en excluant le début 2020 (avant que les deux canaux soient pleinement en place) ? À arrêter au vu de la fiche de données, pas avant.
6. **Page publique (phase 5).** Confirmer que « pas de paragraphes d'avertissement » n'exclut pas la rubrique « Limites » déjà présente sur toutes les pages de résultat d'Hélios. À reprendre en phase 5.
7. **Téléchargements.** Je te fournis un script que tu lances toi-même, ou tu m'autorises à lancer les trois téléchargements (≈ 30 Mo) sur cette machine ? Les fichiers resteraient hors git, avec manifeste SHA-256.
8. **Le PDF.** Si tu as une version du PDF que je peux lire (ou si le `.tex` du zip n'est pas la source exacte), dis-le-moi avant la phase 1.
