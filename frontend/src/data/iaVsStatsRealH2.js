/**
 * §2.2 du cahier des charges "banc d'essai IA vs statistiques" : un
 * classifieur spatial (convolution de graphe, `backend/app/spatial_ml.py`)
 * entraine a distinguer un instantane genere sur le RESEAU REEL des
 * departements d'un instantane genere sur une GRILLE DE CONTROLE de meme
 * taille -- comparé a l'indice de Moran (§5.2) sur la MEME tache, puis
 * appliqué à la vraie série de chômage départemental déjà utilisée par H2.
 * Résultat gelé par backend/scripts/train_and_apply_spatial_classifier.py
 * -- chiffres réels, jamais inventés.
 */
import result from "./results/ia_vs_stats_real_h2.json";

export const IA_VS_STATS_REAL_H2 = result;

export const IA_VS_STATS_REAL_H2_NOTE =
  "Contrairement au CNN-LSTM temporel (§1.1, une adaptation fidèle de Bury et al.), il n'existe pas d'architecture publiée pour ce problème précis : la donnée est une carte de territoires, pas une série temporelle. Faute de coordonnées géographiques disponibles pour les départements (seule l'adjacence est connue), l'architecture retenue est un réseau de convolution de GRAPHE (deux branches, une par topologie candidate, appliquées au même instantané brut centré par sa propre moyenne) plutôt qu'un CNN 2D sur une carte rasterisée -- l'analogue neuronal, à poids appris, de calculer l'indice de Moran une fois avec chaque topologie sur le même instantané, exactement ce que fait déjà le test statistique existant.";

export const IA_VS_STATS_REAL_H2_RESULT_NOTE =
  "Sur la tâche de discrimination elle-même (instantanés simulés d'une bifurcation nœud-col couplée sur le réseau réel ou sur la grille de contrôle, jamais vus à l'entraînement) : l'indice de Moran, sans aucun paramètre appris, atteint 90,5% de bonnes réponses -- l'ensemble des 10 classifieurs spatiaux fait moins bien, 84,1% en ensemble (83,6% ± 0,7% individuellement) -- un résultat net en faveur de la méthode statistique classique sur cette tâche. Appliqué à la vraie série de chômage départemental (106 trimestres, 2000 à 2026) : le classifieur reconnaît 77,4% des trimestres réels comme \"réseau réel\" (probabilité moyenne 0,69), contre 99,1% pour la règle de Moran -- puisque ces données proviennent authentiquement du réseau réel, la règle de Moran est donc presque toujours correcte tandis que le classifieur se trompe sur près d'un quart des trimestres. Les deux résultats vont dans le même sens : sur cette tâche précise, l'indice de Moran discrimine mieux la topologie réelle qu'un classifieur de graphe entraîné sur des données simulées -- rapporté tel quel, sans habillage, comme le prévoit le cadrage du banc d'essai (\"l'IA peut très bien perdre la comparaison\").";
