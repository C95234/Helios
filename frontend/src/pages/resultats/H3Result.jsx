import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ZAxis } from "recharts";
import { api } from "../../api.js";
import MethodNote from "../../components/MethodNote.jsx";
import InterpretationGuide from "../../components/InterpretationGuide.jsx";
import MethodDisclaimer from "../../components/MethodDisclaimer.jsx";
import HistoryPanel from "../../components/HistoryPanel.jsx";
import ReportExport from "../../components/ReportExport.jsx";
import ResultPageTemplate from "../../components/ResultPageTemplate.jsx";
import { saveToHistory, loadHistory, clearHistory } from "../../history.js";
import { h3Outcome } from "../../outcomes.js";
import { formatGeneratedAt, methodMarkdown, interpretationMarkdown, disclaimerMarkdown, slugify } from "../../report.js";
import { HYPOTHESES } from "../../data/hypotheses.js";
import { H3_PHENOMENA, H3_UNAVAILABLE, H3_SUMMARY, H3_REFRESHED_AT } from "../../data/bilanPublie.js";
import VerdictBadge from "../../components/VerdictBadge.jsx";

const HISTORY_PAGE = "h3";
const METHOD_KEYS = ["h3_joint"];

function buildH3Markdown(result) {
  const lines = [
    `# H3 — Indicateur joint : ${result.phenomenon_label}`,
    "",
    `Rapport généré le ${formatGeneratedAt()} par Hélios.`,
    "",
    result.phenomenon_description,
    "",
    "## Verdict",
    "",
    result.verdict_simple,
    "",
    "## Statistiques",
    "",
    `- tau national : ${result.observed_national_tau?.toFixed(3) ?? "n/a"}`,
    `- Indice de Moran : ${result.observed_spatial_i?.toFixed(3) ?? "n/a"} (trimestre le plus proche : ${result.nearest_spatial_quarter ?? "n/a"})`,
    `- p temporel (rang) : ${result.p_temporal_rank?.toFixed(3) ?? "n/a"}`,
    `- p spatial (rang) : ${result.p_spatial_rank?.toFixed(3) ?? "n/a"}`,
    `- T (Fisher) : ${result.t_observed?.toFixed(3) ?? "n/a"}`,
    `- p_joint : ${result.p_joint?.toFixed(3) ?? "n/a"} (sur ${result.n_historical_windows} trimestres comparables, 2000-2026)`,
    "",
    "## Méthode",
    "",
    methodMarkdown("h3_joint"),
    interpretationMarkdown("h3", h3Outcome(result)),
    disclaimerMarkdown(result.n_episodes_tested, result.causal_disclaimer),
  ];
  return lines.join("\n");
}

const H3_DATA = HYPOTHESES.find((h) => h.code === "H3");

