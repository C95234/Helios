/**
 * §2.3 du cahier des charges "banc d'essai IA vs statistiques" : un
 * classifieur a DOUBLE ENTREE (fenêtre temporelle + instantané spatial,
 * `backend/app/h3_ml.py`) entraîné à détecter une anomalie JOINTE
 * (les deux signaux anormaux en même temps) près d'une bascule réelle
 * simulée sur le réseau réel des départements -- comparé à une baseline
 * classique (tendance + Moran), puis appliqué aux 6 phénomènes réels déjà
 * testés par H3 (`stats/h3_joint.py`). Résultat gelé par
 * backend/scripts/train_and_apply_joint_classifier.py -- chiffres réels,
 * jamais inventés.
 */
import result from "./results/ia_vs_stats_real_h3.json";

export const IA_VS_STATS_REAL_H3 = result;

export const IA_VS_STATS_REAL_H3_NOTE =
  "H3 pose une question à ENTRÉE DOUBLE, propre à ce cas : les deux signaux (tendance temporelle nationale, indice de Moran spatial départemental) sont-ils anormaux EN MÊME TEMPS ? Le classifieur comparable ici a donc deux branches -- une temporelle (convolution + LSTM, plus légère que le CNN-LSTM de §1.1 puisqu'elle ne reproduit pas Bury et al., qui ne traite qu'un seul flux) et une spatiale (la même convolution de graphe que §2.2, réseau réel uniquement) -- fusionnées avant la décision finale. Les deux canaux proviennent TOUJOURS de la même trajectoire simulée (moyenne du réseau et instantané par nœud au même instant), jamais appairés artificiellement.";

export const IA_VS_STATS_REAL_H3_RESULT_NOTE =
  "Sur la tâche de détection elle-même (paires simulées, jamais vues à l'entraînement) : le classifieur double-entrée obtient 99,2% de bonnes réponses en ensemble (98,9% ± 0,5% individuellement, 10 entraînements), largement au-dessus de la baseline classique (tendance + Moran combinés simplement) à 84,0% -- un avantage net et cohérent, cette fois en faveur du classifieur. Appliqué aux 6 phénomènes réels déjà testés par H3 : les deux méthodes s'accordent -- aucun des 6 phénomènes n'est signalé comme \"anomalie jointe\" ni par le classifieur (probabilités toutes sous 6,1%, loin du seuil de 50%) ni par la baseline classique. Ce résultat négatif concorde avec le verdict déjà publié de H3 sur données réelles (majoritairement non concluant) -- mais la conclusion honnête reste la même que pour les autres extensions : un classifieur qui excelle sur une tâche simulée peut très bien ne rien détecter du tout sur des données réelles à une échelle et une source complètement différentes, ce n'est ni une confirmation ni une réfutation de H3 elle-même.";
