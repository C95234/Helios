import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import { api } from "../../api.js";
import SeriesChart from "../../components/SeriesChart.jsx";
import MethodDisclaimer from "../../components/MethodDisclaimer.jsx";
import MethodNote from "../../components/MethodNote.jsx";
import InterpretationGuide from "../../components/InterpretationGuide.jsx";
import HistoryPanel from "../../components/HistoryPanel.jsx";
import ReportExport from "../../components/ReportExport.jsx";
import ResultPageTemplate from "../../components/ResultPageTemplate.jsx";
import { saveToHistory, loadHistory, clearHistory } from "../../history.js";
import { h2Outcome } from "../../outcomes.js";
import { formatGeneratedAt, methodMarkdown, interpretationMarkdown, disclaimerMarkdown } from "../../report.js";
import { HYPOTHESES } from "../../data/hypotheses.js";
import { H2_RESULT, H2_MORAN_SERIES, H2_AGGREGATE, H2_REFRESHED_AT } from "../../data/bilanPublie.js";
import VerdictBadge from "../../components/VerdictBadge.jsx";

const h2ChartData = H2_MORAN_SERIES.dates.map((date, i) => ({
  date,
  reel: H2_MORAN_SERIES.real[i],
  grille: H2_MORAN_SERIES.grid[i],
}));

const HISTORY_PAGE = "h2";
const HISTORY_PAGE_AGGREGATE = "h2_aggregate";
const NETWORK_METHOD_KEYS = ["morans_i", "moran_trend", "permutation_test"];

/** Meme seuils que _h2_aggregate_verdict (backend/scripts/refresh_results.py)
 * et test_h2_aggregate (routers/h2.py) -- duplique ici faute d'un endroit
 * commun entre le script Python et le frontend JS (meme limite deja
 * documentee pour Fusion/Plasma). */
function aggregateOutcome(nFavorable, nAgainst, n) {
  if (n === 0) return "neutral";
  if (nFavorable > nAgainst && nFavorable >= n / 2) return "favorable";
  if (nAgainst > nFavorable && nAgainst >= n / 2) return "against";
  return "neutral";
}

function AggregateVariableRow({ v }) {
  return (
    <tr>
      <td>{v.label}</td>
      <td>
        {v.n_periods ?? v.nPeriods} ({(v.period_start ?? v.periodStart)?.slice(0, 4)}–{(v.period_end ?? v.periodEnd)?.slice(0, 4)})
      </td>
      <td>{(v.real_trend?.observed_tau ?? v.realTau)?.toFixed(3)}</td>
      <td>{(v.grid_trend?.observed_tau ?? v.gridTau)?.toFixed(3)}</td>
      <td>
        <VerdictBadge outcome={v.outcome} />
      </td>
    </tr>
  );
}

function NetworkBlock({ label, data, note, color }) {
  const [expertMode, setExpertMode] = useState(false);
  const { trend, latest_snapshot, moran_series } = data;

  return (
    <div className="signal-block">
      <div className="result-card-header">
        <h3>{label}</h3>
        <button type="button" className="mode-toggle" onClick={() => setExpertMode((v) => !v)} aria-pressed={expertMode}>
          {expertMode ? "Mode simplifié" : "Mode expert"}
        </button>
      </div>
      <p className="signal-title">{note}</p>
      <SeriesChart dates={moran_series.dates} values={moran_series.values} color={color} label="Indice de Moran par trimestre (2000-2026)" />

      {!expertMode && (
        <>
          <p className={trend.significant_at_0_05 ? "moran-sig-yes" : "moran-sig-no"}>
            {trend.significant_at_0_05
              ? "La synchronisation entre voisins suit une vraie tendance sur ces 26 ans, plus que ce que le hasard expliquerait."
              : "Pas de vraie tendance sur ces 26 ans : la synchronisation entre voisins monte et descend, sans direction claire."}
          </p>
          <p className={latest_snapshot.significant_at_0_05 ? "moran-sig-yes" : "moran-sig-no"}>
            {latest_snapshot.significant_at_0_05
              ? "Sur le dernier trimestre, les voisins se ressemblent nettement plus que le hasard ne l'expliquerait."
              : "Sur le dernier trimestre, les voisins ne se ressemblent pas plus que ne l'expliquerait le hasard."}
          </p>
          <MethodNote methodKeys={NETWORK_METHOD_KEYS} expertMode={false} />
        </>
      )}

      {expertMode && (
        <>
          <p className="signal-title" style={{ marginTop: "0.75rem" }}>Tendance sur 26 ans (105 trimestres)</p>
          <dl className="signal-stats">
            <div>
              <dt>tau de Kendall</dt>
              <dd>{trend.observed_tau?.toFixed(3)}</dd>
            </div>
            <div>
              <dt>p-value</dt>
              <dd>{trend.p_value?.toFixed(3)}</dd>
            </div>
            <div>
              <dt>Surrogates</dt>
              <dd>{trend.n_surrogates}</dd>
            </div>
            <div>
              <dt>Points</dt>
              <dd>{trend.n_points}</dd>
            </div>
          </dl>
          <p className="signal-title" style={{ marginTop: "0.75rem" }}>Coupe du dernier trimestre (test par permutation)</p>
          <dl className="signal-stats">
            <div>
              <dt>Indice de Moran</dt>
              <dd>{latest_snapshot.observed_i?.toFixed(3)}</dd>
            </div>
            <div>
              <dt>p-value</dt>
              <dd>{latest_snapshot.p_value?.toFixed(3)}</dd>
            </div>
            <div>
              <dt>Moyenne du hasard</dt>
              <dd>{latest_snapshot.null_mean?.toFixed(3)}</dd>
            </div>
            <div>
              <dt>Écart-type du hasard</dt>
              <dd>{latest_snapshot.null_std?.toFixed(3)}</dd>
            </div>
          </dl>
          <MethodNote methodKeys={NETWORK_METHOD_KEYS} expertMode={true} />
        </>
      )}
    </div>
  );
}

