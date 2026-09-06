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
