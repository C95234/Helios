# Fiche de données : urgences, SOS Médecins et référence de R (généré par `vulnerabilite_audit_donnees.py`)

## 1. Identification

| fichier | jeu | licence | téléchargé le (UTC) | octets | sha256 (début) |
|---|---|---|---|---|---|
| sursaud-covid-quot-dep-2025-01-01-18h00.csv | Données des urgences hospitalières et de SOS médecins relatives à l'épidémie de COVID-19  | lov2 | 2026-10-17T07:11:28+00:00 | 20 587 252 | 46e94484b6d9b85b… |
| table-indicateurs-open-data-dep-serie.csv | Indicateurs de suivi de l’épidémie de COVID-19 | lov2 | 2026-10-17T07:11:29+00:00 | 9 602 359 | a8f9a8eb86f6b358… |

## 2. Urgences et SOS Médecins : structure

- Lignes : 520 352 ; départements : 101 (96 de métropole, 5 d'outre-mer : 971, 972, 973, 974, 976).
- Période (fichier entier) : **2022-12-26 → 2024-12-30** (736 jours distincts, 736 attendus : aucun jour manquant).
- Classes d'âge présentes : 0, 1, 2, 3, 4, 5, 6 (nouveau codage 0 à 6 ; le changement du 4 novembre 2021 est antérieur à la période du fichier : aucun mélange d'anciens et de nouveaux codes). Analyse sur la classe 0 (tous âges).
- Lignes « tous âges » : 74 336 = 101 départements × 736 jours ; doublons (département, date) : 0.
- Pas de temps : quotidien. Unités : comptes de personnes (passages ou actes). Aucune variable « nombre d'établissements participants » dans le fichier.

## 3. Valeurs manquantes

| champ | % de valeurs absentes (tous âges) |
|---|---|
| nbre_pass_corona | 0.3 |
| nbre_pass_tot | 0.3 |
| nbre_hospit_corona | 0.3 |
| nbre_acte_corona | 54.8 |
| nbre_acte_tot | 54.8 |

## 4. Couverture du canal SOS Médecins

- Départements ayant des données SOS Médecins (au moins un jour) : **46 sur 101** (45 de métropole).
- Dont couverture complète sur les 736 jours : **37** ; couverture partielle : 9.
- Les deux canaux (urgences et SOS) sont donc disponibles dans **46 départements au plus** (37 à couverture complète), contre ~96 visés par le cahier ; le seuil de 30 unités du bootstrap est respecté avec la couverture complète.
- Départements avec les deux canaux, couverture complète : 02, 06, 10, 13, 14, 17, 18, 21, 25, 29, 33, 34, 35, 38, 42, 44, 45, 50, 54, 56, 59, 63, 64, 66, 67, 68, 69, 73, 74, 75, 76, 78, 80, 83, 87, 89, 91.

Couverture partielle :

| dep | premier jour | dernier jour | jours renseignés |
|---|---|---|---|
| 2A | 2022-12-26 | 2024-12-30 | 733 |
| 30 | 2022-12-26 | 2024-12-30 | 735 |
| 31 | 2022-12-26 | 2024-12-30 | 732 |
| 40 | 2023-03-05 | 2024-12-30 | 667 |
| 51 | 2022-12-26 | 2024-12-30 | 730 |
| 60 | 2022-12-26 | 2024-12-30 | 735 |
| 77 | 2022-12-26 | 2024-12-30 | 735 |
| 95 | 2022-12-26 | 2024-07-12 | 565 |
| 972 | 2022-12-26 | 2024-12-29 | 733 |

- Sans aucun SOS Médecins (55) : 01, 03, 04, 05, 07, 08, 09, 11, 12, 15, 16, 19, 22, 23, 24, 26, 27, 28, 2B, 32, 36, 37, 39, 41, 43, 46, 47, 48, 49, 52, 53, 55, 57, 58, 61, 62, 65, 70, 71, 72, 79, 81, 82, 84, 85, 86, 88, 90, 92, 93, 94, 971, 973, 974, 976.

## 5. Petits effectifs (départements avec les deux canaux, couverture complète)

| compte hebdomadaire | n (dép.-semaines) | % de zéros | D1 | Q1 | médiane | Q3 | D9 | max |
|---|---|---|---|---|---|---|---|---|
| nbre_pass_corona | 3885 | 1.7% | 3 | 8 | 17 | 34 | 57 | 286 |
| nbre_acte_corona | 3885 | 2.7% | 3 | 7 | 19 | 45 | 90 | 628 |
| nbre_pass_tot | 3885 | 0.0% | 2362 | 2953 | 4042 | 5948 | 10193 | 17336 |
| nbre_acte_tot | 3885 | 0.0% | 730 | 951 | 1331 | 2697 | 4388 | 9080 |

Répartition des valeurs quotidiennes basses (un déficit anormal des valeurs 1 à 4 trahirait un masquage des petits effectifs) :

