import { HYPOTHESES } from "../data/hypotheses.js";
import HypothesisCard from "../components/HypothesisCard.jsx";

export default function Resultats() {
  return (
    <div className="page page-hypotheses">
      <h1>Résultats</h1>
      <p className="lede">
        Hélios teste trois hypothèses de recherche originales sur des données réelles, et en tire une
        conclusion honnête — jamais un verdict plus catégorique que ce que le test statistique permet. Une
        quatrième (H4) est d'une autre nature : une simulation pédagogique, pas un test statistique — voir
        sa mention distincte ci-dessous. Chaque page de résultat suit le même gabarit : verdict, postulat,
        résultat obtenu, limites, puis l'outil pour le tester soi-même en direct.
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
        d'exécutions.
      </p>
    </div>
  );
}
