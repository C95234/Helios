/**
 * Positionnement scientifique honnête -- cahier des charges Helios §1bis.
 * Contenu centralisé : la home et le Bilan en portent chacun une
 * reformulation courte qui renvoie ici, jamais une redite complète
 * (règle de non-duplication, restructuration §3).
 */
export const POSITIONING_SHORT =
  "Hélios n'invente ni nouvelle théorie ni nouvelle méthode : chaque outil utilisé (signaux précurseurs, criticité, synchronisation, indice de Moran) est déjà établi dans la littérature. Sa contribution réelle tient à quatre choses -- réplication sur un domaine jamais testé, publication de résultats négatifs, un outil réutilisable, de la médiation scientifique -- jamais une « découverte ».";

export const CONTRIBUTIONS = [
  {
    title: "De la réplication",
    text: "Les théories mobilisées (signaux précurseurs, criticité, synchronisation) ont été testées sur une poignée de domaines (écologie, épidémiologie, finance, neurosciences). Personne n'avait testé leur généralisation à des données socio-territoriales françaises combinant Insee et réseaux sociaux ouverts. La réplication sur un nouveau domaine est une contribution scientifique réelle, quoique modeste -- c'est l'écrasante majorité du travail scientifique publié chaque année, loin du mythe de la découverte spectaculaire.",
  },
  {
    title: "Des résultats négatifs documentés",
    text: "La littérature publiée est structurellement biaisée vers les résultats positifs (biais de publication). Un résultat négatif obtenu avec un protocole rigoureux et publié tel quel (voir le Bilan) corrige, à très petite échelle, ce biais.",
  },
  {
    title: "Un outil réutilisable et reproductible",
    text: "Le pipeline (connecteurs de données, tests statistiques calibrés, garde-fous, scripts versionnés) reste utilisable par quiconque voudrait tester un nouvel épisode, sans dépendre de qui a testé quoi en premier.",
  },
  {
    title: "De la médiation scientifique",
    text: "Le Journal de recherche, le cours de statistiques et la démo interactive font circuler des méthodes réelles (signaux précurseurs, tests par permutation, indice de Moran) vers un public qui n'y aurait pas accès autrement.",
  },
];

export const NOT_A_DISCOVERY =
  "Ce que ce projet n'apporte pas : une nouvelle théorie, une nouvelle méthode mathématique, ou une découverte au sens où on l'entend pour un prix scientifique majeur. Le mot « découverte » n'est jamais utilisé pour décrire un résultat du projet -- ni sur le site, ni dans les rapports générés, ni dans le Journal de recherche.";

/**
 * Deux preuves concrètes du pilier "outil réutilisable" (§1ter) -- statut
 * tenu à jour à la main, jamais présenté comme acquis avant de l'être
 * réellement. Voir /positionnement/ewstools et /positionnement/hopfieldkit.
 */
export const EWSTOOLS_STATUS = {
  developpe_non_soumis: { label: "Développé, pas encore soumis", tone: "neutral" },
  soumis: { label: "Soumis (pull request ouverte)", tone: "neutral" },
  en_attente: { label: "En attente de revue", tone: "neutral" },
  fusionne: { label: "Accepté / Fusionné", tone: "favorable" },
  non_retenu: { label: "Non retenu", tone: "against" },
};

export const EWSTOOLS_INFO = {
  status: "developpe_non_soumis",
  repoUrl: "https://github.com/ThomasMBury/ewstools",
  packageName: "ewstools",
  summary:
    "Deux modules développés pour combler un manque identifié dans ewstools (bibliothèque Python de référence pour les signaux précurseurs, publiée dans le Journal of Open Source Software) : un indicateur spatial (indice de Moran, absent du paquet) et une combinaison de p-values corrélées (méthode empirique de Brown, absente aussi).",
  nTestsAdded: 21,
  nTestsExistingBaseline: 32,
  gapFound:
    "Recherche vérifiée en direct sur le dépôt réel avant tout code : ewstools couvre en détail la branche temporelle des signaux précurseurs (variance, autocorrélation, spectre...) mais ne contient aucune trace de « moran », « spatial », « fisher » ou « brown » dans ses modules principaux.",
  usageAngles: [
    "Recherche : toute étude de transition critique sur données spatialisées (écologie, épidémiologie, données socio-territoriales, réseaux de capteurs) gagne un outil de signal précurseur spatial dans le même paquet que l'outil temporel.",
    "Industrie / surveillance d'infrastructure : réseaux de capteurs (réseaux électriques, surveillance structurelle) produisent déjà exactement la forme de données attendue par le nouveau module.",
    "Services publics : les agences de statistiques territoriales publiant des indicateurs réguliers par unité administrative peuvent l'utiliser directement sur leurs propres données.",
  ],
};

export const HOPFIELDKIT_STATUS = {
  code_complet_non_publie: { label: "Code complet, non encore publié", tone: "neutral" },
  publie_pypi: { label: "Publié sur PyPI", tone: "favorable" },
};

export const HOPFIELDKIT_INFO = {
  status: "code_complet_non_publie",
  packageName: "hopfieldkit",
  repoUrl: null,
  summary:
    "Apprentissage hebbien, démonstration de convergence, théorie de la capacité (bornes de Hopfield 1982 et Amit-Gutfreund-Sompolinsky 1985), diagnostics des limites connues (attracteurs parasites, dépendance à l'ordre de mise à jour), et un second mode d'apprentissage par descente de gradient façon perceptron (Gardner 1988 ; Diederich & Opper 1987), avec comparaison empirique de capacité entre les deux méthodes.",
  nTests: 22,
  gapFound:
    "Le paysage des réseaux de Hopfield en Python est fragmenté -- une dizaine de petits projets isolés, sans tests ni documentation comparables -- d'où un paquet autonome plutôt qu'une contribution à un outil dominant existant (à la différence d'ewstools).",
  usageAngles: [
    "Pédagogie : les deux modes d'apprentissage, la théorie de la capacité et les diagnostics de limites en un seul paquet testé, réutilisable pour tout cours ou démonstration sur la mémoire associative.",
    "Recherche : base de départ testée pour comparer empiriquement des règles d'apprentissage sur la mémoire associative, plutôt que de repartir d'un script isolé à chaque fois.",
    "Portfolio : une preuve de compétence en implémentation rigoureuse d'un modèle établi (démonstration de convergence, bornes théoriques vérifiées empiriquement, limites diagnostiquées plutôt que passées sous silence).",
  ],
};
