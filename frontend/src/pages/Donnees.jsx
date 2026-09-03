import { useEffect, useState } from "react";
import { api } from "../api.js";
import { BIBLIOGRAPHY } from "../data/methods.js";
import MethodNote from "../components/MethodNote.jsx";

const METHOD_ORDER = ["rolling_variance", "rolling_ac1", "kendall_tau", "surrogate_test", "morans_i", "permutation_test", "moran_trend", "h3_joint"];

export default function Donnees() {
  const [connectors, setConnectors] = useState([]);
  const [guardrails, setGuardrails] = useState(null);

  useEffect(() => {
    api.getConnectors().then(setConnectors);
    api.getGuardrails().then(setGuardrails);
  }, []);

  return (
    <div className="page page-donnees">
      <h1>D'où viennent les données, et comment sont-elles traitées ?</h1>
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
        <p className="text-muted">
          Cette mise en forme rend les sources comparables entre elles (même colonnes, mêmes types), mais ne
          dit rien de leur signification statistique — c'est le rôle des outils ci-dessous.
        </p>
      </section>

      <section>
        <h2>Les outils mathématiques utilisés</h2>
        <p>
          Une fois les données mises en forme, Hélios leur applique une poignée d'outils statistiques —
          toujours les mêmes, documentés en méthode standard, jamais inventés pour l'occasion. Chaque
          résultat affiché dans l'application montre une explication en langage courant par défaut ; voici
          la démonstration complète (pas seulement la formule finale) de chacun, avec sa référence exacte —
          §3 du cahier des charges.
        </p>
        <div className="method-reference-list">
          <MethodNote methodKeys={METHOD_ORDER} expertMode={true} />
        </div>
        <p className="text-muted" style={{ marginTop: "1rem" }}>
          <strong>Un revers à connaître :</strong> tester beaucoup de signaux à la fois (Hélios en teste
          jusqu'à une quarantaine par phénomène pour H1) augmente mécaniquement le risque qu'un signal
          ressorte « significatif » par pur hasard, même sans lien réel avec l'événement — c'est le problème
          classique des comparaisons multiples. Hélios ne corrige pas ce seuil automatiquement : il affiche
          toujours le compte complet (ex. « 4/38 signaux significatifs »), jamais un seul résultat isolé
          présenté comme une preuve.
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
            <strong>Aucune source non conforme.</strong> Si une source n'offre pas d'accès conforme à ses
            propres conditions d'utilisation, elle est exclue — même si elle serait techniquement
            récupérable (c'est pour cela que Google Trends reste désactivé, et que GDELT n'est pas encore
            intégré : voir la note du connecteur Wikipédia ci-dessus).
          </li>
          <li>
            <strong>Jamais de surinterprétation.</strong> Chaque résultat rappelle qu'un signal précurseur
            indique une perte de résilience statistique, pas une prédiction certaine ni une cause
            identifiée — et jamais de verdict « confirmée » sur un seul épisode testé.
          </li>
        </ul>
      </section>

      <section>
        <h2>Bibliographie complète</h2>
        <p className="text-muted">
          Toute affirmation théorique du §5 est accompagnée de sa référence exacte dans l'interface (mode
          expert), pas seulement d'un nom d'auteur — §12 du cahier des charges.
        </p>
        <ol className="bibliography-list">
          {BIBLIOGRAPHY.map((ref, i) => (
            <li key={i}>{ref}</li>
          ))}
        </ol>
      </section>
    </div>
  );
}
