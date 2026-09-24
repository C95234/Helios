/**
 * Banc d'essai comparatif : indicateurs statistiques classiques vs un
 * classifieur de deep learning -- cahier des charges, suite ewstools §3bis.
 * Résultat gelé par backend/scripts/train_and_compare_classifier.py --
 * mêmes conventions que les autres résultats (chiffres réels, jamais
 * inventés). Test de réplication comparative, jamais une nouvelle méthode.
 */
import result from "./results/ia_vs_stats.json";

export const IA_VS_STATS_RESULT = result;

export const IA_VS_STATS_METHOD_NOTE =
  "Les deux modèles déjà construits pour Hélios (bifurcation nœud-col, §5.6quater ; synchronisation de Kuramoto, §5.8) sont réutilisés, à échelle réduite pour générer les milliers de fenêtres nécessaires à l'entraînement -- mêmes équations, mêmes fonctions, seuls les paramètres d'échelle (taille du réseau, durée) changent, dans le même esprit d'adaptation documentée que le reste du projet.";

export const IA_VS_STATS_GUARDRAIL =
  "Ceci est un test de réplication comparative, pas une nouvelle méthode ni une découverte. L'architecture (CNN-LSTM) est adaptée de Bury et al. (2021) -- code source publié, lu directement -- mais à une échelle d'entraînement très réduite par rapport à la leur (voir /methode/cnn-deep-learning) et entraînée uniquement sur des données synthétiques -- aucune prétention de classification du type de bifurcation sur des données réelles, ni de comparaison de performance avec leurs résultats publiés (tâche différente : bascule oui/non sur 2 modèles, pas le type de bifurcation sur un grand nombre de modèles génériques). Les deux sens du résultat sont rapportés sans favoriser l'un ou l'autre. Le classifieur est ré-entraîné en ensemble de 10 modèles indépendants (§1.1, la méthode de robustesse de Bury et al. eux-mêmes) pour rapporter sa variabilité, jamais un seul chiffre présenté comme définitif -- même exigence que celle qui a révélé un test fragile dans la contribution ewstools (Journal §8).";

export const IA_VS_STATS_ASYMMETRY_NOTE =
  "Le résultat n'est pas le même sur les deux modèles, et c'est justement l'intérêt d'un vrai banc d'essai plutôt que d'un chiffre unique. Sur le nœud-col, le classifieur (architecture CNN-LSTM adaptée de Bury et al.) détecte 100% des bascules réelles sur les 10 entraînements (écart-type nul), avec zéro faux positif -- contre 93,3% de détection mais 86,7% de faux positifs pour l'indicateur classique complet. Cet écart de faux positifs de l'indicateur classique est en partie imputable à un filtre de persistance calibré pour un détecteur plus ancien, pas pour le test de significativité complet actuel -- signalé comme limite ouverte ci-dessous. Sur Kuramoto, les deux méthodes détectent 100% des vraies synchronisations, mais le classifieur flague aussi en moyenne 93,9% des contrôles stables (écart-type 11,8% -- la seule métrique où les 10 entraînements divergent notablement, de 61,5% à 100% selon la graine) contre 100% pour l'indicateur classique : ni l'un ni l'autre ne discrimine ce système à partir d'une simple fenêtre brute. Le test de validité sur séries AR(1) stationnaires (§1.1bis, ci-dessous) confirme d'ailleurs directement pourquoi : le classifieur reproduit le biais de prétraitement documenté par Dablander & Bury (2021), flaguant à tort des séries sans aucune bifurcation.";
