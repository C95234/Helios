/**
 * §2.1 du cahier des charges "banc d'essai IA vs statistiques" : le
 * classifieur entraîné sur les modèles simulés (nœud-col, Kuramoto),
 * appliqué aux mêmes épisodes réels déjà utilisés pour H1 (attention
 * Wikipédia). Résultat gelé par
 * backend/scripts/apply_classifier_to_real_h1.py -- chiffres réels,
 * jamais inventés, rapportés dans les deux sens honnêtement.
 */
import result from "./results/ia_vs_stats_real_h1.json";

export const IA_VS_STATS_REAL_H1 = result;

export const IA_VS_STATS_REAL_H1_NOTE =
  "Le classifieur n'a jamais vu de série réelle à l'entraînement -- seulement des trajectoires simulées de bifurcation nœud-col et de synchronisation de Kuramoto, des quantités abstraites (moyenne du réseau, paramètre d'ordre) sans rapport d'échelle avec des vues Wikipédia quotidiennes. Chaque fenêtre de 60 jours est centrée-réduite par sa PROPRE moyenne et son écart-type avant d'être présentée au réseau -- une adaptation nécessaire, documentée, qui ne garantit en rien que la forme reconnue par le classifieur sur des données simulées reste pertinente sur un signal social réel.";

export const IA_VS_STATS_REAL_H1_RESULT_NOTE =
  "Avec l'architecture CNN-LSTM adaptée de Bury et al., le résultat est plus nuancé qu'avec la première version (un simple CNN qui flaguait 91 à 100% des fenêtres partout, sans discriminer quoi que ce soit) : le taux de fenêtres flaguées varie maintenant réellement d'un épisode à l'autre, de 42,9% (confinement 2020) à 94,9% (gilets jaunes 2018). Fait notable, à interpréter avec prudence sur seulement 6 épisodes : ce taux suit approximativement le nombre de signaux sociaux déjà trouvés significatifs par H1 (nSocSig) -- le plus bas (confinement, 0 signal social significatif sur 3) donne le taux le plus faible, le plus haut (gilets jaunes, 3 signaux significatifs sur 3) donne le taux le plus élevé. Mais ce n'est PAS une preuve de capacité de détection : le test de validité sur séries AR(1) (§1.1bis, ci-dessus) montre que ce même ensemble flague à tort 78% de fenêtres sans aucune bifurcation -- le classifieur pourrait très bien réagir à \"combien la série bouge\" en général (une forme de biais de prétraitement déjà documenté) plutôt qu'à un vrai signal précurseur de bascule. Le contrôle négatif explicite de H1 (« climat social récent ») reste flagué à un taux élevé (73,2%), pas nul -- cohérent avec cette lecture prudente plutôt qu'avec une vraie discrimination.";
