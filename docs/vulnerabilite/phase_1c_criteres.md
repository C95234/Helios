# Phase 1c du banc Dansgaard-Oeschger : critère de passage, fixé AVANT d'écrire l'estimateur

**Statut : figé par commit daté (étiquette `phase1c-criteres-v1`).** Il ne change plus. Décisions de Clément du 28 octobre 2026 : lancer la phase 1c ; second capteur = carotte GRIP ;
téléchargement des fichiers publics autorisé **seulement si le critère ci-dessous est atteint** ; la branche `vulnerabilite-epidemies` reste locale.
Aucune donnée réelle n'est regardée dans cette phase.

## Ce qui est développé (hors périmètre du critère)

Un estimateur de V\* à deux capteurs affines pour une dérive **cubique** (double puits), généralisant la proposition 14 (dérive quadratique) : variables instrumentales avec les puissances de l'autre capteur,
correction des biais dus au bruit de mesure du capteur sur lequel on régresse, puis calcul de V\* depuis le puits occupé en fin de fenêtre jusqu'au point selle.

## Simulations (fixées maintenant)

Double puits dx = (x − x³ + h(t))dt + σ dW ; observation tous les 0,2 unités de temps (20 ans), 2 400 points par série (48 000 ans) ; forçage lent h(t) = 0,15·sin(2πt/120 + phase aléatoire) ; deux capteurs affines
(gains 1 et 0,7, décalages 0 et 0,3, bruit de mesure indépendant d'écart-type 25 % du signal, en unités du capteur). Deux jeux de paramètres : **σ = 0,55 et σ = 0,65**. Trente séries par jeu, graine 20261028.
Bascule : passage de l'état froid (x < −0,3) à l'état chaud (x > 0,3) ou l'inverse (hystérésis).

Fenêtres glissantes décalées de 50 points, de **100, 200 ou 400 points** (2 000, 4 000 ou 8 000 ans). Pour chaque fenêtre dont une bascule suit la fin :
V\* estimé (depuis le puits le plus proche de la moyenne des 5 derniers points), temps d'attente = temps entre la fin de la fenêtre et la bascule suivante ;
V\* vrai = 2·ΔU/σ², où ΔU est la barrière entre le puits occupé à la fin de la fenêtre et la selle, pour l'inclinaison h de cet instant.

## Critère de réussite (tous les points, pour une même taille de fenêtre et un même jeu de σ)

1. **Corrélation.** Dans au moins **90 %** des séries simulées, la corrélation de rang de Spearman entre V\* estimé et ln du temps d'attente est **≥ 0,5**.
2. **Estimabilité.** Au moins **70 %** des fenêtres donnent un V\* fini (trois points fixes réels, la selle entre les deux puits).
3. **Exactitude.** Le rapport médian V\* estimé / V\* vrai est dans **[0,5 ; 1,5]**.

Réussir pour **au moins une** des six combinaisons (taille de fenêtre × σ) suffit pour passer aux données réelles ; ce choix, plus indulgent qu'un seuil sur toutes, est assumé : il s'agit d'un filtre de faisabilité, pas d'un résultat.
Si aucune combinaison ne réussit, **on s'arrête** : le banc est déclaré non faisable avec la méthode de la note, les raisons sont documentées, aucune donnée réelle n'est téléchargée.

## Rapportés à titre de repère (pas des critères)

Corrélations de rang de l'autocorrélation d'ordre 1 et de la variance avec ln du temps d'attente, sur les mêmes fenêtres.
