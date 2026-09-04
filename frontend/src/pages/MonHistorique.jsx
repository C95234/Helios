import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { loadHistory, formatSavedAt } from "../history.js";
import { h1Outcome, h2Outcome, h3Outcome } from "../outcomes.js";

const MIN_EPISODES = 5;

function dedupByCode(entries) {
  const seen = new Map();
  for (const entry of entries) {
    // garde la plus recente par phenomene (code) -- une meme hypothese testee
    // deux fois sur le meme phenomene ne compte qu'une fois comme "episode".
    const existing = seen.get(entry.code);
    if (!existing || new Date(entry.savedAt) > new Date(existing.savedAt)) {
      seen.set(entry.code, entry);
    }
  }
  return Array.from(seen.values());
}

function OutcomeCounts({ favorable, against, neutral }) {
  return (
    <div className="agg-summary">
      <div className="agg-stat">
        <span className="agg-number">{favorable}</span>
        <span>favorable(s)</span>
      </div>
      {against !== undefined && (
        <div className="agg-stat">
          <span className="agg-number">{against}</span>
          <span>contre</span>
        </div>
      )}
      <div className="agg-stat">
        <span className="agg-number">{neutral}</span>
        <span>neutre(s) / non concluant(s)</span>
      </div>
    </div>
  );
}