| valeur quotidienne | nbre_pass_corona | nbre_acte_corona |
|---|---|---|
| 0 | 5629 | 6137 |
| 1 | 4863 | 4356 |
| 2 | 3823 | 3150 |
| 3 | 2985 | 2287 |
| 4 | 2195 | 1906 |
| 5 | 1724 | 1441 |
| 6 | 1320 | 1142 |

## 6. Incohérences et anomalies

- Lignes « tous âges » où les comptes COVID dépassent le total : urgences 0, SOS 0.
- Somme hommes + femmes ≠ total (urgences COVID) : 9 lignes sur 74121 renseignées.
- Somme hommes + femmes ≠ total (urgences totales) : 2702 lignes sur 74121.
- Somme des classes d'âge 1 à 6 ≠ classe 0 (urgences COVID) : 5 lignes sur 74121 (le fichier signale des âges non identifiés).
- Valeurs négatives : 0.

## 7. Ruptures de série

Règle descriptive : pour chaque département, médiane mensuelle du total (urgences : `nbre_pass_tot` ; SOS : `nbre_acte_tot`) ; rupture si la médiane du mois est > 2 fois ou < 0,5 fois celle du mois précédent (mois précédent ≥ 10).

- urgences : 1 rupture(s) mensuelle(s) sur 101 départements × 24 transitions.

| département | mois | médiane mois précédent | médiane du mois |
|---|---|---|---|
| 976 | 2024-05 | 76 | 37 |

- urgences : départements avec au moins 7 jours consécutifs sans donnée ou à zéro (total) : 4 (48, 971, 972, 976).

- SOS Médecins : 1 rupture(s) mensuelle(s) sur 46 départements × 24 transitions.

| département | mois | médiane mois précédent | médiane du mois |
|---|---|---|---|
| 95 | 2024-07 | 370 | 33 |

- SOS Médecins : départements avec au moins 7 jours consécutifs sans donnée ou à zéro (total) : 2 (40, 95).

## 8. Décalage temporel entre les deux canaux (corrélation croisée)

Comptes COVID nationaux sur les 37 départements à couverture complète, moyenne mobile centrée sur 7 jours. Corrélation à décalage 0 : 0.921. Meilleur décalage : **+4 jour(s)** (corrélation 0.936) ; un décalage positif signifie que SOS Médecins précède les urgences.

Évolution mensuelle des comptes COVID (somme sur ces départements), à titre descriptif :

| mois | urgences COVID | actes SOS COVID |
|---|---|---|
| 2022-12 | 2024 | 1255 |
| 2023-01 | 2987 | 2800 |
| 2023-02 | 2028 | 2143 |
| 2023-03 | 4534 | 4836 |
| 2023-04 | 5075 | 6263 |
| 2023-05 | 3077 | 4681 |
| 2023-06 | 1366 | 2084 |
| 2023-07 | 1273 | 2405 |
| 2023-08 | 4876 | 9310 |
| 2023-09 | 8936 | 17577 |
| 2023-10 | 8030 | 13537 |
| 2023-11 | 7109 | 10227 |
| 2023-12 | 12299 | 15163 |
| 2024-01 | 4509 | 4816 |
| 2024-02 | 1446 | 1509 |
| 2024-03 | 669 | 844 |
| 2024-04 | 536 | 836 |
| 2024-05 | 1112 | 2095 |
| 2024-06 | 3890 | 7598 |
| 2024-07 | 4715 | 8421 |
| 2024-08 | 4029 | 5202 |
| 2024-09 | 6158 | 10282 |
| 2024-10 | 5140 | 6655 |
| 2024-11 | 1923 | 2860 |
| 2024-12 | 2044 | 2286 |

## 9. Référence de R (indicateurs de suivi, ministère de la Santé)

- Période du fichier : 2020-03-18 → 2022-08-29 ; 101 départements ; R renseigné pour 12.0% des lignes, du **2020-06-15 au 2022-08-16**.

| annee | lignes | % R renseigné |
|---|---|---|
| 2020 | 29189 | 16.9 |
| 2021 | 36865 | 11.5 |
| 2022 | 24341 | 6.6 |

- **Chevauchement avec la période urgences/SOS (2022-12-26 → 2024-12-30) : AUCUN.** Dernier R publié : 2022-08-16 ; premier jour des urgences/SOS : 2022-12-26 (écart de 132 jours).
- Le R du fichier est celui des indicateurs de suivi, calculé à partir des tests (SI-DEP) : indépendant des deux canaux, mais sans recouvrement ici.

## 10. Codes de départements et matrice de voisinage

- Matrice de voisinage du dépôt : 96 départements (IGN Admin Express COG 2018, via gregoiredavid/france-geojson (Licence Ouverte)).
- Départements du fichier de métropole absents de la matrice : aucun ; départements de la matrice absents du fichier : aucun.
- Parmi les 46 départements avec SOS Médecins, ceux de la matrice : 45.

## 11. Constats et conséquences pour le pré-enregistrement (rédigés à la main ; le reste du document est généré)

Aucune grandeur du modèle (R, c, Φ, V\*, AUC, date de démarrage de vague) n'a été calculée sur ces données. Les comptes mensuels du §8 sont
descriptifs ; ils servent seulement à juger de la faisabilité.

