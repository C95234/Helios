import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api.js";
import SeriesChart from "../components/SeriesChart.jsx";
import ResultCard from "../components/ResultCard.jsx";
import MethodDisclaimer from "../components/MethodDisclaimer.jsx";

function trendGauge(values) {
  const clean = values.filter((v) => v !== null && v !== undefined);
  if (clean.length < 6) return 0;
  const third = Math.floor(clean.length / 3);
  const early = clean.slice(0, third).reduce((a, b) => a + b, 0) / third;
  const late = clean.slice(-third).reduce((a, b) => a + b, 0) / third;
  const growth = (late - early) / (Math.abs(early) + 1e-6);
  return Math.max(0, Math.min(1, growth / 2));
}

export default function Demo() {
  const [seed, setSeed] = useState(42);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    api
      .getDemo(seed)
      .then(setData)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [seed]);

  return (
    <div className="page page-demo">
      <h1>Démo pédagogique : un système simulé qui bascule</h1>
      <p className="lede">
        Aucune donnée réelle ici : une série est simulée pour illustrer le principe. Sa capacité à
        « récupérer » après une perturbation ralentit peu à peu — jusqu'à une bascule (ligne pointillée).
      </p>

      <button className="cta secondary" onClick={() => setSeed((s) => s + 1)}>
        Rejouer avec une autre simulation
      </button>

      {loading && <p>Chargement…</p>}
      {error && <p className="error">{error}</p>}

      {data && (
        <>
          <SeriesChart
            dates={data.dates}
            values={data.values}
            markIndex={data.tipping_index}
            label="Série simulée (la ligne pointillée marque la bascule)"
          />

          <div className="result-grid">
            <ResultCard
              title="Variance glissante"
              simpleSentence="Avant la bascule, la série devient plus agitée : elle s'écarte davantage de sa moyenne récente que d'habitude."
              gaugeValue={trendGauge(data.variance.values)}
              gaugeLabel="Montée de la fébrilité statistique"
              methodKeys={["rolling_variance"]}
              chart={
                <SeriesChart
                  dates={data.variance.dates}
                  values={data.variance.values}
                  markIndex={data.tipping_index}
                  color="var(--color-mid)"
                />
              }
            />

            <ResultCard
              title="Autocorrélation à lag-1 (AC1)"
              simpleSentence="La série met plus de temps à « oublier » ses derniers à-coups : c'est le signe classique du ralentissement critique."
              gaugeValue={trendGauge(data.ac1.values)}
              gaugeLabel="Ralentissement du retour à l'équilibre"
              methodKeys={["rolling_ac1"]}
              chart={
                <SeriesChart
                  dates={data.ac1.dates}
                  values={data.ac1.values}
                  markIndex={data.tipping_index}
                  color="var(--color-accent)"
                />
              }
            />
          </div>

          <p className="hypothesis-link-note">
            Cette série est <strong>simulée</strong>, pas réelle : elle illustre uniquement la brique
            temporelle qui contribuerait à <strong>l'hypothèse H1</strong> (décalage temporel). Dans H1, ce
            même calcul serait fait à la fois sur un signal social et un signal officiel, pour voir lequel
            des deux réagit en premier — étape pas encore disponible dans Hélios.{" "}
            <Link to="/hypotheses">Voir les 3 hypothèses</Link>.
          </p>

          <MethodDisclaimer nEpisodes={1} />
        </>
      )}
    </div>
  );
}
