import { Link } from "react-router-dom";
import { HYPOTHESES } from "../data/hypotheses.js";
import HypothesisCard from "../components/HypothesisCard.jsx";

export default function Resultats() {
  return (
    <div className="page page-hypotheses">
      <h1>Résultats</h1>
      <p className="lede">
        Hélios teste quatre hypothèses de recherche originales sur des données réelles (H1, H2, H3, H5), et en
        tire une conclusion honnête — jamais un verdict plus catégorique que ce que le test statistique permet.
        H4 est d'une autre nature : une simulation pédagogique, pas un test statistique — voir sa mention
        distincte ci-dessous. H5 diffère aussi des trois premières : pas un épisode testé à la fois, mais une
        distribution testée sur un grand nombre de chocs (§5.9). Chaque page de résultat suit le même gabarit :
        verdict, postulat, résultat obtenu, limites, puis l'outil pour le tester soi-même en direct.
      </p>

      <div className="hypotheses-list">
        {HYPOTHESES.map((h) => (
          <HypothesisCard key={h.code} hypothesis={h} />
        ))}
      </div>

      <p className="hypotheses-footnote">
        Pour H1-H3 : le protocole de validation prévoit au moins 5 épisodes historiques indépendants avant
        toute conclusion ferme — jamais de verdict « confirmée » sur un seul cas. H4 n'entre pas dans ce
        décompte : en tant que simulation, elle n'aura jamais de verdict de ce type, quel que soit le nombre
        d'exécutions. H5 non plus : son verdict repose sur un test de plausibilité par bootstrap et une
        comparaison à des modèles alternatifs (§5.9.2), pas sur un décompte d'épisodes.
      </p>

      <section className="hypotheses-teaser" style={{ marginTop: "2.5rem" }}>
        <h2>Second domaine d'application — Fusion nucléaire</h2>
        <p>
          Le même pipeline de détection (variance, autocorrélation, indice de Moran — code inchangé) appliqué
          à des données réelles et ouvertes de tokamak (MAST, UKAEA), pour démontrer que la méthode généralise
          au-delà du socio-territorial. Détection uniquement -- jamais un système de contrôle réel, jamais
          combiné aux résultats H1-H5 dans un même verdict.
        </p>
        <Link to="/resultats/fusion" className="cta secondary">
          Voir la détection sur données de fusion
        </Link>
      </section>
    </div>
  );
}