function networkMarkdown(title, data) {
  return [
    `## ${title}`,
    "",
    `- Tendance sur 26 ans : tau de Kendall = ${data.trend.observed_tau?.toFixed(3) ?? "n/a"}, p = ${data.trend.p_value?.toFixed(3) ?? "n/a"} (${data.trend.significant_at_0_05 ? "significatif" : "non significatif"})`,
    `- Dernier trimestre (permutation) : I = ${data.latest_snapshot.observed_i?.toFixed(3) ?? "n/a"}, p = ${data.latest_snapshot.p_value?.toFixed(3) ?? "n/a"} (${data.latest_snapshot.significant_at_0_05 ? "significatif" : "non significatif"})`,
    "",
  ].join("\n");
}

function buildH2Markdown(result) {
  const lines = [
    `# H2 — Robustesse sur réseau réel`,
    "",
    `Rapport généré le ${formatGeneratedAt()} par Hélios.`,
    "",
    `Période ${result.period_start} → ${result.period_end}, ${result.n_units} départements, ${result.n_quarters} trimestres, ${result.n_edges_real_network} paires de voisins sur le réseau réel, grille ${result.grid_shape[0]}×${result.grid_shape[1]}.`,
    "",
    "## Verdict",
    "",
    result.verdict_simple,
    "",
  ];
  lines.push(networkMarkdown("Réseau réel (départements)", result.real_network));
  lines.push(networkMarkdown("Grille de contrôle (artificielle)", result.control_grid));

  lines.push("## Méthode", "");
  for (const key of NETWORK_METHOD_KEYS) lines.push(methodMarkdown(key));

  lines.push(interpretationMarkdown("h2", h2Outcome(result)));
  lines.push(disclaimerMarkdown(result.n_episodes_tested, result.causal_disclaimer));

  return lines.join("\n");
}

const H2_DATA = HYPOTHESES.find((h) => h.code === "H2");

