import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../../api.js";
import MethodNote from "../../components/MethodNote.jsx";
import ResultPageTemplate from "../../components/ResultPageTemplate.jsx";
import VerdictBadge from "../../components/VerdictBadge.jsx";
import { saveToHistory, loadHistory, clearHistory } from "../../history.js";
import HistoryPanel from "../../components/HistoryPanel.jsx";
import { PLASMA_RESULT } from "../../data/bilanPublie.js";

const HISTORY_PAGE = "plasma";
const HISTORY_PAGE_AGGREGATE = "plasma_aggregate";
const METHOD_KEYS = ["plasma_power_balance"];

function runVerdict(scenario, precursor) {
  if (scenario === "ignited") return precursor ? "favorable" : "against";
  return precursor ? "against" : "neutral";
}

function aggregateVerdict(agg) {
  const hitRate = agg.nIgnited > 0 ? agg.nIgnitedWithPrecursor / agg.nIgnited : 0;
  const falsePositiveRate = agg.nStable > 0 ? agg.nStableFalsePositive / agg.nStable : 0;
  if (hitRate === 0) return "against";
  if (hitRate >= 0.5 && falsePositiveRate < 0.5) return "favorable";
  return "neutral";
}

function FrozenRunRow({ run }) {
  return (
    <tr>
      <td>{run.seed}</td>
      <td>{run.scenario === "ignited" ? "Ignité" : "Stable"}</td>
      <td>{run.tIgnition !== null ? `${run.tIgnition.toFixed(3)} s` : "—"}</td>
      <td>{run.peakTemperatureKev.toFixed(2)} keV</td>
      <td>{run.varianceSig ? "Oui" : "Non"}</td>
      <td>{run.ac1Sig ? "Oui" : "Non"}</td>
      <td>
        <VerdictBadge outcome={runVerdict(run.scenario, run.precursor)} />
      </td>
    </tr>
  );
}

function LiveRunRow({ run }) {
  return (
    <tr>
      <td>{run.seed}</td>
      <td>{run.scenario === "ignited" ? "Ignité" : "Stable"}</td>
      <td>{run.t_ignition !== null ? `${run.t_ignition.toFixed(3)} s` : "—"}</td>
      <td>{run.peak_temperature_kev.toFixed(2)} keV</td>
      <td>{run.variance_significance.significant_at_0_05 ? "Oui" : "Non"}</td>
      <td>{run.ac1_significance.significant_at_0_05 ? "Oui" : "Non"}</td>
      <td>
        <VerdictBadge outcome={runVerdict(run.scenario, run.precursor_before_ignition)} />
      </td>
    </tr>
  );
}

