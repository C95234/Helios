import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api.js";
import SeriesChart from "../components/SeriesChart.jsx";
import ResultCard from "../components/ResultCard.jsx";
import MethodDisclaimer from "../components/MethodDisclaimer.jsx";
import HistoryPanel from "../components/HistoryPanel.jsx";
import { saveToHistory, loadHistory, clearHistory } from "../history.js";

const HISTORY_PAGE = "analyze";

function verdictSentence(sig, label) {
  if (Number.isNaN(sig.observed_tau)) {
    return `Pas assez de points pour évaluer une tendance de ${label} sur cette période.`;
  }
  const direction = sig.observed_tau > 0 ? "augmenté" : "diminué";
  if (sig.significant_at_0_05) {
    return `Le signal de ${label} a ${direction} plus que ce que le hasard seul expliquerait sur cette période (p = ${sig.p_value.toFixed(3)}).`;
  }
  return `Le signal de ${label} a bougé, mais pas plus que ce que le hasard seul peut produire sur cette période (p = ${sig.p_value.toFixed(3)}).`;
}

function h1Reformulation(result) {
  const anySignificant =
    result.variance_significance.significant_at_0_05 || result.ac1_significance.significant_at_0_05;
  const title = result.source_title;
  if (anySignificant) {
    return `Sur « ${title} », le signal officiel montre une hausse significative de fébrilité statistique sur cette période. C'est exactement la moitié de ce que teste l'hypothèse H1 : si Hélios disposait d'un signal social équivalent (réseaux sociaux, recherche en ligne) sur la même période, H1 comparerait lequel des deux réagit en premier — ce connecteur n'existe pas encore.`;
  }
  return `Sur « ${title} », aucun signal officiel significatif n'est détecté sur cette période : cette série ne fournit pas, ici, d'épisode candidat pour tester l'hypothèse H1. Essayez une autre série ou une autre fenêtre, ou consultez la démo pour voir à quoi ressemble un signal qui se déclenche.`;
}

export default function Analyze() {
  const [catalog, setCatalog] = useState([]);
  const [idbank, setIdbank] = useState("");
  const [window_, setWindow] = useState(12);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [history, setHistory] = useState([]);

  useEffect(() => {
    api.getCatalog().then((c) => {
      setCatalog(c);
      if (c.length) setIdbank(c[0].idbank);
    });
    setHistory(loadHistory(HISTORY_PAGE));
  }, []);

  const runAnalysis = () => {
    if (!idbank) return;
    setLoading(true);
    setError(null);
    setResult(null);
    api
      .analyzeInsee(idbank, window_)
      .then((r) => {
        setResult(r);
        saveToHistory(HISTORY_PAGE, { idbank, window: window_, result: r });
        setHistory(loadHistory(HISTORY_PAGE));
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  };

  const restoreFromHistory = (entry) => {
    setIdbank(entry.idbank);
    setWindow(entry.window);
    setResult(entry.result);
    setError(null);
  };

  const clearAnalysisHistory = () => {
    clearHistory(HISTORY_PAGE);
    setHistory([]);
  };

  return (
    <div className="page page-analyze">
      <h1>Analyser une série officielle (INSEE)</h1>
      <p className="lede">
        Données publiques, agrégées, issues de la Banque de données macroéconomiques de l'Insee — accès
        ouvert, sans clé, conforme aux{" "}
        <a href="https://www.insee.fr/fr/information/2862759" target="_blank" rel="noreferrer">
          conditions d'utilisation du service web SDMX de l'Insee
        </a>
        .
      </p>

      <div className="controls">
        <label>
          Série
          <select value={idbank} onChange={(e) => setIdbank(e.target.value)}>
            {catalog.map((c) => (
              <option key={c.idbank} value={c.idbank}>
                {c.title}
              </option>
            ))}
          </select>
        </label>
        <label>
          Fenêtre glissante ({window_} points)
          <input
            type="range"
            min="6"
            max="40"
            value={window_}
            onChange={(e) => setWindow(Number(e.target.value))}
          />
        </label>
        <button className="cta" onClick={runAnalysis} disabled={loading || !idbank}>
          {loading ? "Calcul en cours…" : "Analyser"}
        </button>
      </div>

      <HistoryPanel
        entries={history}
        onSelect={restoreFromHistory}
        onClear={clearAnalysisHistory}
        renderLabel={(e) => `${e.result.source_title} · fenêtre ${e.window}`}
      />

      {error && <p className="error">{error}</p>}

      {result && (
        <>
          <h2>{result.source_title}</h2>
          <p className="source-note">
            {result.n_observations} observations · source : Insee (BDM, accès ouvert)
          </p>

          <SeriesChart dates={result.raw.dates} values={result.raw.values} label="Série brute" />

          <div className="result-grid">
            <ResultCard
              title="Variance glissante"
              simpleSentence={verdictSentence(result.variance_significance, "variance")}
              gaugeValue={result.variance_significance.significant_at_0_05 ? 0.8 : 0.25}
              gaugeLabel="Force du signal (test contre le hasard)"
              methodKeys={["rolling_variance", "kendall_tau", "surrogate_test"]}
              chart={<SeriesChart dates={result.variance.dates} values={result.variance.values} color="var(--color-mid)" />}
              expert={
                <p className="method-numbers">
                  tau de Kendall observé : {result.variance_significance.observed_tau?.toFixed(4)} · p-value :{" "}
                  {result.variance_significance.p_value?.toFixed(4)} ·{" "}
                  {result.variance_significance.n_surrogates} substitutions · fenêtre {result.window} points ·
                  n = {result.variance_significance.n_points}
                </p>
              }
            />

            <ResultCard
              title="Autocorrélation à lag-1 (AC1)"
              simpleSentence={verdictSentence(result.ac1_significance, "l'AC1")}
              gaugeValue={result.ac1_significance.significant_at_0_05 ? 0.8 : 0.25}
              gaugeLabel="Force du signal (test contre le hasard)"
              methodKeys={["rolling_ac1", "kendall_tau", "surrogate_test"]}
              chart={<SeriesChart dates={result.ac1.dates} values={result.ac1.values} color="var(--color-accent)" />}
              expert={
                <p className="method-numbers">
                  tau de Kendall observé : {result.ac1_significance.observed_tau?.toFixed(4)} · p-value :{" "}
                  {result.ac1_significance.p_value?.toFixed(4)} ·{" "}
                  {result.ac1_significance.n_surrogates} substitutions · fenêtre {result.window} points · n ={" "}
                  {result.ac1_significance.n_points}
                </p>
              }
            />
          </div>

          <p className="hypothesis-link-note">
            {h1Reformulation(result)} <Link to="/hypotheses">Voir les 3 hypothèses</Link>.
          </p>

          <MethodDisclaimer nEpisodes={result.n_episodes_tested} />
        </>
      )}
    </div>
  );
}
