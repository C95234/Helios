import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { CartesianGrid, ResponsiveContainer, Scatter, ScatterChart, Tooltip, XAxis, YAxis } from "recharts";
import { api } from "../../api.js";
import MethodNote from "../../components/MethodNote.jsx";
import HistoryPanel from "../../components/HistoryPanel.jsx";
import ResultPageTemplate from "../../components/ResultPageTemplate.jsx";
import VerdictBadge from "../../components/VerdictBadge.jsx";
import { saveToHistory, loadHistory, clearHistory } from "../../history.js";
import { HYPOTHESES } from "../../data/hypotheses.js";
import { H5_RESULT } from "../../data/bilanPublie.js";

const HISTORY_PAGE = "h5";
const METHOD_KEYS = ["power_law_h5"];

function ccdfChartData(tailValues, alpha, xmin) {
  const n = tailValues.length;
  const empirical = tailValues.map((x, i) => ({ x, y: (n - i) / n }));
  const fitted = n > 0 ? [tailValues[0], tailValues[n - 1]].map((x) => ({ x, y: Math.pow(x / xmin, -(alpha - 1)) })) : [];
  return { empirical, fitted };
}

function ComparisonRow({ label, comparison }) {
  return (
    <tr>
      <td>{label}</td>
      <td>{comparison.r > 0 ? "loi de puissance" : "alternative"}</td>
      <td>{comparison.p_value !== null ? comparison.p_value.toFixed(3) : "n/a"}</td>
      <td>
        <VerdictBadge
          outcome={comparison.favors_power_law === true ? "favorable" : comparison.favors_power_law === false ? "against" : "neutral"}
        />
      </td>
    </tr>
  );
}

const H5_DATA = HYPOTHESES.find((h) => h.code === "H5");