1. **C1 n'est pas calculable avec la référence publiée.** Le R des indicateurs de suivi s'arrête au 16 août 2022 (fichier au 29 août 2022) ; les
   urgences et SOS Médecins commencent le 26 décembre 2022. Aucun jour en commun (132 jours d'écart). Le jeu officiel n'expose qu'un seul fichier
   départemental, couvrant les deux dernières années ; je n'ai trouvé aucune version plus ancienne officielle (les ressources communautaires de 2020
   sont des dépôts tiers, que je n'ai pas utilisés). **Décision à prendre avant le pré-enregistrement** :
   - (a) chercher des données départementales d'urgences et de SOS Médecins pour 2020-2022 auprès de Santé publique France ;
   - (b) retenir une autre référence indépendante sur 2023-2024 (par exemple hospitalisations ou eaux usées ; sources non vérifiées par moi). Ce ne
     serait pas un R : C1 changerait de nature ;
   - (c) abandonner C1 et le dire, ou le remplacer par un critère de cohérence interne entre les deux canaux.
   La règle d'interprétation fixée par Clément (analyse principale sans effets temporels, sensibilité avec effets temporels complets) reste valable telle
   quelle dès qu'une référence existe.
2. **Très peu de vagues indépendantes.** À la lecture des comptes mensuels, on distingue environ 3 à 5 épisodes nationaux entre décembre 2022 et
   décembre 2024 (mars-avril 2023 ; août à décembre 2023 avec deux sommets ; juin à octobre 2024). Avec la vague nationale comme unité
   d'indépendance (décision validée), C2 (« plus de la moitié des démarrages ») repose sur ce petit nombre : à 4 vagues, même 4 succès sur 4 donnent
   p = 1/16 ≈ 0,06 au test de signe, donc **jamais significatif à 5 %** ; il faudrait 5 vagues au moins (p = 1/32 ≈ 0,03). L'AUC fenêtres
   pré-démarrage / témoins aurait un intervalle très large. À décider : accepter que C2 soit essentiellement descriptif sur ce banc, ou
   obtenir 2020-2022 (une dizaine de vagues supplémentaires).
3. **37 départements, pas 96, et pas au hasard.** SOS Médecins n'existe que dans 46 départements (45 de métropole), 37 avec couverture complète. Le seuil de 30
   unités du bootstrap est respecté, de peu. Les départements couverts correspondent à l'implantation des associations SOS Médecins (probablement urbains) : les
   résultats ne représentent pas la France entière.
4. **Petits effectifs : pas de masquage détecté.** Les valeurs quotidiennes 1 à 6 décroissent régulièrement (§5) : aucun déficit des petits comptes. Comptes
   hebdomadaires COVID médians : 17 (urgences) et 19 (SOS), premier décile 3, 1,7 % et 2,7 % de semaines à zéro. L'hypothèse de Poisson reste plausible, mais le
   niveau calme est bas (m₋ de l'ordre de quelques unités par semaine), régime où la note signale un plancher d'estimation.
5. **Décalage entre canaux : SOS Médecins précède les urgences d'environ 4 jours** (corrélation croisée 0,936 à +4 jours contre 0,921 à 0). Au pas hebdomadaire, c'est
   une demi-période. À décider dans le pré-enregistrement : décaler ou non SOS avant l'agrégation hebdomadaire (le décalage ayant été mesuré ici sur les
   comptes nationaux, il ne dépend d'aucun critère d'évaluation).
6. **Ruptures et trous : peu.** Une rupture mensuelle côté urgences (976, mai 2024) et une côté SOS (95, juillet 2024, la série s'arrête le 12 juillet) ; les départements
   à couverture complète n'ont aucun trou de 7 jours. Le fichier ne contient pas le nombre d'établissements participants : les ruptures de participation ne sont
   détectables qu'indirectement (niveau des totaux).
7. **Incohérences négligeables pour l'usage prévu** : aucun compte COVID supérieur au total ; 9 lignes où hommes + femmes ≠ total COVID ; 5 lignes où la somme des classes
   d'âge ≠ tous âges. 2 702 lignes (3,6 %) où hommes + femmes ≠ total des urgences, sans effet : on utilise les totaux tous âges, tous sexes.
8. **Mesures nationales.** Sur décembre 2022-décembre 2024, aucune mesure sanitaire nationale majeure (confinement, couvre-feu) n'est à exclure ; la table datée demandée ne
   sert que si 2020-2022 est ajouté. Je ne l'ai pas constituée (sources non établies).
9. **Contrôles de calendrier.** Les jours fériés se calculent par règle (pas de fichier à télécharger). Les vacances scolaires par zone demandent un fichier officiel
   (calendrier de l'Éducation nationale) que je n'ai pas téléchargé : à autoriser séparément.
10. **Format.** Valeurs entières non négatives (comptes), classes d'âge : on prend la classe 0. Compatible avec `estimer_vulnerabilite` après un simple renommage
    des colonnes (`dep` → `unite`, `date_de_passage` → `date`, un canal par `source`).
