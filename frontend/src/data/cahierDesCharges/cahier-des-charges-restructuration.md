# Cahier des charges — Restructuration du site Hélios

*Document destiné à être fourni tel quel comme brief à Claude Code pour
la phase de restructuration, avant toute reprise du travail de recherche
(H5).*

---

## 1. Constat

Le site a été construit module par module, au fil des besoins successifs
(H1 → H2 → H3 → H4 → Journal de recherche → Conclusions), sans jamais
revenir sur la navigation d'ensemble. Résultat : une architecture de
l'information qui reflète l'ordre de développement plutôt que les besoins
du lecteur, avec des contenus dupliqués (démonstrations mathématiques
présentes à la fois dans les pages Résultats et dans une page Méthode
partielle) et une page "Conclusions" qui mélange résultats détaillés et
synthèse de projet.

## 2. Objectif

Réorganiser l'information autour de **7 sections stables**, identiques
sur toutes les pages, plutôt qu'une navigation redéfinie page par page :

1. **Accueil**
2. **Comprendre** — la démonstration pédagogique, sans donnée réelle
3. **Résultats** — une page par hypothèse (H1, H2, H3, H4, et futures)
4. **Méthode** — tout ce qui est mathématique : cours, démonstrations,
   bibliographie
5. **Journal de recherche** — le récit chronologique de la recherche, y
   compris les erreurs corrigées
6. **Bilan** — la synthèse honnête du projet (points forts / points
   faibles), pas les résultats détaillés
7. **Le roman** — le contexte narratif, séparé de tout contenu
   scientifique

## 3. Règle de non-duplication

Une information donnée ne vit qu'à **un seul endroit**. Toute autre page
qui en a besoin y renvoie par un lien, jamais en la recopiant. En
particulier : les démonstrations mathématiques ne vivent que dans
**Méthode** ; aucune page Résultats ne doit reproduire une démonstration
complète, seulement un renvoi contextuel bref si nécessaire.

## 4. Gabarit obligatoire pour toute page Résultats (H1 à H4, et futures H5+)

Chaque page Résultats doit suivre, dans cet ordre, la structure
suivante :

1. **Bannière de verdict** : confirmée / infirmée / non concluante --
   ou "non testée empiriquement" pour les hypothèses de type simulation
   (H4). Le nombre d'épisodes testés doit toujours être visible dans la
   bannière, jamais caché plus bas dans la page.
2. **Résumé en une phrase**, simplifié, sans jargon.
3. **Le postulat d'origine** : ce que l'hypothèse affirmait avant test.
4. **Le résultat obtenu** : ce qui a été trouvé, avec un lien vers la
   démonstration complète dans Méthode -- jamais la démonstration
   elle-même reproduite ici.
5. **Les limites**, explicites : taille d'échantillon, proxy imparfait,
   etc.
6. **Un lien vers le passage correspondant du Journal de recherche.**

Ce gabarit est un **plancher**, pas un plafond : une page peut garder son
outil interactif existant en plus, mais jamais à la place de ces six
éléments.

## 5. Plan de migration (6 étapes)

1. Squelette de navigation à 7 sections, identique sur toutes les pages,
   généré une seule fois (pas redéfini page par page).
2. Migration de H1 à H4 dans le nouveau gabarit.
3. Extraction du contenu Méthode (cours, démonstrations, bibliographie)
   dans sa propre section, avec renvoi depuis les pages Résultats plutôt
   que duplication.
4. Audit CSS : une seule source de tokens de design (couleurs, polices,
   espacements), aucune redéfinition locale par page.
5. Nouveau Bilan : synthèse honnête, séparée des résultats détaillés.
6. Migration des pages restantes (Comprendre, Le roman, pages
   secondaires) et redirections depuis toutes les anciennes URLs.

## 6. Audit final de non-duplication

Avant de considérer la restructuration terminée : vérifier qu'aucun texte
de démonstration mathématique, ni aucune donnée chiffrée, n'apparaît
identique à deux endroits du site. Toute page qui a besoin d'une
information déjà présentée ailleurs doit y renvoyer par un lien.

---

*Voir aussi le [cahier des charges produit](/dev/cahier-des-charges) pour
le positionnement général du projet, les hypothèses testées et les
garde-fous éthiques.*
