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
  "Ceci est un test de réplication comparative, pas une nouvelle méthode ni une découverte. Le classifieur est volontairement modeste (un petit CNN 1D, pas une reproduction de l'architecture de Bury et al., 2021) et entraîné uniquement sur des données synthétiques -- aucune prétention de classification du type de bifurcation sur des données réelles. Les deux sens du résultat sont rapportés sans favoriser l'un ou l'autre. Le classifieur est ré-entraîné plusieurs fois indépendamment (§1.1) pour rapporter sa variabilité, jamais un seul chiffre présenté comme définitif -- même exigence que celle qui a révélé un test fragile dans la contribution ewstools (Journal §8).";

export const IA_VS_STATS_ASYMMETRY_NOTE =
  "Le résultat n'est pas le même sur les deux modèles, et c'est justement l'intérêt d'un vrai banc d'essai plutôt que d'un chiffre unique. Sur le nœud-col, le classifieur détecte 100% des bascules réelles sur les 5 entraînements (écart-type nul), avec zéro faux positif -- contre 93,3% de détection mais 86,7% de faux positifs pour l'indicateur classique complet. Cet écart de faux positifs est plus marqué qu'avant la correction de rigueur, et une part importante en est probablement un artefact de calibration plutôt qu'un vrai écart de robustesse : le filtre de persistance (6 fenêtres glissantes consécutives requises) avait été calibré pour l'ancien détecteur à seuil simple, pas pour le nouveau test de significativité complet (variance et AC1, testées par données de substitution), qui déclenche plus souvent par fenêtre isolée sans un nouveau balayage de calibration -- signalé explicitement comme limite ouverte ci-dessous, pas corrigé silencieusement faute de budget de calcul pour un second balayage complet. Sur Kuramoto, les deux méthodes détectent 100% des vraies synchronisations mais flaguent aussi 100% des contrôles stables : ni l'une ni l'autre ne discrimine ce système à partir d'une simple fenêtre brute, avec ou sans la correction de rigueur -- un résultat qui, lui, tient.";
