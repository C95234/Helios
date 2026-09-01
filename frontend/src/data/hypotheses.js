/**
 * Les 3 hypothèses de recherche originales -- cahier des charges Helios §5.5.
 * Contenu centralisé pour rester cohérent entre la page /hypotheses, la démo
 * et la page d'analyse (§3 : jamais deux formulations différentes du même énoncé).
 */
import { INTERPRETATION } from "./interpretation.js";

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
      "Testable dès maintenant sur quelques phénomènes réels curatés (confiance des ménages INSEE vs attention Wikipédia) — mais sur un seul épisode à la fois, donc toujours préliminaire. GDELT (nommé au §6) reste hors d'atteinte depuis cet environnement ; Wikipédia sert de substitut pour le signal social.",
    link: { to: "/tester-h1", label: "Tester H1 sur un phénomène réel" },
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
    link: { to: "/tester-h2", label: "Tester H2 sur les départements français" },
  },
  {
    code: "H3",
    title: "Indicateur joint",
    simple:
      "Est-ce que combiner le signal temporel et le signal géographique donne un résultat plus fiable, avec moins de fausses alertes, que chacun pris isolément ?",
    expert:
      "Combiner une tendance temporelle ET une tendance spatiale significatives, via une statistique de Fisher calibrée empiriquement par données de substitution couplées, réduit les faux positifs par rapport à chaque indicateur pris isolément (§5.6).",
    status: "non-disponible",
    statusNote:
      "Pas encore testable : H1 et H2 existent désormais séparément, mais la statistique jointe (Fisher, calibrée par surrogates couplés — §5.6) qui les combine sur un même phénomène n'est pas encore construite. Voir le détail ci-dessous.",
    detailReasons: INTERPRETATION.h3.whyNotTestable,
  },
];

export const STATUS_LABELS = {
  testable: "Testable (préliminaire, un épisode à la fois)",
  "non-disponible": "Pas encore testable",
};
