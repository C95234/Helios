/**
 * Les 3 hypothèses de recherche originales -- cahier des charges Helios §5.5.
 * Contenu centralisé pour rester cohérent entre la page /hypotheses, la démo
 * et la page d'analyse (§3 : jamais deux formulations différentes du même énoncé).
 */
export const HYPOTHESES = [
  {
    code: "H1",
    title: "Décalage temporel",
    simple:
      "Est-ce que les réseaux sociaux montrent des signes de tension avant que les statistiques officielles ne le confirment, pour un même événement de rupture ?",
    expert:
      "Les indicateurs précurseurs calculés sur les signaux sociaux se déclenchent statistiquement avant ceux calculés sur les statistiques officielles, pour un même événement de rupture territoriale réel (§5.5).",
    status: "testable",
    statusNote:
      "Testable dès maintenant sur quelques phénomènes réels curatés (confiance des ménages INSEE vs attention Wikipédia, complétée par Google Trends) — mais sur un seul épisode à la fois, donc toujours préliminaire.",
    link: { to: "/resultats/h1", label: "Voir le résultat H1" },
  },
  {
    code: "H2",
    title: "Robustesse sur réseau réel",
    simple:
      "Est-ce que la façon dont des territoires voisins évoluent ensemble se comporte différemment sur la vraie carte des communes françaises que sur une grille régulière artificielle ?",
    expert:
      "L'indice de Moran se comporte différemment sur le réseau réel (tailles et topologie hétérogènes) que sur une grille régulière de contrôle de même taille — un créneau identifié dans la littérature, où les études EWS spatiales sont presque toujours validées sur des grilles idéalisées (§5.5).",
    status: "testable",
    statusNote:
      "Testable dès maintenant : réseau réel des 96 départements de métropole (contours IGN) contre une grille régulière de contrôle, sur le taux de chômage départemental (Insee). Toujours une seule coupe temporelle — préliminaire.",
    link: { to: "/resultats/h2", label: "Voir le résultat H2" },
  },
  {
    code: "H3",
    title: "Indicateur joint",
    simple:
      "Est-ce que combiner le signal temporel et le signal géographique donne un résultat plus fiable, avec moins de fausses alertes, que chacun pris isolément ?",
    expert:
      "Combiner une tendance temporelle ET une tendance spatiale significatives, via une statistique de Fisher calibrée empiriquement par données de substitution couplées, réduit les faux positifs par rapport à chaque indicateur pris isolément (§5.6).",
    status: "testable",
    statusNote:
      "Testable dès maintenant, avec une adaptation assumée : la p-value spatiale est un instantané (pas une tendance, faute de données départementales assez fréquentes), et la loi nulle jointe est calibrée par comparaison à l'historique réel 2000-2026 plutôt que par surrogates synthétiques couplés. Voir les détails sur la page de test.",
    link: { to: "/resultats/h3", label: "Voir le résultat H3" },
  },
  {
    code: "H4",
    title: "Contrôle actif de la synchronisation (inspiré du RCA)",
    simple:
      "Peut-on empêcher une bascule collective sans supprimer l'activité individuelle -- en affaiblissant seulement les liens entre les éléments qui sont en train de se synchroniser entre eux, plutôt qu'en réduisant tout le système au silence ?",
    expert:
      "Un couplage adaptatif par paire, qui s'affaiblit localement tant qu'une paire d'oscillateurs reste verrouillée en phase, peut maintenir le paramètre d'ordre collectif $r$ sous un seuil $r_c$ malgré les mêmes perturbations qui feraient basculer le système sous couplage fixe (§5.8).",
    status: "simulation",
    statusNote:
      "H4 est d'une autre nature que H1-H3 : une démonstration de principe en simulation (modèle de Kuramoto), jamais un test statistique contre des données réelles. Aucun verdict « confirmée / infirmée » n'est jamais attaché à ses résultats.",
    link: { to: "/resultats/h4", label: "Voir le résultat H4" },
  },
  {
    code: "H5",
    title: "Criticité auto-organisée",
    simple:
      "Est-ce que les tailles des chocs observés (au lieu d'une seule bascule ponctuelle) suivent une loi de puissance -- signe que le système vit en permanence à la limite de la stabilité, plutôt que d'approcher un seul point de rupture ?",
    expert:
      "Les tailles d'événements du système observé suivent une loi de puissance (Bak, Tang & Wiesenfeld, 1987), estimée par maximum de vraisemblance (Clauset, Shalizi & Newman, 2009) et validée par un test de plausibilité par bootstrap -- jamais par simple ajustement visuel sur un graphe log-log (§5.9).",
    status: "distribution",
    statusNote:
      "Nature différente de H1-H4 : pas un épisode testé à la fois, mais une distribution testée sur un grand nombre de chocs (amplitude des variations trimestrielles du chômage départemental, Insee -- GDELT et Reddit/SNAP restent indisponibles). Empirique et falsifiable, mais pas comparable épisode par épisode à H1-H3.",
    link: { to: "/resultats/h5", label: "Voir le résultat H5" },
  },
];

export const STATUS_LABELS = {
  testable: "Testable (préliminaire, un épisode à la fois)",
  "non-disponible": "Pas encore testable",
  simulation: "Simulation pédagogique (pas un test statistique)",
  distribution: "Testable (test de distribution, pas un épisode)",
};
