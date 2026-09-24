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
  "Résultat net et sans ambiguïté, dans le sens que le cahier des charges envisageait explicitement comme possible : le classifieur ne discrimine RIEN sur ces données réelles. Il flague 91 à 100% des fenêtres sur les 6 épisodes -- y compris « Climat social récent », le contrôle négatif explicite de H1 où aucun signal n'est attendu (100% flaguées), et à un taux quasi identique entre le seul cas favorable à H1 (attentats de 2015, 100%) et les cas défavorables (jusqu'à 100% aussi). Un classifieur qui répond presque toujours « oui » n'apporte aucune information : la différence de domaine (dynamique simulée lisse et continue vs vues quotidiennes réelles, bruitées et à sauts) est totale, et aucune adaptation de normalisation par fenêtre ne suffit à la combler. Ce résultat confirme que le problème vient des données -- le classifieur n'a simplement rien appris qui généralise à un signal social réel -- pas de la méthode de deep learning elle-même, ni de l'indicateur statistique classique (qui, lui, reste interprétable et déjà testé séparément sur ces mêmes données pour H1).";
