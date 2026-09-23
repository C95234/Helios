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
  "Ceci est un test de réplication comparative, pas une nouvelle méthode ni une découverte. Le classifieur est volontairement modeste (un petit CNN 1D, pas une reproduction de l'architecture de Bury et al., 2021) et entraîné uniquement sur des données synthétiques -- aucune prétention de classification du type de bifurcation sur des données réelles. Les deux sens du résultat sont rapportés sans favoriser l'un ou l'autre.";

export const IA_VS_STATS_ASYMMETRY_NOTE =
  "Le résultat n'est pas le même sur les deux modèles, et c'est justement l'intérêt d'un vrai banc d'essai plutôt que d'un chiffre unique : sur le nœud-col, le classifieur détecte aussi bien que l'indicateur classique mais beaucoup plus tôt (56 unités de temps d'avance contre 2,5). Sur Kuramoto, le classifieur -- entraîné conjointement sur les deux modèles avec un seuil de décision unique -- finit par tout signaler comme une approche de bascule (100% de détection, mais aussi 100% de fausses alertes sur les contrôles stables) : un signe que ce classifieur modeste, partagé entre deux systèmes assez différents, ne s'est pas correctement calibré pour celui-ci. L'indicateur classique, recalibré spécifiquement pour Kuramoto, reste faible mais réel (26% de détection contre 21% de fausses alertes) -- ni l'un ni l'autre ne discrimine bien ce système à partir d'une simple fenêtre brute.";
