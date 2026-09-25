/**
 * Modules des domaines Fusion nucléaire et Mémoire collective -- même
 * forme que HYPOTHESES (data/hypotheses.js) pour être rendus par le
 * même composant HypothesisCard, sans dupliquer le rendu (cahier des
 * charges visibilité/accroches §2-3).
 *
 * §0.1 : chaque `simple`/`expert` s'ouvre sur la question PROPRE au
 * module, jamais sur une référence à un autre domaine -- le partage de
 * moteur statistique est mentionné ensuite, comme un fait secondaire,
 * jamais comme la phrase d'ouverture.
 */

export const FUSION_DOMAIN_MODULES = [
  {
    code: "Fusion",
    catchyTitle: "La même méthode, un tout autre monde",
    title: "Détection sur données de tokamak",
    simple: "Avant qu'un plasma de fusion ne perde son confinement, y a-t-il des signes avant-coureurs mesurables ?",
    expert:
      "Une disruption de plasma (perte brutale de confinement) est-elle précédée d'un signal détectable dans le courant et le réseau de sondes magnétiques d'un tokamak réel (MAST) ? Le même moteur statistique que celui construit pour le domaine Société (variance/AC1 glissantes, indice de Moran, test par données de substitution) est réutilisé ici sans modification -- une preuve que la méthode généralise, pas un emprunt.",
    status: "testable-batterie",
    statusNote:
      "Testé sur une batterie curatée de 20 tirs réels MAST (10 disruptés, 10 stables) -- détection uniquement, jamais de conception de système de contrôle réel.",
    link: { to: "/resultats/fusion", label: "Voir le résultat" },
  },
  {
    code: "Plasma",
    catchyTitle: "Le seuil où le feu s'auto-entretient",
    title: "Modèle de bilan de puissance",
    simple: "À quel moment précis un plasma de fusion s'embrase-t-il tout seul ?",
    expert:
      "Un modèle réduit mais réel de physique des plasmas (bilan de puissance à zéro dimension, critère de Lawson) permet-il de détecter, statistiquement, l'approche du seuil d'ignition avant qu'il ne soit franchi ? Même moteur statistique que le reste du projet, appliqué cette fois à une température simulée par une vraie équation physique -- pas une donnée mesurée, pas une analogie sociale.",
    status: "simulation",
    statusNote:
      "Modèle réduit illustratif (pas une simulation de réacteur complet) -- démonstration de principe sur une vraie bifurcation physique, jamais une donnée mesurée.",
    link: { to: "/resultats/plasma-modele", label: "Voir le résultat" },
  },
];

/** Banc d'essai transversal (suite ewstools §3bis) -- n'appartient à aucun
 * domaine, jamais combiné à un verdict de domaine. */
export const BANC_ESSAI_MODULES = [
  {
    code: "IA",
    catchyTitle: "Un signal précurseur se voit-il aussi bien à l'œil qu'appris par une machine ?",
    title: "Indicateurs statistiques vs deep learning",
    simple:
      "Sur les mêmes fenêtres de série brute, un classifieur entraîné détecte-t-il l'approche d'une bascule mieux qu'un indicateur statistique classique -- ou est-ce l'inverse ?",
    expert:
      "Comparaison, sur les deux modèles de bifurcation déjà construits pour Hélios (nœud-col, Kuramoto), d'un classifieur CNN-LSTM (architecture adaptée de Bury et al., 2021, ensemble de 10 modèles indépendants) face à l'indicateur statistique COMPLET de H1 (variance et AC1, tau de Kendall, test par données de substitution) -- taux de détection, délai d'anticipation, faux positifs, plus un test de validité sur séries AR(1) stationnaires.",
    status: "comparatif",
    statusNote: "Résultat asymétrique sur les modèles simulés : sur le nœud-col, le classifieur (CNN-LSTM, 10 modèles) détecte 100% des bascules réelles sans aucun faux positif, contre 93% de détection et un taux de faux positifs élevé pour l'indicateur classique -- écart en partie imputable à un filtre de persistance pas encore recalibré (limite signalée). Sur Kuramoto, aucun des deux ne discrimine bien les vraies synchronisations des contrôles stables. Un test de validité sur séries AR(1) confirme un biais de prétraitement documenté (Dablander & Bury, 2021) : 78% de fenêtres sans bifurcation flaguées à tort. Appliqué aux 6 épisodes réels de H1, le taux de fenêtres flaguées varie réellement d'un épisode à l'autre (43% à 95%) et suit approximativement le nombre de signaux sociaux déjà trouvés par H1 -- une piste intéressante, mais pas une preuve de détection vu le biais AR(1) déjà mesuré sur le même ensemble. Appliqué à 20 tirs réels MAST (domaine Fusion), le même ensemble flague tous les tirs (disruptés comme stables) sur le critère binaire, et le taux de fenêtres flaguées est même en moyenne PLUS élevé sur les tirs stables (98%) que sur les tirs disruptés (70%) -- un résultat négatif net, dans le sens inverse de celui espéré.",
    link: { to: "/resultats/ia-vs-statistiques", label: "Voir le résultat" },
  },
];

export const MEMOIRE_COLLECTIVE_MODULES = [
  {
    code: "Hopfield",
    catchyTitle: "Comment un groupe se souvient de ce qu'il a déjà vécu",
    title: "Mémoire collective (Hopfield)",
    simple:
      "Comment un groupe reconnaît-il une situation déjà vécue, et combien de situations distinctes peut-il retenir avant de les confondre ?",
    expert:
      "Un réseau de Hopfield (mémoire associative, Hopfield 1982, prix Nobel de physique 2024) mémorise des configurations sociales passées par apprentissage hebbien, les retrouve à partir d'un signal partiel, et perd sa capacité à distinguer les situations mémorisées au-delà d'un seuil de charge précisément quantifiable. Le mécanisme qui explique ici la perte de stabilité d'un souvenir collectif éclaire, sous un autre angle, ce qu'on observe aussi dans le domaine Société -- une convergence entre deux domaines, pas une dépendance de l'un envers l'autre.",
    status: "simulation",
    statusNote:
      "Démonstration pédagogique (mémoire, mise en instabilité, limite de capacité), non testée empiriquement -- jamais un verdict confirmé/infirmé, comme H4.",
    link: { to: "/resultats/hopfield", label: "Voir le résultat" },
  },
];
