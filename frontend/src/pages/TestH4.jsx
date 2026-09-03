import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { CartesianGrid, Line, LineChart, ReferenceLine, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { api } from "../api.js";
import MethodNote from "../components/MethodNote.jsx";
import HistoryPanel from "../components/HistoryPanel.jsx";
import { saveToHistory, loadHistory, clearHistory } from "../history.js";

const HISTORY_PAGE = "h4";
const METHOD_KEYS = ["kuramoto_h4"];

function RChart({ label, trace, refValue, refLabel, color, yDomain = [0, 1] }) {
  const data = trace.time.map((t, i) => ({ t, r: trace.values[i] }));
  return (
    <div className="series-chart">
      <div className="series-chart-label">{label}</div>
      <ResponsiveContainer width="100%" height={220}>
        <LineChart data={data} margin={{ top: 8, right: 16, bottom: 0, left: -16 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
          <XAxis dataKey="t" tick={{ fontSize: 10 }} label={{ value: "temps (u.a.)", position: "insideBottom", offset: -2, fontSize: 10 }} />
          <YAxis domain={yDomain} tick={{ fontSize: 10 }} width={32} />
          <Tooltip formatter={(v) => v.toFixed(3)} labelFormatter={(t) => `t=${t.toFixed(1)}`} />
          {typeof refValue === "number" && (
            <ReferenceLine y={refValue} stroke="var(--color-sim)" strokeDasharray="4 2" label={{ value: refLabel, fontSize: 10, fill: "var(--color-sim)" }} />
          )}
          <Line type="monotone" dataKey="r" stroke={color} dot={false} strokeWidth={2} isAnimationActive={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

export default function TestH4() {
  const [params, setParams] = useState({ n_oscillators: 40, coupling_k: 3.0, r_threshold: 0.5, beta: 2.0, duration: 30 });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [expertMode, setExpertMode] = useState(false);
  const [history, setHistory] = useState([]);

  useEffect(() => {
    setHistory(loadHistory(HISTORY_PAGE));
  }, []);

  const setParam = (key) => (e) => setParams((p) => ({ ...p, [key]: Number(e.target.value) }));

  const run = () => {
    setLoading(true);
    setError(null);
    setResult(null);
    api
      .simulateH4(params)
      .then((r) => {
        setResult(r);
        saveToHistory(HISTORY_PAGE, { params, result: r });
        setHistory(loadHistory(HISTORY_PAGE));
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  };

  return (
    <div className="page page-test-h4">
      <h1>H4 : contrôle actif de la synchronisation (inspiré du RCA)</h1>

      <div className="simulation-banner">
        <strong>Simulation pédagogique — pas un test statistique.</strong>
        <span>
          Contrairement à H1, H2 et H3, H4 ne compare rien à des données réelles. C'est une démonstration de
          principe sur un modèle mathématique (Kuramoto) : elle illustre un mécanisme possible, elle ne le
          prouve pas dans le monde réel. Aucun résultat ci-dessous n'est un verdict « confirmée / infirmée ».
        </span>
      </div>

      <p className="lede">
        N oscillateurs de phase, chacun avec son propre rythme naturel, couplés entre eux avec une force K.
        Au-delà d'un seuil critique K_c, ils basculent brutalement dans un rythme commun (paramètre d'ordre{" "}
        <em>r</em> → 1). Un couplage adaptatif par paire, qui s'affaiblit localement quand une paire se
        verrouille en phase, peut-il empêcher cette bascule sans réduire l'activité individuelle à zéro
        (<em>r</em> maintenu sous un seuil r_c) ?{" "}
        <Link to="/donnees">Voir la démonstration complète</Link>.
      </p>

      <div className="controls">
        <label>
          N oscillateurs
          <input type="number" min={10} max={100} value={params.n_oscillators} onChange={setParam("n_oscillators")} />
        </label>
        <label>
          Couplage K
          <input type="number" min={0.1} max={20} step={0.1} value={params.coupling_k} onChange={setParam("coupling_k")} />
        </label>
        <label>
          Seuil r_c
          <input type="number" min={0.05} max={0.95} step={0.05} value={params.r_threshold} onChange={setParam("r_threshold")} />
        </label>
        <label>
          β (force du contrôle)
          <input type="number" min={0.1} max={20} step={0.1} value={params.beta} onChange={setParam("beta")} />
        </label>
        <label>
          Durée (u.a.)
          <input type="number" min={2} max={100} step={1} value={params.duration} onChange={setParam("duration")} />
        </label>
        <button className="cta" onClick={run} disabled={loading}>
          {loading ? "Simulation en cours…" : "Lancer la simulation"}
        </button>
      </div>

      <HistoryPanel
        entries={history}
        onSelect={(entry) => {
          setParams(entry.params);
          setResult(entry.result);
        }}
        onClear={() => {
          clearHistory(HISTORY_PAGE);
          setHistory([]);
        }}
        renderLabel={(e) => `N=${e.params.n_oscillators}, K=${e.params.coupling_k}, β=${e.params.beta}`}
      />

      {error && <p className="error">{error}</p>}

      {result && (
        <>
          <div className="result-card-header">
            <h2>K choisi = {result.coupling_k} · K_c théorique = {result.critical_coupling}</h2>
            <button type="button" className="mode-toggle" onClick={() => setExpertMode((v) => !v)} aria-pressed={expertMode}>
              {expertMode ? "Mode simplifié" : "Mode expert"}
            </button>
          </div>
          <p className="source-note">
            {result.coupling_k > result.critical_coupling
              ? "K est au-dessus du seuil critique : sans contrôle, le système bascule vers la synchronisation."
              : "K est en dessous du seuil critique : même sans contrôle, le système resterait incohérent -- augmentez K pour observer une vraie bascule à contrôler."}
          </p>

          <div className="result-grid">
            <div className="signal-block">
              <RChart label="Sans contrôle (K fixe)" trace={result.r_uncontrolled} refValue={result.r_threshold} refLabel="r_c" color="var(--color-warn)" />
              <dl className="signal-stats">
                <div>
                  <dt>r moyen (régime établi)</dt>
                  <dd>{result.r_mean_uncontrolled}</dd>
                </div>
                <div>
                  <dt>r final</dt>
                  <dd>{result.r_final_uncontrolled}</dd>
                </div>
              </dl>
            </div>
            <div className="signal-block">
              <RChart label="Avec contrôle adaptatif" trace={result.r_controlled} refValue={result.r_threshold} refLabel="r_c" color="var(--color-sim)" />
              <dl className="signal-stats">
                <div>
                  <dt>r moyen (régime établi)</dt>
                  <dd>{result.r_mean_controlled}</dd>
                </div>
                <div>
                  <dt>r final</dt>
                  <dd>{result.r_final_controlled}</dd>
                </div>
              </dl>
            </div>
          </div>

          <p className="source-note">
            {result.r_mean_controlled < result.r_mean_uncontrolled
              ? `Sur cette simulation, le contrôle adaptatif maintient r nettement plus bas (${result.r_mean_controlled} contre ${result.r_mean_uncontrolled} sans contrôle) -- même perturbations, même graine aléatoire, seule la règle de couplage change.`
              : "Sur cette simulation, le contrôle n'a pas réduit la synchronisation par rapport au cas non contrôlé -- essayez d'augmenter β ou de réduire K."}
          </p>

          {expertMode && (
            <>
              <div className="chart-box">
                <RChart
                  label="Couplage moyen effectif K̄(t) sous contrôle adaptatif (K_base en pointillé)"
                  trace={result.mean_coupling_controlled}
                  refValue={result.coupling_k}
                  refLabel="K_base"
                  color="var(--color-accent)"
                  yDomain={[0, "auto"]}
                />
              </div>
              <dl className="signal-stats">
                <div>
                  <dt>N oscillateurs</dt>
                  <dd>{result.n_oscillators}</dd>
                </div>
                <div>
                  <dt>β</dt>
                  <dd>{result.beta}</dd>
                </div>
                <div>
                  <dt>Durée / pas</dt>
                  <dd>{result.duration} / {result.dt}</dd>
                </div>
                <div>
                  <dt>Graine</dt>
                  <dd>{result.seed ?? "aléatoire"}</dd>
                </div>
              </dl>
              <MethodNote methodKeys={METHOD_KEYS} expertMode={true} />
            </>
          )}
          {!expertMode && <MethodNote methodKeys={METHOD_KEYS} expertMode={false} />}

          <div className="simulation-banner">
            <strong>Rappel :</strong>
            <span>{result.simulation_disclaimer}</span>
          </div>
        </>
      )}
    </div>
  );
}
