import { HYPOTHESES } from "../data/hypotheses.js";
import HypothesisCard from "../components/HypothesisCard.jsx";

export default function Hypotheses() {
  return (
    <div className="page page-hypotheses">
      <h1>Les 3 hypothèses qu'Hélios cherche à tester</h1>
      <p className="lede">
        Hélios n'est pas qu'un calculateur d'indicateurs : le projet teste trois hypothèses de recherche
        originales sur des données réelles, et en tire une conclusion honnête — jamais un verdict plus
        catégorique que ce que le test statistique permet.
      </p>

      <div className="hypotheses-list">
        {HYPOTHESES.map((h) => (
          <HypothesisCard key={h.code} hypothesis={h} />
        ))}
      </div>

      <p className="hypotheses-footnote">
        Le protocole de validation prévoit au moins 5 épisodes historiques indépendants avant toute
        conclusion ferme sur l'une de ces hypothèses — jamais de verdict « confirmée » sur un seul cas.
      </p>
    </div>
  );
}
