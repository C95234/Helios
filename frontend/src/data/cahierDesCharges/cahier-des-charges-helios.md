# Cahier des charges — Hélios
## Plateforme de détection et de test de signaux précurseurs de bascules collectives

---

## 1. Positionnement

**Ce que c'est** : un outil de recherche et de vulgarisation qui calcule,
sur des séries temporelles et des réseaux territoriaux réels, les
indicateurs statistiques de "ralentissement critique" qui précèdent
généralement une rupture ou un changement d'état d'un système complexe —
méthode issue de la littérature sur les transitions critiques (écologie,
épidémiologie, sociophysique) — puis teste trois hypothèses de recherche
originales sur des données réelles et en tire une conclusion honnête.

**Ce que ce n'est pas** : un outil d'identification, de profilage ou de
surveillance de personnes. Le produit travaille exclusivement sur des
**données agrégées** (comptages, indices, séries officielles), jamais sur
des données nominatives individuelles.

**Origine et ambition** : le projet est inspiré d'un roman dans lequel
deux chercheurs, Moussa et Louise, construisent un outil pour détecter
des signes de bascule sociale avant qu'ils ne deviennent visibles.

---

## 5.5 Les trois hypothèses à tester

**H1 — Décalage temporel** : les indicateurs précurseurs calculés sur les
signaux sociaux se déclenchent statistiquement avant ceux calculés sur
les statistiques officielles, pour un même événement de rupture
territoriale réel.

**H2 — Robustesse sur réseau réel** : l'indice de Moran se comporte
différemment sur le réseau réel (tailles et topologie hétérogènes) que
sur une grille régulière de contrôle de même taille.

**H3 — Indicateur joint** : combiner une tendance temporelle
significative ET une tendance spatiale significative réduit les faux
positifs par rapport à chaque indicateur pris isolément.

## 5.8 H4 — Contrôle actif de la synchronisation (inspiré du RCA)

Nature différente des trois premières hypothèses : H1-H3 sont des
hypothèses empiriques, testées contre des données réelles. H4 n'est pas
testable de la même façon — c'est une démonstration de principe en
simulation, jamais présentée avec le même statut de preuve que H1-H3.

---

## 7. Module de test des hypothèses

Sortie du module, pour chaque hypothèse (H1, H2, H3) : un verdict
(confirmée / infirmée / non concluante), jamais formulé de façon plus
catégorique que ne le permet le test statistique. Le module indique
systématiquement le nombre d'épisodes indépendants testés. En dessous de
5 épisodes, mention automatique "résultat préliminaire".

## 7bis. Module "Journal de recherche"

Tout ce qui a été établi mathématiquement pendant la conception du projet
doit être visible et lisible dans le logiciel lui-même — y compris
l'erreur corrigée, qui doit rester visible plutôt qu'être effacée.

---

## 9. Garde-fous techniques et éthiques

1. Refus structurel des données nominatives.
2. Anonymisation par défaut (k-anonymat ≥ 20).
3. Conformité des connecteurs — aucune source sans accès conforme à ses
   propres conditions d'utilisation.
4. Rate limiting sur l'API.
5. Chiffrement en transit et au repos.
6. Journalisation d'audit sans contenu de données.
7. Validation stricte des entrées.
8. Prudence statistique obligatoire.

---

*Document de référence — voir aussi le cahier des charges de
restructuration du site, plus récent, pour l'architecture de
l'information actuelle.*