export default function MonHistorique() {
  const [h1Entries, setH1Entries] = useState([]);
  const [h1AggEntries, setH1AggEntries] = useState([]);
  const [h2Entries, setH2Entries] = useState([]);
  const [h3Entries, setH3Entries] = useState([]);

  useEffect(() => {
    setH1Entries(loadHistory("h1"));
    setH1AggEntries(loadHistory("h1_aggregate"));
    setH2Entries(loadHistory("h2"));
    setH3Entries(loadHistory("h3"));
  }, []);

  const h1Distinct = dedupByCode(h1Entries);
  const h1Counts = h1Distinct.reduce(
    (acc, e) => {
      const o = h1Outcome(e.result);
      acc[o] += 1;
      return acc;
    },
    { favorable: 0, against: 0, neutral: 0 }
  );

  const h3Distinct = dedupByCode(h3Entries);
  const h3Counts = h3Distinct.reduce(
    (acc, e) => {
      const o = h3Outcome(e.result);
      acc[o === "favorable" ? "favorable" : "neutral"] += 1;
      return acc;
    },
    { favorable: 0, neutral: 0 }
  );

  const h2Counts = h2Entries.reduce(
    (acc, e) => {
      const o = h2Outcome(e.result);
      acc[o === "favorable" ? "favorable" : "neutral"] += 1;
      return acc;
    },
    { favorable: 0, neutral: 0 }
  );

  const latestAgg = h1AggEntries[0]?.result;

  // Historique fusionné, toutes hypotheses confondues, trie du plus recent au plus ancien.
  const merged = [
    ...h1Entries.map((e) => ({ hyp: "H1", label: e.result.phenomenon_label, date: e.savedAt, detail: `${e.result.n_official_significant}/${e.result.official_signals.length} off. · ${e.result.n_social_significant}/${e.result.social_signals.length} soc.`, to: "/resultats/h1" })),
    ...h1AggEntries.map((e) => ({ hyp: "H1 (agrégat)", label: "6 phénomènes", date: e.savedAt, detail: `${e.result.n_favorable_to_h1} favorable / ${e.result.n_against_h1} contre / ${e.result.n_neutral} neutre`, to: "/resultats/h1" })),
    ...h2Entries.map((e) => ({ hyp: "H2", label: `${e.result.period_start} → ${e.result.period_end}`, date: e.savedAt, detail: e.result.real_network.trend.significant_at_0_05 ? "réel significatif" : "réel non significatif", to: "/resultats/h2" })),
    ...h3Entries.map((e) => ({ hyp: "H3", label: e.result.phenomenon_label, date: e.savedAt, detail: `p_joint=${e.result.p_joint?.toFixed(3) ?? "n/a"}`, to: "/resultats/h3" })),
  ].sort((a, b) => new Date(b.date) - new Date(a.date));

  const nothingYet = h1Entries.length === 0 && h2Entries.length === 0 && h3Entries.length === 0;

  return (
    <div className="page page-bilan">
      <h1>Mon historique : qu'est-ce que j'ai testé sur cet appareil ?</h1>
      <p className="lede">
        Regroupe les tests lancés <strong>depuis ce navigateur précis</strong> (stocké localement, rien n'est
        partagé entre appareils ni envoyé à un serveur) et calcule un bilan honnête par hypothèse — jamais un
        verdict plus catégorique que ce que le nombre d'épisodes testés ne permet (§7). Vide tant que tu n'as
        rien lancé toi-même ici.
      </p>
      <p className="source-note">
        Tu cherches les résultats officiels du projet (tous les phénomènes déjà testés, publiés une fois pour
        toutes) ? Va voir <Link to="/bilan">le Bilan</Link> ou les pages{" "}
        <Link to="/resultats">Résultats</Link> — visibles par n'importe quel visiteur, sans rien avoir à
        relancer.
      </p>

      {nothingYet && (
        <p className="source-note">
          Aucun test enregistré pour l'instant sur cet appareil. Va sur{" "}
          <Link to="/resultats/h1">Résultat H1</Link>, <Link to="/resultats/h2">Résultat H2</Link> ou{" "}
          <Link to="/resultats/h3">Résultat H3</Link> pour commencer.
        </p>
      )}

      {!nothingYet && (
        <>
          <section>
            <h2>H1 — Décalage temporel</h2>
            {h1Distinct.length === 0 ? (
              <p className="source-note">Pas encore testé individuellement (l'agrégat ci-dessous compte séparément).</p>
            ) : (
              <>
                <p className="source-note">
                  {h1Distinct.length} phénomène{h1Distinct.length > 1 ? "s" : ""} distinct{h1Distinct.length > 1 ? "s" : ""} testé{h1Distinct.length > 1 ? "s" : ""} individuellement sur cet appareil.
                </p>
                <OutcomeCounts {...h1Counts} />
              </>
            )}
            {latestAgg && (
              <p className="text-muted">
                Dernier agrégat des 6 phénomènes curatés ({formatSavedAt(h1AggEntries[0].savedAt)}) :{" "}
                <strong>{latestAgg.n_favorable_to_h1} favorable</strong> / <strong>{latestAgg.n_against_h1} contre</strong> /{" "}
                <strong>{latestAgg.n_neutral} neutre</strong> sur {latestAgg.n_phenomena_tested} testés.
              </p>
            )}
            <p className={h1Distinct.length < MIN_EPISODES ? "disclaimer-preliminary" : "text-muted"}>
              {h1Distinct.length < MIN_EPISODES
                ? `Résultat préliminaire (${h1Distinct.length}/${MIN_EPISODES} épisodes indépendants minimum, §5.7) — à confirmer sur davantage de cas avant toute conclusion ferme.`
                : `${h1Distinct.length} épisodes testés -- toujours pas une preuve statistique agrégée (les phénomènes restent choisis à la main, pas tirés au hasard), mais le seuil minimal du §5.7 est atteint.`}
            </p>
          </section>

          <section>
            <h2>H2 — Robustesse sur réseau réel</h2>
            {h2Entries.length === 0 ? (
              <p className="source-note">Pas encore testé sur cet appareil.</p>
            ) : (
              <>
                <p className="source-note">
                  {h2Entries.length} exécution{h2Entries.length > 1 ? "s" : ""} enregistrée{h2Entries.length > 1 ? "s" : ""}.
                </p>
                <OutcomeCounts favorable={h2Counts.favorable} neutral={h2Counts.neutral} />
                <p className="text-muted">
                  Nuance propre à H2 : chaque exécution retourne sur le même jeu de données (les 96
                  départements, 2000-2026) -- relancer le test plusieurs fois n'ajoute pas d'épisodes
                  indépendants au sens du §5.7, seulement une actualisation si l'Insee a publié de nouvelles
                  données depuis.
                </p>
              </>
            )}
          </section>

          <section>
            <h2>H3 — Indicateur joint</h2>
            {h3Distinct.length === 0 ? (
              <p className="source-note">Pas encore testé sur cet appareil.</p>
            ) : (
              <>
                <p className="source-note">
                  {h3Distinct.length} phénomène{h3Distinct.length > 1 ? "s" : ""} distinct{h3Distinct.length > 1 ? "s" : ""} testé{h3Distinct.length > 1 ? "s" : ""}.
                </p>
                <OutcomeCounts favorable={h3Counts.favorable} neutral={h3Counts.neutral} />
              </>
            )}
            <p className={h3Distinct.length < MIN_EPISODES ? "disclaimer-preliminary" : "text-muted"}>
              {h3Distinct.length > 0 &&
                (h3Distinct.length < MIN_EPISODES
                  ? `Résultat préliminaire (${h3Distinct.length}/${MIN_EPISODES} épisodes indépendants minimum, §5.7).`
                  : `${h3Distinct.length} épisodes testés.`)}
            </p>
          </section>

          <section>
            <h2>Historique complet, toutes hypothèses confondues</h2>
            <div className="table-scroll">
              <table className="agg-table">
                <thead>
                  <tr>
                    <th>Hypothèse</th>
                    <th>Cas</th>
                    <th>Résultat</th>
                    <th>Date</th>
                    <th></th>
                  </tr>
                </thead>
                <tbody>
                  {merged.map((row, i) => (
                    <tr key={i}>
                      <td>{row.hyp}</td>
                      <td>{row.label}</td>
                      <td>{row.detail}</td>
                      <td>{formatSavedAt(row.date)}</td>
                      <td>
                        <Link to={row.to}>revoir →</Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        </>
      )}
    </div>
  );
}
