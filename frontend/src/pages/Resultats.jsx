import { HYPOTHESES } from "../data/hypotheses.js";
import { FUSION_DOMAIN_MODULES, MEMOIRE_COLLECTIVE_MODULES } from "../data/domainModules.js";
import HypothesisCard from "../components/HypothesisCard.jsx";

export default function Resultats() {
  return (
    <div className="page page-hypotheses">
      <h1>Résultats</h1>
      <p className="lede">
        Hélios teste des méthodes de détection de bascules et d'états critiques, établies dans la
        littérature scientifique, sur trois domaines distincts -- société, fusion nucléaire, mémoire
        collective -- présentés ici en parallèle, sans ordre de priorité entre eux. Chaque page de module
        suit le même gabarit : verdict, postulat, résultat obtenu, limites, puis l'outil pour le tester
        soi-même en direct (sauf mention contraire). Les résultats de chaque domaine ne sont jamais combinés
        entre eux.
      </p>

      <section id="societe" className="domain-section">
        <h2>Domaine Société</h2>
        <p className="domain-tagline">
          Un système social envoie-t-il des signes avant de basculer -- et peut-on apprendre à les repérer,
          honnêtement, avant que les statistiques officielles ne les confirment ?
        </p>
        <div className="hypotheses-list">
          {HYPOTHESES.map((h) => (
            <HypothesisCard key={h.code} hypothesis={h} />
          ))}
        </div>
        <p className="hypotheses-footnote">
          Pour H1-H3 : le protocole de validation prévoit au moins 5 épisodes historiques indépendants avant
          toute conclusion ferme — jamais de verdict « confirmée » sur un seul cas. H4 n'entre pas dans ce
          décompte : en tant que simulation, elle n'aura jamais de verdict de ce type, quel que soit le
          nombre d'exécutions. H5 non plus : son verdict repose sur un test de plausibilité par bootstrap et
          une comparaison à des modèles alternatifs (§5.9.2), pas sur un décompte d'épisodes.
        </p>
      </section>

      <section id="fusion" className="domain-section">
        <h2>Domaine Fusion nucléaire</h2>
        <p className="domain-tagline">
          Avant qu'un plasma de fusion ne perde son confinement -- ou ne s'embrase de lui-même -- y a-t-il
          des signes avant-coureurs mesurables ?
        </p>
        <div className="hypotheses-list">
          {FUSION_DOMAIN_MODULES.map((m) => (
            <HypothesisCard key={m.code} hypothesis={m} />
          ))}
        </div>
      </section>

      <section id="memoire-collective" className="domain-section">
        <h2>Domaine Mémoire collective</h2>
        <p className="domain-tagline">
          Comment un groupe se souvient-il d'une situation déjà vécue, et jusqu'où peut-il pousser sa mémoire
          avant de tout confondre ?
        </p>
        <div className="hypotheses-list">
          {MEMOIRE_COLLECTIVE_MODULES.map((m) => (
            <HypothesisCard key={m.code} hypothesis={m} />
          ))}
        </div>
      </section>
    </div>
  );
}