export default function H5Result() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [expertMode, setExpertMode] = useState(false);
  const [history, setHistory] = useState([]);

  useEffect(() => {
    setHistory(loadHistory(HISTORY_PAGE));
  }, []);

  const run = () => {
    setLoading(true);
    setError(null);
    setResult(null);
    api
      .testH5()
      .then((r) => {
        setResult(r);
        saveToHistory(HISTORY_PAGE, { result: r });
        setHistory(loadHistory(HISTORY_PAGE));
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  };

  const chart = result ? ccdfChartData(result.tail_values, result.alpha, result.xmin) : null;

  return (
    <ResultPageTemplate
      code="H5"
      title="Criticité auto-organisée"
      catchyTitle={H5_DATA.catchyTitle}
      domain={{ name: "Société", to: "/resultats#societe" }}
      verdict={H5_RESULT.verdict}
      episodesLabel={`${H5_RESULT.nTail} chocs analysés (sur ${H5_RESULT.nTotal} au total, ${H5_RESULT.periodStart.slice(0, 4)}–${H5_RESULT.periodEnd.slice(0, 4)})`}
      summary="Les tailles des chocs de chômage départemental suivent-elles une loi de puissance -- signe que le système vit en permanence à la limite de la stabilité plutôt que d'approcher un seul point de rupture ? Sur la source réelle disponible, non : le test de plausibilité rejette la loi de puissance, et les deux modèles alternatifs (log-normale, exponentielle) sont préférés."
      postulateSimple={H5_DATA.simple}
      postulateExpert={H5_DATA.expert}
      resultText={
        <>
          <p className="text-muted">Rafraîchi automatiquement le {H5_RESULT.refreshedAt} (Insee, dernier trimestre disponible).</p>
          <dl className="signal-stats">
            <div>
              <dt>α̂ (exposant)</dt>
              <dd>{H5_RESULT.alpha.toFixed(2)}</dd>
            </div>
            <div>
              <dt>x_min</dt>
              <dd>{H5_RESULT.xmin.toFixed(2)}</dd>
            </div>
            <div>
              <dt>D (Kolmogorov-Smirnov)</dt>
              <dd>{H5_RESULT.ksStatistic.toFixed(3)}</dd>
            </div>
            <div>
              <dt>p (plausibilité, bootstrap)</dt>
              <dd>{H5_RESULT.pPlausibility.toFixed(3)}</dd>
            </div>
          </dl>
          <p className="text-muted">
            p = {H5_RESULT.pPlausibility.toFixed(3)} {"<"} 0,1 : la loi de puissance ajustée est rejetée par le test
            de plausibilité (§5.9.2) -- avant même de la comparer aux modèles alternatifs.
          </p>
          <div className="table-scroll">
            <table className="agg-table">
              <thead>
                <tr>
                  <th>Comparaison</th>
                  <th>Modèle préféré</th>
                  <th>p (Vuong)</th>
                  <th>Verdict</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>Loi de puissance vs log-normale</td>
                  <td>{H5_RESULT.lognormal.r > 0 ? "loi de puissance" : "log-normale"}</td>
                  <td>{H5_RESULT.lognormal.pValue.toFixed(3)}</td>
                  <td>
                    <VerdictBadge outcome={H5_RESULT.lognormal.favorsPowerLaw ? "favorable" : "against"} />
                  </td>
                </tr>
                <tr>
                  <td>Loi de puissance vs exponentielle</td>
                  <td>{H5_RESULT.exponential.r > 0 ? "loi de puissance" : "exponentielle"}</td>
                  <td>{H5_RESULT.exponential.pValue.toFixed(3)}</td>
                  <td>
                    <VerdictBadge outcome={H5_RESULT.exponential.favorsPowerLaw ? "favorable" : "against"} />
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <p className="text-muted">
            Détail complet sur <Link to="/bilan">la page Bilan</Link>.
          </p>
        </>
      }
      methodLink={{ to: "/methode/cours-statistiques#loi-de-puissance", label: "Voir la démonstration (loi de puissance, maximum de vraisemblance)" }}
      limits={[
        "Seule source réelle disponible : amplitude des chocs trimestriels de chômage départemental (Insee). GDELT (rate-limité de façon persistante) et Reddit/SNAP (aucun connecteur construit) restent indisponibles (§5.9.3).",
        "La résolution trimestrielle limite le nombre de chocs distincts et la finesse de la queue analysée -- un signal de criticité auto-organisée pourrait exister à une résolution plus fine (hebdomadaire, quotidienne) sans être visible ici.",
        "Un ajustement de xmin par minimisation de la distance de Kolmogorov-Smirnov peut, sur peu de points, se rabattre sur une toute petite queue où presque n'importe quelle distribution ressemble localement à une loi de puissance -- d'où l'importance de la comparaison aux modèles alternatifs plutôt que du seul test de plausibilité.",
      ]}
      journalLink={{ to: "/journal", label: "Voir le Journal de recherche" }}
    >
      <p className="lede">
        Hypothèse d'une autre nature que H1-H3 : pas un épisode testé à la fois, mais une distribution testée sur
        un grand nombre de chocs. Empirique et falsifiable -- mais un verdict n'est jamais fondé sur le seul
        ajustement visuel d'un graphe log-log (§5.9, cadrage honnête).
      </p>

      <div className="controls">
        <p className="text-muted" style={{ margin: 0 }}>
          Donnée : amplitude des chocs trimestriels de chômage départemental (Insee), 2000-2026.
        </p>
        <button className="cta" onClick={run} disabled={loading}>
          {loading ? "Calcul en cours…" : "Relancer l'ajustement en direct"}
        </button>
      </div>

      <HistoryPanel
        entries={history}
        onSelect={(entry) => setResult(entry.result)}
        onClear={() => {
          clearHistory(HISTORY_PAGE);
          setHistory([]);
        }}
        renderLabel={(e) => `α=${e.result.alpha}, x_min=${e.result.xmin}, verdict=${e.result.verdict}`}
      />

      {error && <p className="error">{error}</p>}

      {result && (
        <>
          <div className="result-card-header">
            <h2>
              α̂ = {result.alpha} · x_min = {result.xmin} · {result.n_tail} points dans la queue
            </h2>
            <button type="button" className="mode-toggle" onClick={() => setExpertMode((v) => !v)} aria-pressed={expertMode}>
              {expertMode ? "Mode simplifié" : "Mode expert"}
            </button>
          </div>

          <div className="chart-box">
            <p className="series-chart-label">
              Distribution cumulée inverse (log-log) -- points réels vs droite attendue si loi de puissance
            </p>
            <ResponsiveContainer width="100%" height={240}>
              <ScatterChart margin={{ top: 8, right: 16, bottom: 8, left: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
                <XAxis dataKey="x" type="number" scale="log" domain={["auto", "auto"]} tick={{ fontSize: 10 }} label={{ value: "taille du choc", position: "insideBottom", offset: -4, fontSize: 10 }} />
                <YAxis dataKey="y" type="number" scale="log" domain={["auto", "auto"]} tick={{ fontSize: 10 }} width={40} />
                <Tooltip formatter={(v) => (typeof v === "number" ? v.toFixed(4) : v)} />
                <Scatter name="Données réelles" data={chart.empirical} fill="var(--color-accent)" />
                <Scatter
                  name="Loi de puissance ajustée"
                  data={chart.fitted}
                  fill="var(--color-warn)"
                  line={{ stroke: "var(--color-warn)", strokeWidth: 2 }}
                  shape={() => null}
                  isAnimationActive={false}
                />
              </ScatterChart>
            </ResponsiveContainer>
            <p className="text-muted">
              Un ajustement qui « a l'air droit » sur ce genre de graphe ne prouve rien (§5.9) -- c'est justement
              pour ça que le verdict se fonde sur le test de plausibilité et la comparaison de modèles ci-dessous,
              pas sur cette impression visuelle.
            </p>
          </div>

          <dl className="signal-stats">
            <div>
              <dt>p (plausibilité, {result.n_synthetic} tirages)</dt>
              <dd>{result.p_plausibility !== null ? result.p_plausibility.toFixed(3) : "n/a"}</dd>
            </div>
            <div>
              <dt>D observé</dt>
              <dd>{result.ks_statistic}</dd>
            </div>
          </dl>

          <div className="table-scroll">
            <table className="agg-table">
              <thead>
                <tr>
                  <th>Comparaison</th>
                  <th>Modèle préféré</th>
                  <th>p (Vuong)</th>
                  <th>Verdict</th>
                </tr>
              </thead>
              <tbody>
                <ComparisonRow label="vs log-normale" comparison={result.lognormal} />
                <ComparisonRow label="vs exponentielle" comparison={result.exponential} />
              </tbody>
            </table>
          </div>

          {expertMode && (
            <dl className="signal-stats">
              <div>
                <dt>Départements / trimestres</dt>
                <dd>{result.n_departments} / {result.n_quarters}</dd>
              </div>
              <div>
                <dt>Période</dt>
                <dd>{result.period_start} → {result.period_end}</dd>
              </div>
              <div>
                <dt>N total / N queue</dt>
                <dd>{result.n_total} / {result.n_tail}</dd>
              </div>
            </dl>
          )}

          <MethodNote methodKeys={METHOD_KEYS} expertMode={expertMode} />

          <div className="simulation-banner">
            <strong>Rappel :</strong>
            <span>{result.data_source_disclaimer}</span>
          </div>
        </>
      )}
    </ResultPageTemplate>
  );
}
