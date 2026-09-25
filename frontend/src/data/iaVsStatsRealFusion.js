/**
 * §2.4 du cahier des charges "banc d'essai IA vs statistiques" : le même
 * ensemble de 10 classifieurs (§1.1, jamais ré-entraîné) appliqué à la
 * batterie curatée de 20 tirs réels MAST déjà utilisée pour le domaine
 * Fusion (routers/fusion.py). Résultat gelé par
 * backend/scripts/apply_classifier_to_real_fusion.py -- chiffres réels,
 * jamais inventés, rapportés dans les deux sens honnêtement.
 */
import result from "./results/ia_vs_stats_real_fusion.json";

export const IA_VS_STATS_REAL_FUSION = result;

export const IA_VS_STATS_REAL_FUSION_NOTE =
  "Même ensemble que pour l'extension à H1 (ci-dessus) -- jamais ré-entraîné, jamais vu de courant plasma réel à l'entraînement, seulement des trajectoires simulées de bifurcation nœud-col et de synchronisation de Kuramoto. Fenêtre de 60 points glissée (pas de 5, la même qu'à l'entraînement) sur la fenêtre pré-quench (ou pré-fin-de-tir pour un tir stable) déjà isolée par le même critère de détection de quench que le module Fusion, chaque fenêtre centrée-réduite par sa propre moyenne et son écart-type -- le courant plasma en kiloampères n'a aucun rapport d'échelle avec les quantités abstraites vues à l'entraînement.";

export const IA_VS_STATS_REAL_FUSION_RESULT_NOTE =
  "Sur le critère binaire \"au moins une fenêtre flaguée\", le résultat est sans appel et sans intérêt : les 10 tirs disruptés ET les 10 tirs stables sont tous flagués (10/10 -- 10/10), comme lors du tout premier essai sur les données réelles de H1 avant la correction d'architecture. Mais le taux de fenêtres flaguées et la probabilité moyenne, eux, ne sont pas plats -- et vont dans le sens INVERSE de celui espéré : les tirs disruptés sont flagués en moyenne à 69,7% (de 46,4% à 100% selon le tir, probabilité moyenne 0,622), tandis que les tirs stables le sont à 98,3% (de 91,3% à 100%, probabilité moyenne 0,742) -- c'est-à-dire que l'ensemble réagit PLUS fortement aux tirs qui ne disruptent jamais qu'à ceux qui disruptent réellement. Rapporté tel quel, sans explication de confort : ceci n'est pas une preuve que le classifieur \"détecte l'absence de disruption\" (aucune hypothèse de ce type n'a été testée), seulement un signal que la variabilité brute du courant plasma pendant un tir stable ressemble, pour cet ensemble, davantage à ce qu'il a appris à reconnaître comme \"proche d'une bascule\" que la variabilité d'un tir qui va réellement disrupter. Combiné au test de validité sur séries AR(1) (§1.1bis, 78% de fenêtres sans bifurcation flaguées à tort sur ce même ensemble), la lecture la plus honnête est que ce classifieur, dans cette adaptation à cette échelle, ne généralise pas de façon fiable à un signal réel de tokamak -- ni dans le bon sens ni dans le sens inverse, un résultat négatif rapporté sans l'habiller.";
