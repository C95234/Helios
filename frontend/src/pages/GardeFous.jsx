import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api.js";

export default function GardeFous() {
  const [connectors, setConnectors] = useState([]);
  const [guardrails, setGuardrails] = useState(null);

  useEffect(() => {
    api.getConnectors().then(setConnectors);
    api.getGuardrails().then(setGuardrails);
  }, []);

  return (
    <div className="page page-garde-fous">
      <h1>Garde-fous techniques et éthiques</h1>
      <p className="lede">
        Hélios ne travaille que sur des sources ouvertes, accédées dans le respect de leurs propres
        conditions d'utilisation — jamais par scraping. Chaque source alimente le même schéma commun avant
        tout calcul.
      </p>

      <section>
        <h2>Les sources utilisées aujourd'hui</h2>
        <div className="connector-list">
          {connectors.map((c) => (
            <div key={c.name} className="connector-card">
              <h3>{c.label}</h3>
              <p>{c.description}</p>
              <p className="connector-access">{c.access_type}</p>
              <ul>
                {c.ethical_notes.map((note, i) => (
                  <li key={i}>{note}</li>
                ))}
              </ul>
              <a href={c.terms_of_use_url} target="_blank" rel="noreferrer">
                Conditions d'utilisation de la source →
              </a>
            </div>
          ))}
        </div>
      </section>

      <section>
        <h2>Comment les données brutes sont mises en forme (schéma commun)</h2>
        <p>
          Chaque connecteur est un module indépendant : il ne fait que <code>fetch()</code> (récupérer les
          données brutes) puis <code>normalize()</code> (les convertir vers un schéma commun). Ajouter une
          nouvelle source ne modifie jamais le reste du système.
        </p>
        {guardrails && (
          <div className="schema-box">
            <span>Schéma commun :</span>
            <code>({guardrails.schema_commun.join(", ")})</code>
          </div>
        )}
        <p className="text-muted">
          <strong>source</strong> identifie le connecteur (ex. <code>insee_bdm</code>) ·{" "}
          <strong>territoire</strong> est toujours un agrégat géographique (pays, région...), jamais une
          personne · <strong>date</strong> et <strong>valeur</strong> portent le point de mesure ·{" "}
          <strong>métadonnées</strong> garde le contexte (titre de la série, langue...).
        </p>
      </section>

      <section>
        <h2>Critères éthiques, non négociables</h2>
        <ul className="ethics-list">
          <li>
            <strong>Aucune donnée nominative.</strong> Toute colonne qui ressemble à un identifiant
            personnel (email, nom propre, numéro d'utilisateur) est rejetée à l'import, avec un message
            explicite — jamais ignorée silencieusement.
          </li>
          <li>
            <strong>Anonymisation par défaut.</strong> Aucun résultat par sous-groupe n'est affiché en
            dessous de {guardrails?.min_k_anonymity ?? 20} observations
            {guardrails ? ` (k-anonymat ≥ ${guardrails.min_k_anonymity})` : ""}. Les données communales sont
            masquées en dessous de{" "}
            {guardrails ? `${guardrails.min_commune_population_for_display.toLocaleString("fr-FR")} habitants` : "2 000 habitants"}
            .
          </li>
          <li>
            <strong>Conformité des sources, et dérogations toujours documentées.</strong> Si une source
            n'offre pas d'accès conforme à ses propres conditions d'utilisation, elle est en principe
            exclue. La seule exception assumée est Google Trends (accès non officiel, voir sa fiche
            ci-dessus) : une dérogation délibérée, évaluée et documentée dans le code du connecteur — jamais
            un contournement silencieux.
          </li>
          <li>
            <strong>Jamais de surinterprétation.</strong> Chaque résultat rappelle qu'un signal précurseur
            indique une perte de résilience statistique, pas une prédiction certaine ni une cause
            identifiée — et jamais de verdict « confirmée » sur un seul épisode testé.
          </li>
        </ul>
      </section>

      <section>
        <h2>Comparaisons multiples : un revers à connaître</h2>
        <p>
          Tester beaucoup de signaux à la fois (Hélios en teste jusqu'à une quarantaine par phénomène pour
          H1) augmente mécaniquement le risque qu'un signal ressorte « significatif » par pur hasard, même
          sans lien réel avec l'événement — c'est le problème classique des comparaisons multiples. Hélios
          ne corrige pas ce seuil automatiquement : il affiche toujours le compte complet (ex. « 4/38
          signaux significatifs »), jamais un seul résultat isolé présenté comme une preuve.
        </p>
      </section>

      <p className="text-muted">
        Les démonstrations mathématiques des outils cités ici (test par permutation, tau de Kendall, indice
        de Moran, méthode de Fisher...) sont dans la section <Link to="/methode">Méthode</Link>.
      </p>
    </div>
  );
}