export default function H2Result() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [history, setHistory] = useState([]);

  const [aggregate, setAggregate] = useState(null);
  const [aggregateLoading, setAggregateLoading] = useState(false);
  const [aggregateError, setAggregateError] = useState(null);
  const [aggregateHistory, setAggregateHistory] = useState([]);

  useEffect(() => {
    setHistory(loadHistory(HISTORY_PAGE));
    setAggregateHistory(loadHistory(HISTORY_PAGE_AGGREGATE));
  }, []);

  const run = () => {
    setLoading(true);
    setError(null);
    setResult(null);
    api
      .testH2()
      .then((r) => {
        setResult(r);
        saveToHistory(HISTORY_PAGE, { result: r });
        setHistory(loadHistory(HISTORY_PAGE));
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  };

  const runAggregate = () => {
    setAggregateLoading(true);
    setAggregateError(null);
    setAggregate(null);
    api
      .testH2Aggregate()
      .then((r) => {
        setAggregate(r);
        saveToHistory(HISTORY_PAGE_AGGREGATE, { result: r });
        setAggregateHistory(loadHistory(HISTORY_PAGE_AGGREGATE));
      })
      .catch((e) => setAggregateError(e.message))
      .finally(() => setAggregateLoading(false));
  };

  const barData = result?.values_latest.map((v) => ({ name: v.code, value: v.value })) ?? [];

  return (
    <ResultPageTemplate
      code="H2"
      title="Robustesse sur réseau réel"
      catchyTitle={H2_DATA.catchyTitle}
      domain={{ name: "Société", to: "/resultats#societe" }}
      verdict={H2_AGGREGATE.verdict}
      episodesLabel={`${H2_AGGREGATE.nVariablesTested} variables réelles testées`}
      summary="L'indice de Moran se comporte-t-il différemment sur le vrai réseau des 96 départements de métropole que sur une grille régulière artificielle de même taille ? Testé sur 5 variables territoriales réelles (pas seulement le chômage) : 3 vont à l'encontre de H2 (la grille de contrôle montre une tendance significative, pas le réseau réel), 2 restent non concluantes, aucune ne va dans le sens de H2."
      postulateSimple={H2_DATA.simple}
      postulateExpert={H2_DATA.expert}
      resultText={
        <>
          <p className="text-muted">Rafraîchi automatiquement le {H2_REFRESHED_AT} (Insee, dernier trimestre/mois disponible).</p>
          <dl className="signal-stats">
            <div>
              <dt>Variables favorables à H2</dt>
              <dd>{H2_AGGREGATE.nFavorable}/{H2_AGGREGATE.nVariablesTested}</dd>
            </div>
            <div>
              <dt>Variables défavorables</dt>
              <dd>{H2_AGGREGATE.nAgainst}/{H2_AGGREGATE.nVariablesTested}</dd>
            </div>
          </dl>
          <div className="table-scroll">
            <table className="agg-table">
              <thead>
                <tr>
                  <th>Variable réelle</th>
                  <th>Périodes (couverture)</th>
                  <th>τ réseau réel</th>
                  <th>τ grille</th>
                  <th>Verdict</th>
                </tr>
              </thead>
              <tbody>
                {H2_AGGREGATE.variables.map((v) => (
                  <AggregateVariableRow key={v.key} v={v} />
                ))}
              </tbody>
            </table>
          </div>
          <p className="text-muted">{H2_AGGREGATE.verdictSimple}</p>
          <p className="text-muted">
            Détail complet pour le chômage (variable d'origine de H2), avec son graphique dans le temps :
          </p>
          <dl className="signal-stats">
            <div>
              <dt>Réel — tendance (τ)</dt>
              <dd>{H2_RESULT.realNetwork.trendTau} (p={H2_RESULT.realNetwork.trendP})</dd>
            </div>
            <div>
              <dt>Grille — tendance (τ)</dt>
              <dd>{H2_RESULT.controlGrid.trendTau} (p={H2_RESULT.controlGrid.trendP})</dd>
            </div>
          </dl>
          <div className="chart-box">
            <p className="series-chart-label">Indice de Moran par trimestre, 2000-2026 (réel vs grille, chômage)</p>
            <ResponsiveContainer width="100%" height={220}>
              <LineChart data={h2ChartData} margin={{ top: 8, right: 16, bottom: 0, left: -16 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
                <XAxis dataKey="date" tick={{ fontSize: 9 }} minTickGap={60} />
                <YAxis tick={{ fontSize: 10 }} width={40} domain={["auto", "auto"]} />
                <Tooltip formatter={(v) => v.toFixed(3)} />
                <Line type="monotone" dataKey="reel" name="Réseau réel" stroke="var(--color-accent)" dot={false} strokeWidth={2} connectNulls />
                <Line type="monotone" dataKey="grille" name="Grille de contrôle" stroke="var(--color-mid)" dot={false} strokeWidth={1.5} connectNulls />
              </LineChart>
            </ResponsiveContainer>
          </div>
          <p className="moran-sig-yes">
            Le réseau réel est au-dessus de la grille de contrôle sur les {H2_RESULT.nRealAboveGrid}{" "}
            trimestres, sans une seule exception -- pas ce que H2 teste formellement (la tendance), mais une
            différence structurelle systématique. Voir le détail sur <Link to="/bilan">la page Bilan</Link>.
          </p>
        </>
      }
      methodLink={{ to: "/methode/cours-statistiques#moran", label: "Voir la démonstration (indice de Moran)" }}
      limits={[
        "5 variables réelles, pas 5 épisodes indépendants au sens du §5.7 : ce sont 5 mesures différentes sur le même territoire et à peu près la même période, pas 5 systèmes territoriaux distincts -- un indice plus robuste qu'une seule variable, mais pas l'équivalent de 5 réplications indépendantes.",
        "Fréquences et couvertures différentes selon la variable (chômage et logements en cumul 12 mois, créations d'entreprises en cumul 12 mois faute de variante CVS au niveau département, population en annuel sur 52 points seulement) -- pas directement comparables entre elles en rigueur statistique.",
        "La grille de contrôle replace les mêmes valeurs dans un ordre arbitraire, pas selon une géographie fictive alternative construite exprès.",
      ]}
      journalLink={{ to: "/journal", label: "Voir le Journal de recherche" }}
    >
      <p className="lede">
        Calculé sur les 105 trimestres disponibles (2000-2026) plutôt que sur un seul instantané — un
        indicateur sur une seule date n'aurait rien de significatif statistiquement.
      </p>

      <div className="controls">
        <p className="text-muted" style={{ margin: 0 }}>
          Donnée : taux de chômage localisé par département (Insee), tous les trimestres depuis 2000.
        </p>
        <button className="cta" onClick={run} disabled={loading}>
          {loading ? "Calcul en cours…" : "Comparer réseau réel et grille de contrôle"}
        </button>
      </div>

      <HistoryPanel
        entries={history}
        onSelect={(entry) => setResult(entry.result)}
        onClear={() => {
          clearHistory(HISTORY_PAGE);
          setHistory([]);
        }}
        renderLabel={(e) => `Période ${e.result.period_start} → ${e.result.period_end}`}
      />

      {error && <p className="error">{error}</p>}

      {result && (
        <>
          <p className="source-note">
            {result.n_units} départements · {result.n_quarters} trimestres ({result.period_start} →{" "}
            {result.period_end}) · {result.n_edges_real_network} paires de voisins sur le réseau réel · grille
            {" "}
            {result.grid_shape[0]}×{result.grid_shape[1]}
          </p>

          <div className="result-grid">
            <NetworkBlock
              label="Réseau réel (départements)"
              data={result.real_network}
              note="Chaque département n'est voisin que de ceux qu'il touche vraiment sur la carte."
              color="var(--color-accent)"
            />
            <NetworkBlock
              label="Grille de contrôle (artificielle)"
              data={result.control_grid}
              note="Mêmes valeurs, replacées sur une grille régulière sans rapport avec la vraie géographie."
              color="var(--color-mid)"
            />
          </div>

          <div className="chart-box">
            <p className="series-chart-label">Taux de chômage par département, dernier trimestre ({result.period_end})</p>
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={barData} margin={{ top: 8, right: 16, bottom: 0, left: -16 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
                <XAxis dataKey="name" tick={{ fontSize: 8 }} interval={4} />
                <YAxis tick={{ fontSize: 10 }} width={32} />
                <Tooltip />
                <Bar dataKey="value" fill="var(--color-accent)" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="h1-verdict">
            <p>{result.verdict_simple}</p>
          </div>

          <InterpretationGuide hypothesis="h2" outcome={h2Outcome(result)} />

          <MethodDisclaimer nEpisodes={result.n_episodes_tested} />

          <ReportExport buildMarkdown={() => buildH2Markdown(result)} filenameBase={`helios-h2-${result.period_start}-${result.period_end}`} />
        </>
      )}

      <hr className="divider" />
      <h2>Relancer les 5 variables en direct</h2>
      <p className="text-muted">
        Refait le test réseau réel vs grille de contrôle sur les 5 variables territoriales réelles (chômage,
        défaillances d'entreprises, logements autorisés, créations d'entreprises, population) --
        exactement comme pour produire le tableau figé ci-dessus.
      </p>
      <button className="cta secondary" onClick={runAggregate} disabled={aggregateLoading}>
        {aggregateLoading ? "Calcul en cours…" : "Tester les 5 variables en direct"}
      </button>

      <HistoryPanel
        entries={aggregateHistory}
        onSelect={(entry) => setAggregate(entry.result)}
        onClear={() => {
          clearHistory(HISTORY_PAGE_AGGREGATE);
          setAggregateHistory([]);
        }}
        renderLabel={(e) => `${e.result.n_favorable}/${e.result.n_variables_tested} favorables, ${e.result.n_against}/${e.result.n_variables_tested} défavorables`}
      />

      {aggregateError && <p className="error">{aggregateError}</p>}

      {aggregate && (
        <>
          <div className="result-card-header">
            <h3>Résultat en direct</h3>
            <VerdictBadge outcome={aggregateOutcome(aggregate.n_favorable, aggregate.n_against, aggregate.n_variables_tested)} />
          </div>
          <p className="source-note">{aggregate.verdict_simple}</p>
          <div className="table-scroll">
            <table className="agg-table">
              <thead>
                <tr>
                  <th>Variable réelle</th>
                  <th>Périodes (couverture)</th>
                  <th>τ réseau réel</th>
                  <th>τ grille</th>
                  <th>Verdict</th>
                </tr>
              </thead>
              <tbody>
                {aggregate.results.map((v) => (
                  <AggregateVariableRow key={v.key} v={v} />
                ))}
              </tbody>
            </table>
          </div>
          {aggregate.errors.length > 0 && (
            <p className="text-muted">Indisponibles : {aggregate.errors.join(" · ")}</p>
          )}
        </>
      )}
    </ResultPageTemplate>
  );
}