export default function PlasmaModeleResult() {
  const [seed, setSeed] = useState("0");
  const [scenario, setScenario] = useState("ignited");
  const [runResult, setRunResult] = useState(null);
  const [runLoading, setRunLoading] = useState(false);
  const [runError, setRunError] = useState(null);
  const [history, setHistory] = useState([]);

  const [aggregate, setAggregate] = useState(null);
  const [aggregateLoading, setAggregateLoading] = useState(false);
  const [aggregateError, setAggregateError] = useState(null);
  const [aggregateHistory, setAggregateHistory] = useState([]);

  useEffect(() => {
    setHistory(loadHistory(HISTORY_PAGE));
    setAggregateHistory(loadHistory(HISTORY_PAGE_AGGREGATE));
  }, []);

  const runOne = () => {
    setRunLoading(true);
    setRunError(null);
    setRunResult(null);
    api
      .testPlasmaRun({ seed, scenario })
      .then((r) => {
        setRunResult(r);
        saveToHistory(HISTORY_PAGE, { seed, scenario, result: r });
        setHistory(loadHistory(HISTORY_PAGE));
      })
      .catch((e) => setRunError(e.message))
      .finally(() => setRunLoading(false));
  };

  const runAggregate = () => {
    setAggregateLoading(true);
    setAggregateError(null);
    setAggregate(null);
    api
      .testPlasmaAggregate()
      .then((r) => {
        setAggregate(r);
        saveToHistory(HISTORY_PAGE_AGGREGATE, { result: r });
        setAggregateHistory(loadHistory(HISTORY_PAGE_AGGREGATE));
      })
      .catch((e) => setAggregateError(e.message))
      .finally(() => setAggregateLoading(false));
  };

  return (
    <ResultPageTemplate
      code="Plasma"
      title="Modèle réduit de physique des plasmas — seuil d'ignition"
      catchyTitle="Le seuil où le feu s'auto-entretient"
      domain={{ name: "Fusion nucléaire", to: "/resultats#fusion" }}
      verdict={PLASMA_RESULT.verdict}
      episodesLabel={`${PLASMA_RESULT.nRuns} réalisations analysées (${PLASMA_RESULT.nIgnited} ignitées, ${PLASMA_RESULT.nStable} stables)`}
      summary="À quel moment précis un plasma de fusion s'embrase-t-il tout seul ? Sur 10 réalisations d'un modèle réduit de physique des plasmas (bilan de puissance 0-D, critère de Lawson) qui traversent le seuil critique, les 10 montrent un signal précurseur -- mais aucune des 10 réalisations de contrôle (chauffage sous le seuil) ne déclenche de faux positif. Même moteur statistique que le reste du projet (variance, autocorrélation, test par données de substitution), ni donnée réelle mesurée (contrairement à Fusion) ni analogie sociale (contrairement à H4)."
      postulateSimple="Est-ce que l'approche d'un seuil d'ignition -- le moment où un plasma de fusion s'auto-entretient -- se détecte statistiquement avant d'être franchi, dans un vrai modèle physique réduit (pas une donnée mesurée, pas une analogie, une vraie équation de bilan de puissance) ?"
      postulateExpert="Réplication du moteur statistique du reste du projet (variance/AC1 glissantes + test par données de substitution, §5.1/5.4) sur la température d'un modèle 0-D de bilan de puissance (Freidberg 2007 ; Wesson 2004) intégré par Euler-Maruyama, chauffage externe ramené lentement au-delà du seuil critique -- une bifurcation nœud-col bien réelle (le critère de Lawson, 1957), même structure mathématique que celle déjà validée pour le domaine Société au §5.6quater/quinquies du Journal de recherche, mais ici sans transposition sociale (§7quater)."
      resultText={
        <>
          <dl className="signal-stats">
            <div>
              <dt>Réalisations ignitées avec précurseur</dt>
              <dd>{PLASMA_RESULT.nIgnitedWithPrecursor}/{PLASMA_RESULT.nIgnited}</dd>
            </div>
            <div>
              <dt>Faux positifs (réalisations stables)</dt>
              <dd>{PLASMA_RESULT.nStableFalsePositive}/{PLASMA_RESULT.nStable}</dd>
            </div>
          </dl>
          <div className="table-scroll">
            <table className="agg-table">
              <thead>
                <tr>
                  <th>Graine</th>
                  <th>Scénario</th>
                  <th>t_ignition</th>
                  <th>T pic</th>
                  <th>Variance sig.</th>
                  <th>AC1 sig.</th>
                  <th>Verdict</th>
                </tr>
              </thead>
              <tbody>
                {PLASMA_RESULT.runs.map((r) => (
                  <FrozenRunRow key={r.seed} run={r} />
                ))}
              </tbody>
            </table>
          </div>
          <p className="text-muted">
            Signal porté presque entièrement par la variance -- l'autocorrélation (AC1) ne devient
            significative sur aucune réalisation, cohérent avec le constat déjà fait au §5.6quater du{" "}
            <Link to="/journal">Journal de recherche</Link> (la variance y était un détecteur nettement plus
            sensible que l'AC1). Détail complet sur <Link to="/bilan">la page Bilan</Link>.
          </p>
        </>
      }
      methodLink={{ to: "/methode/cours-statistiques", label: "Voir le cours de statistiques (méthode commune à H1/Fusion)" }}
      limits={[
        "Contrairement aux données réelles et bruitées de H1/Fusion, ce modèle produit un emballement quasi déterministe une fois le seuil franchi -- la détection quasi parfaite (10/10) reflète la netteté du phénomène physique modélisé, pas une performance exceptionnelle de la méthode statistique en elle-même.",
        "Modèle réduit illustratif (bilan de puissance 0-D) -- pas une simulation de réacteur complet : aucune magnétohydrodynamique, aucun profil spatial de température ou de densité. Paramètres (densité, temps de confinement) choisis pour faire apparaître une vraie bifurcation en quelques secondes de temps simulé, pas ceux d'une machine réelle précise.",
        "Aucune donnée mesurée : contrairement au module Fusion (§7ter, données réelles MAST), ce module ne teste rien contre une observation réelle -- une simulation Monte-Carlo d'une équation physique, comme H4, mais avec une vraie physique plutôt qu'une analogie sociale.",
        "Détection uniquement : ce module ne conçoit aucun système de contrôle réel de plasma. Toute mention du RCA (roman) reste une note conceptuelle hors périmètre, jamais une conception fonctionnelle applicable à un vrai réacteur.",
        "Résultats présentés séparément des domaines socio-territorial (H1-H5) et Fusion (§7ter, données réelles de tokamak), jamais combinés en un verdict unique.",
      ]}
      journalLink={{ to: "/journal", label: "Voir le Journal de recherche (même protocole que H1)" }}
    >
      <p className="lede">
        Domaine Fusion nucléaire, aux côtés du module Fusion (données réelles de tokamak) : une température
        simulée par un vrai modèle réduit de physique des plasmas, jamais combinée aux résultats d'un autre
        domaine ou module dans un même verdict.
      </p>

      <div className="simulation-banner">
        <strong>Le modèle physique :</strong>
        <span>
          L'énergie du plasma évolue selon dW/dt = P_chauffage + P_fusion(T) − W/τ_E − P_rayonnement(T), avec
          P_fusion paramétrée par la réactivité de Bosch &amp; Hale (1992) et P_rayonnement le rayonnement de
          freinage standard. À chauffage externe fixe, un point d'équilibre stable existe à basse
          température ; si le chauffage augmente lentement, ce point et un point instable associé finissent
          par fusionner et disparaître (bifurcation nœud-col, le vrai critère d'ignition de Lawson) --
          au-delà, la température s'emballe.
        </span>
      </div>
      <MethodNote methodKeys={METHOD_KEYS} expertMode={true} />

      <div className="controls">
        <label>
          Scénario
          <select value={scenario} onChange={(e) => setScenario(e.target.value)}>
            <option value="ignited">Ignité (chauffage traverse le seuil)</option>
            <option value="stable">Stable (contrôle, chauffage sous le seuil)</option>
          </select>
        </label>
        <label>
          Graine
          <input type="number" value={seed} onChange={(e) => setSeed(e.target.value)} />
        </label>
        <button className="cta" onClick={runOne} disabled={runLoading}>
          {runLoading ? "Simulation en cours…" : "Lancer une simulation en direct"}
        </button>
      </div>

      <HistoryPanel
        entries={history}
        onSelect={(entry) => {
          setSeed(entry.seed);
          setScenario(entry.scenario);
          setRunResult(entry.result);
        }}
        onClear={() => {
          clearHistory(HISTORY_PAGE);
          setHistory([]);
        }}
        renderLabel={(e) => `Graine ${e.seed} — ${e.scenario === "ignited" ? "ignité" : "stable"}`}
      />

      {runError && <p className="error">{runError}</p>}

      {runResult && (
        <>
          <div className="result-card-header">
            <h2>
              Graine {runResult.seed} ({runResult.scenario === "ignited" ? "ignité" : "stable"}) —{" "}
              {runResult.ignited ? `ignition à t=${runResult.t_ignition.toFixed(3)} s` : "reste stable"}
            </h2>
          </div>
          <dl className="signal-stats">
            <div>
              <dt>Température pic</dt>
              <dd>{runResult.peak_temperature_kev.toFixed(2)} keV</dd>
            </div>
            <div>
              <dt>Points analysés</dt>
              <dd>{runResult.n_points_analyzed}</dd>
            </div>
          </dl>
          <table className="agg-table">
            <thead>
              <tr>
                <th>Indicateur</th>
                <th>τ observé</th>
                <th>p-value</th>
                <th>Significatif</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>Variance (température)</td>
                <td>{runResult.variance_significance.observed_tau?.toFixed(3) ?? "n/a"}</td>
                <td>{runResult.variance_significance.p_value?.toFixed(3) ?? "n/a"}</td>
                <td>
                  <VerdictBadge outcome={runResult.variance_significance.significant_at_0_05 ? "favorable" : "neutral"} />
                </td>
              </tr>
              <tr>
                <td>AC1 (température)</td>
                <td>{runResult.ac1_significance.observed_tau?.toFixed(3) ?? "n/a"}</td>
                <td>{runResult.ac1_significance.p_value?.toFixed(3) ?? "n/a"}</td>
                <td>
                  <VerdictBadge outcome={runResult.ac1_significance.significant_at_0_05 ? "favorable" : "neutral"} />
                </td>
              </tr>
            </tbody>
          </table>
          <p className="source-note">{runResult.verdict_simple}</p>
        </>
      )}

      <hr className="divider" />
      <h2>Relancer la batterie complète en direct</h2>
      <p className="text-muted">
        Refait 10 réalisations ignitées + 10 réalisations stables (contrôle) et leur test de significativité --
        exactement comme pour produire le tableau figé ci-dessus, avec de nouvelles graines.
      </p>
      <button className="cta secondary" onClick={runAggregate} disabled={aggregateLoading}>
        {aggregateLoading ? "Calcul en cours…" : "Relancer la batterie en direct"}
      </button>

      <HistoryPanel
        entries={aggregateHistory}
        onSelect={(entry) => setAggregate(entry.result)}
        onClear={() => {
          clearHistory(HISTORY_PAGE_AGGREGATE);
          setAggregateHistory([]);
        }}
        renderLabel={(e) => `${e.result.n_ignited_with_precursor}/${e.result.n_ignited} précurseurs, ${e.result.n_stable_false_positive}/${e.result.n_stable} faux positifs`}
      />

      {aggregateError && <p className="error">{aggregateError}</p>}

      {aggregate && (
        <>
          <div className="result-card-header">
            <h2>Résultat en direct</h2>
            <VerdictBadge outcome={aggregateVerdict(aggregate)} />
          </div>
          <p className="source-note">{aggregate.verdict_simple}</p>
          <div className="table-scroll">
            <table className="agg-table">
              <thead>
                <tr>
                  <th>Graine</th>
                  <th>Scénario</th>
                  <th>t_ignition</th>
                  <th>T pic</th>
                  <th>Variance sig.</th>
                  <th>AC1 sig.</th>
                  <th>Verdict</th>
                </tr>
              </thead>
              <tbody>
                {aggregate.runs.map((r) => (
                  <LiveRunRow key={`${r.scenario}-${r.seed}`} run={r} />
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}

      <div className="simulation-banner">
        <strong>Rappel :</strong>
        <span>
          Détection uniquement -- aucun système de contrôle réel de plasma n'est simulé ni conçu ici. Toute
          mention du RCA reste une note conceptuelle, hors périmètre de ce module.{" "}
          <Link to="/roman">Voir le roman</Link> pour le contexte narratif du RCA.
        </span>
      </div>
    </ResultPageTemplate>
  );
}