export default function H3Result() {
  const [phenomena, setPhenomena] = useState([]);
  const [code, setCode] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [expertMode, setExpertMode] = useState(false);
  const [history, setHistory] = useState([]);

  useEffect(() => {
    api.getPhenomena().then((list) => {
      setPhenomena(list);
      if (list.length) setCode(list[0].code);
    });
    setHistory(loadHistory(HISTORY_PAGE));
  }, []);

  const run = () => {
    if (!code) return;
    setLoading(true);
    setError(null);
    setResult(null);
    api
      .testH3(code)
      .then((r) => {
        setResult(r);
        saveToHistory(HISTORY_PAGE, { code, result: r });
        setHistory(loadHistory(HISTORY_PAGE));
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  };

  const selected = phenomena.find((p) => p.code === code);

  const scatterData = result?.historical_points
    .filter((p) => p.national_tau !== null && p.spatial_i !== null)
    .map((p) => ({ x: p.national_tau, y: p.spatial_i, date: p.date })) ?? [];
  const observedPoint = result
    ? [{ x: result.observed_national_tau, y: result.observed_spatial_i, date: result.nearest_spatial_quarter }]
    : [];

  return (
    <ResultPageTemplate
      code="H3"
      title="Indicateur joint"
      catchyTitle={H3_DATA.catchyTitle}
      domain={{ name: "Société", to: "/resultats#societe" }}
      verdict="preliminary"
      nEpisodes={H3_SUMMARY.nCalculable}
      summary="Combiner un signal temporel (confiance des ménages, national) et un signal spatial (indice de Moran) réduit-il les faux positifs par rapport à chaque signal pris seul ? Calculable sur 4 phénomènes sur 6 -- 1 favorable."
      postulateSimple={H3_DATA.simple}
      postulateExpert={H3_DATA.expert}
      resultText={
        <>
          <p className="text-muted">Rafraîchi automatiquement le {H3_REFRESHED_AT} (Insee, dernier trimestre disponible).</p>
          <div className="table-scroll">
            <table className="agg-table">
              <thead>
                <tr>
                  <th>Phénomène</th>
                  <th>τ national</th>
                  <th>Moran</th>
                  <th>p_joint</th>
                  <th>Verdict</th>
                </tr>
              </thead>
              <tbody>
                {H3_PHENOMENA.map((p) => (
                  <tr key={p.label}>
                    <td>{p.label}</td>
                    <td>{p.tau.toFixed(3)}</td>
                    <td>{p.moran.toFixed(3)}</td>
                    <td>{p.pJoint.toFixed(3)}</td>
                    <td><VerdictBadge outcome={p.sig ? "favorable" : "neutral"} /></td>
                  </tr>
                ))}
                {H3_UNAVAILABLE.map((p) => (
                  <tr key={p.label}>
                    <td>{p.label}</td>
                    <td colSpan={3} className="text-muted" style={{ fontSize: "0.82rem" }}>{p.reason}</td>
                    <td><VerdictBadge outcome="na" /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p className="text-muted">On compare le phénomène testé à chacun des trimestres comparables des 26 dernières années.</p>
        </>
      }
      methodLink={{ to: "/methode/cours-statistiques#fisher", label: "Voir la démonstration (méthode de Fisher/Brown)" }}
      limits={[
        "4 phénomènes calculables reste sous le seuil de 5 épisodes du §5.7 : résultat préliminaire.",
        "La composante spatiale est un instantané (le trimestre le plus proche), pas une tendance -- le chômage départemental n'est publié qu'au trimestre.",
        "La loi nulle jointe est calibrée par comparaison à l'historique réel 2000-2026 plutôt que par surrogates synthétiques couplés -- adaptation documentée.",
      ]}
      journalLink={{ to: "/journal", label: "Voir le Journal de recherche (postulat testé en amont de H3)" }}
    >
      <p className="lede">
        Adaptation assumée par rapport au §5.6 : la composante spatiale est un instantané (le chômage
        départemental n'est publié que trimestriellement, insuffisant pour une vraie tendance sur la fenêtre
        d'un phénomène), et la loi nulle est calibrée sur l'historique réel plutôt que sur des données de
        substitution synthétiques.
      </p>

      <div className="controls">
        <label>
          Phénomène
          <select value={code} onChange={(e) => setCode(e.target.value)}>
            {phenomena.map((p) => (
              <option key={p.code} value={p.code}>
                {p.label}
              </option>
            ))}
          </select>
        </label>
        <button className="cta" onClick={run} disabled={loading || !code}>
          {loading ? "Calcul en cours…" : "Tester la combinaison"}
        </button>
      </div>

      <HistoryPanel
        entries={history}
        onSelect={(entry) => {
          setCode(entry.code);
          setResult(entry.result);
        }}
        onClear={() => {
          clearHistory(HISTORY_PAGE);
          setHistory([]);
        }}
        renderLabel={(e) => `${e.result.phenomenon_label} · p_joint=${e.result.p_joint?.toFixed(3) ?? "n/a"}`}
      />

      {selected && !result && <p className="source-note">{selected.description}</p>}
      {error && <p className="error">{error}</p>}

      {result && (
        <>
          <h2>{result.phenomenon_label}</h2>
          <p className="source-note">{result.phenomenon_description}</p>

          <div className="signal-block">
            <div className="result-card-header">
              <h3>Position du phénomène face aux {result.n_historical_windows} trimestres comparables</h3>
              <button type="button" className="mode-toggle" onClick={() => setExpertMode((v) => !v)} aria-pressed={expertMode}>
                {expertMode ? "Mode simplifié" : "Mode expert"}
              </button>
            </div>

            <ResponsiveContainer width="100%" height={280}>
              <ScatterChart margin={{ top: 10, right: 20, bottom: 10, left: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
                <XAxis type="number" dataKey="x" name="tendance nationale" tick={{ fontSize: 10 }} />
                <YAxis type="number" dataKey="y" name="indice de Moran" tick={{ fontSize: 10 }} />
                <ZAxis range={[40, 41]} />
                <Tooltip cursor={{ strokeDasharray: "3 3" }} formatter={(v) => v.toFixed(3)} />
                <Scatter name="Historique (2000-2026)" data={scatterData} fill="var(--color-border)" />
                <Scatter name="Phénomène testé" data={observedPoint} fill="var(--color-warn)" shape="star" />
              </ScatterChart>
            </ResponsiveContainer>

            {!expertMode && (
              <>
                <p className={result.significant_at_0_05 ? "moran-sig-yes" : "moran-sig-no"}>
                  {result.significant_at_0_05
                    ? "Ce phénomène se démarque nettement du nuage historique : les deux signaux sont inhabituels en même temps."
                    : "Ce phénomène reste dans le nuage habituel de l'historique : rien d'exceptionnel sur la combinaison des deux signaux."}
                </p>
                <MethodNote methodKeys={METHOD_KEYS} expertMode={false} />
              </>
            )}

            {expertMode && (
              <>
                <dl className="signal-stats">
                  <div>
                    <dt>tau national</dt>
                    <dd>{result.observed_national_tau?.toFixed(3)}</dd>
                  </div>
                  <div>
                    <dt>Moran (I)</dt>
                    <dd>{result.observed_spatial_i?.toFixed(3)}</dd>
                  </div>
                  <div>
                    <dt>p temporel (rang)</dt>
                    <dd>{result.p_temporal_rank?.toFixed(3)}</dd>
                  </div>
                  <div>
                    <dt>p spatial (rang)</dt>
                    <dd>{result.p_spatial_rank?.toFixed(3)}</dd>
                  </div>
                  <div>
                    <dt>T (Fisher)</dt>
                    <dd>{result.t_observed?.toFixed(3)}</dd>
                  </div>
                  <div>
                    <dt>p_joint</dt>
                    <dd>{result.p_joint?.toFixed(3)}</dd>
                  </div>
                </dl>
                <MethodNote methodKeys={METHOD_KEYS} expertMode={true} />
              </>
            )}
          </div>

          <div className="h1-verdict">
            <p>{result.verdict_simple}</p>
          </div>

          <InterpretationGuide hypothesis="h3" outcome={h3Outcome(result)} />

          <MethodDisclaimer nEpisodes={result.n_episodes_tested} />

          <ReportExport buildMarkdown={() => buildH3Markdown(result)} filenameBase={`helios-h3-${slugify(result.phenomenon_label)}`} />
        </>
      )}
    </ResultPageTemplate>
  );
}
