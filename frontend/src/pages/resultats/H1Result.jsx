import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../../api.js";
import SeriesChart from "../../components/SeriesChart.jsx";
import MethodDisclaimer from "../../components/MethodDisclaimer.jsx";
import MethodNote from "../../components/MethodNote.jsx";
import InterpretationGuide from "../../components/InterpretationGuide.jsx";
import HistoryPanel from "../../components/HistoryPanel.jsx";
import ReportExport from "../../components/ReportExport.jsx";
import ResultPageTemplate from "../../components/ResultPageTemplate.jsx";
import { saveToHistory, loadHistory, clearHistory } from "../../history.js";
import { h1Outcome } from "../../outcomes.js";
import { formatGeneratedAt, methodMarkdown, interpretationMarkdown, disclaimerMarkdown, slugify } from "../../report.js";
import { HYPOTHESES } from "../../data/hypotheses.js";
import { H1_PHENOMENA, H1_SUMMARY, H1_REFRESHED_AT } from "../../data/bilanPublie.js";
import VerdictBadge from "../../components/VerdictBadge.jsx";

const HISTORY_PAGE = "h1";
const HISTORY_PAGE_AGGREGATE = "h1_aggregate";

const SIGNAL_METHOD_KEYS = ["rolling_variance", "rolling_ac1", "kendall_tau", "surrogate_test"];

function SignalBlock({ analysis, color }) {
  const [expertMode, setExpertMode] = useState(false);
  const anySig = analysis.variance_significance.significant_at_0_05 || analysis.ac1_significance.significant_at_0_05;

  return (
    <div className="signal-block">
      <div className="result-card-header">
        <h3>{analysis.title}</h3>
        <button type="button" className="mode-toggle" onClick={() => setExpertMode((v) => !v)} aria-pressed={expertMode}>
          {expertMode ? "Mode simplifié" : "Mode expert"}
        </button>
      </div>
      <SeriesChart dates={analysis.raw.dates} values={analysis.raw.values} color={color} />

      {!expertMode && (
        <>
          <p className={anySig ? "moran-sig-yes" : "moran-sig-no"}>
            {anySig
              ? `Ce signal devient statistiquement fébrile sur cette période (pic le ${analysis.peak_date}).`
              : "Ce signal ne montre pas de fébrilité statistique marquée sur cette période."}
          </p>
          <MethodNote methodKeys={SIGNAL_METHOD_KEYS} expertMode={false} />
        </>
      )}

      {expertMode && (
        <>
          <dl className="signal-stats">
            <div>
              <dt>Points</dt>
              <dd>{analysis.n_observations}</dd>
            </div>
            <div>
              <dt>Pic d'AC1</dt>
              <dd>{analysis.peak_date ?? "n/a"}</dd>
            </div>
            <div>
              <dt>p (variance)</dt>
              <dd>{analysis.variance_significance.p_value?.toFixed(3) ?? "n/a"}</dd>
            </div>
            <div>
              <dt>p (AC1)</dt>
              <dd>{analysis.ac1_significance.p_value?.toFixed(3) ?? "n/a"}</dd>
            </div>
          </dl>
          <MethodNote methodKeys={SIGNAL_METHOD_KEYS} expertMode={true} />
        </>
      )}
    </div>
  );
}

function AggregateSection() {
  const [agg, setAgg] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [history, setHistory] = useState([]);

  useEffect(() => {
    setHistory(loadHistory(HISTORY_PAGE_AGGREGATE));
  }, []);

  const run = () => {
    setLoading(true);
    setError(null);
    setAgg(null);
    api
      .testH1Aggregate()
      .then((r) => {
        setAgg(r);
        saveToHistory(HISTORY_PAGE_AGGREGATE, { result: r });
        setHistory(loadHistory(HISTORY_PAGE_AGGREGATE));
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  };

  return (
    <div className="aggregate-box">
      <h2>Vue d'ensemble : tous les phénomènes à la fois</h2>
      <p className="text-muted">
        Un seul phénomène ne prouve rien. Ce bouton relance H1 sur les {"6"} phénomènes curatés et compte
        combien vont dans le sens de H1, combien vont contre, combien sont neutres — un indice plus robuste
        qu'un cas isolé, mais toujours pas les 5 épisodes <em>indépendants</em> qu'exige le protocole complet
        (§5.7) : ces phénomènes restent choisis à la main, pas tirés au hasard.
      </p>
      <button className="cta secondary" onClick={run} disabled={loading}>
        {loading ? "Calcul en cours (5-10 minutes, 6 phénomènes × jusqu'à 42 signaux)…" : "Tester tous les phénomènes d'un coup"}
      </button>

      <HistoryPanel
        entries={history}
        onSelect={(entry) => setAgg(entry.result)}
        onClear={() => {
          clearHistory(HISTORY_PAGE_AGGREGATE);
          setHistory([]);
        }}
        renderLabel={(e) => `${e.result.n_favorable_to_h1} favorables / ${e.result.n_against_h1} contre / ${e.result.n_neutral} neutres`}
      />
      {error && <p className="error">{error}</p>}
      {agg && (
        <>
          <div className="agg-summary">
            <div className="agg-stat">
              <span className="agg-number">{agg.n_favorable_to_h1}</span>
              <span>vont dans le sens de H1</span>
            </div>
            <div className="agg-stat">
              <span className="agg-number">{agg.n_against_h1}</span>
              <span>vont à l'encontre de H1</span>
            </div>
            <div className="agg-stat">
              <span className="agg-number">{agg.n_neutral}</span>
              <span>neutres / non concluants</span>
            </div>
          </div>
          <div className="table-scroll">
            <table className="agg-table">
              <thead>
                <tr>
                  <th>Phénomène</th>
                  <th>Officiels sig.</th>
                  <th>Sociaux sig.</th>
                  <th>Écart (jours)</th>
                  <th>Lecture</th>
                </tr>
              </thead>
              <tbody>
                {agg.results.map((r) => (
                  <tr key={r.phenomenon_label}>
                    <td>{r.phenomenon_label}</td>
                    <td>
                      {r.n_official_significant}/{r.official_signals.length}
                    </td>
                    <td>
                      {r.n_social_significant}/{r.social_signals.length}
                    </td>
                    <td>{r.decalage_jours ?? "n/a"}</td>
                    <td>{r.verdict_simple}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {agg.errors.length > 0 && (
            <p className="text-muted">{agg.errors.length} phénomène(s) n'ont pas pu être calculés cette fois.</p>
          )}
          <InterpretationGuide hypothesis="h1" />
        </>
      )}
    </div>
  );
}

function buildH1Markdown(result) {
  const lines = [
    `# H1 — Décalage temporel : ${result.phenomenon_label}`,
    "",
    `Rapport généré le ${formatGeneratedAt()} par Hélios.`,
    "",
    result.phenomenon_description,
    "",
    "## Verdict",
    "",
    result.verdict_simple,
    "",
  ];
  if (result.decalage_jours !== null) {
    lines.push(
      `Écart entre les pics les plus précoces (parmi les signaux significatifs) : ${Math.abs(result.decalage_jours)} jour(s), le signal ${result.decalage_jours > 0 ? "social" : "officiel"} en premier.`,
      ""
    );
  }

  const signalTable = (title, signals) => {
    const rows = [
      `## ${title} (${signals.filter((s) => s.variance_significance.significant_at_0_05 || s.ac1_significance.significant_at_0_05).length}/${signals.length} significatifs)`,
      "",
      "| Signal | Pic AC1 | p (variance) | p (AC1) |",
      "|---|---|---|---|",
    ];
    for (const s of signals) {
      rows.push(`| ${s.title} | ${s.peak_date ?? "n/a"} | ${s.variance_significance.p_value?.toFixed(3) ?? "n/a"} | ${s.ac1_significance.p_value?.toFixed(3) ?? "n/a"} |`);
    }
    rows.push("");
    return rows.join("\n");
  };
  lines.push(signalTable("Signaux officiels", result.official_signals));
  lines.push(signalTable("Signaux sociaux", result.social_signals));

  lines.push("## Méthode", "");
  for (const key of SIGNAL_METHOD_KEYS) lines.push(methodMarkdown(key));

  lines.push(interpretationMarkdown("h1", h1Outcome(result)));
  lines.push(disclaimerMarkdown(result.n_episodes_tested, result.causal_disclaimer));

  return lines.join("\n");
}

// decalageJours > 0 : le signal social a culmine EN AVANCE sur l'officiel (favorable a H1) --
// decalageJours < 0 : l'inverse. Le signe seul ne suffit pas a l'affichage, il faut dire lequel a mene.
function ecartLabel(decalageJours) {
  if (decalageJours === null) return "—";
  if (decalageJours > 0) return `social ${decalageJours} j`;
  if (decalageJours < 0) return `officiel ${-decalageJours} j`;
  return "simultané";
}

const H1_DATA = HYPOTHESES.find((h) => h.code === "H1");

export default function H1Result() {
  const [phenomena, setPhenomena] = useState([]);
  const [code, setCode] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
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
      .testH1(code)
      .then((r) => {
        setResult(r);
        saveToHistory(HISTORY_PAGE, { code, result: r });
        setHistory(loadHistory(HISTORY_PAGE));
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  };

  const restoreFromHistory = (entry) => {
    setCode(entry.code);
    setResult(entry.result);
    setError(null);
  };

  const selected = phenomena.find((p) => p.code === code);

  return (
    <ResultPageTemplate
      code="H1"
      title="Décalage temporel"
      verdict="against"
      nEpisodes={H1_SUMMARY.nPhenomena}
      summary="Les signaux sociaux se déclenchent-ils avant les statistiques officielles, pour un même événement de rupture ? Sur les 6 phénomènes testés, 1 seul va dans ce sens -- 5 vont à l'encontre."
      postulateSimple={H1_DATA.simple}
      postulateExpert={H1_DATA.expert}
      resultText={
        <>
          <p className="text-muted">Rafraîchi automatiquement le {H1_REFRESHED_AT} (Wikipédia + Insee).</p>
          <p>
            Sur les 6 phénomènes testés, chaque fois qu'un écart de timing était mesurable, c'est le signal{" "}
            <strong>officiel</strong> qui a précédé le signal social -- seul le choc sécuritaire pur
            (attentats 2015, aucune série économique officielle significative) va dans le sens de H1.
          </p>
          <div className="table-scroll">
            <table className="agg-table">
              <thead>
                <tr>
                  <th>Phénomène</th>
                  <th>Officiels sig.</th>
                  <th>Sociaux sig.</th>
                  <th>Écart</th>
                  <th>Verdict</th>
                </tr>
              </thead>
              <tbody>
                {H1_PHENOMENA.map((p) => (
                  <tr key={p.label}>
                    <td>{p.label}</td>
                    <td>{p.nOffSig}/{p.nOff}</td>
                    <td>{p.nSocSig}/{p.nSoc}</td>
                    <td>{ecartLabel(p.decalageJours)}</td>
                    <td><VerdictBadge outcome={p.outcome} /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p className="text-muted">
            <strong>Nuance importante :</strong> Wikipédia (et Google Trends, ajouté en complément) sont des
            proxies structurellement réactifs -- ce résultat défavorable peut refléter cette limite plutôt
            qu'une réfutation de l'hypothèse elle-même. Voir le détail complet sur{" "}
            <Link to="/bilan">la page Bilan</Link>.
          </p>
        </>
      }
      methodLink={{ to: "/methode/cours-statistiques#autocorrelation", label: "Voir la démonstration (autocorrélation, tests par substitution)" }}
      limits={[
        "6 phénomènes choisis à la main (ruptures documentées et datées), pas tirés au hasard -- jamais un échantillon statistiquement représentatif.",
        "La comparaison de timing repose sur la date du pic d'un indicateur, un indice descriptif, pas un test statistique formel de décalage.",
        "Wikipédia (et Google Trends, ajouté en complément) sont des proxies structurellement réactifs -- le résultat défavorable peut refléter cette limite plutôt qu'une réfutation de l'hypothèse elle-même.",
      ]}
      journalLink={{ to: "/journal", label: "Voir le Journal de recherche" }}
    >
      <p className="lede">
        Jusqu'à 39 séries officielles (Insee — ménages, industrie, services, bâtiment, commerce) sont
        comparées à 3 signaux sociaux (attention Wikipédia, éditions, contributeurs distincts), chacun
        testé indépendamment.
      </p>
      <p className="text-muted">
        Ces {phenomena.length || 6} phénomènes sont choisis parce qu'ils sont des ruptures sociales
        documentées et datées (pas des dates arbitraires), et parce que Wikipédia ne couvre que juillet 2015
        et après — c'est pourquoi aucun épisode plus ancien (ex. crise de 2008) n'y figure.
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
          {loading ? "Calcul en cours (30-60s, jusqu'à 42 signaux)…" : "Comparer les signaux"}
        </button>
      </div>

      <HistoryPanel
        entries={history}
        onSelect={restoreFromHistory}
        onClear={() => {
          clearHistory(HISTORY_PAGE);
          setHistory([]);
        }}
        renderLabel={(e) => `${e.result.phenomenon_label} · ${e.result.n_official_significant}+${e.result.n_social_significant} sig.`}
      />

      {selected && !result && <p className="source-note">{selected.description}</p>}
      {error && <p className="error">{error}</p>}

      {result && (
        <>
          <h2>{result.phenomenon_label}</h2>
          <p className="source-note">{result.phenomenon_description}</p>

          <h3 className="signal-group-title">
            Signaux officiels ({result.n_official_significant}/{result.official_signals.length} significatifs)
          </h3>
          <div className="result-grid">
            {result.official_signals.map((s) => (
              <SignalBlock key={s.title} analysis={s} color="var(--color-mid)" />
            ))}
          </div>

          <h3 className="signal-group-title">
            Signaux sociaux ({result.n_social_significant}/{result.social_signals.length} significatifs)
          </h3>
          <div className="result-grid">
            {result.social_signals.map((s) => (
              <SignalBlock key={s.title} analysis={s} color="var(--color-accent)" />
            ))}
          </div>

          <div className="h1-verdict">
            <p>{result.verdict_simple}</p>
            {result.decalage_jours !== null && (
              <p className="h1-decalage">
                Écart entre les pics les plus précoces (parmi les signaux significatifs) :{" "}
                {Math.abs(result.decalage_jours)} jour(s), le signal{" "}
                {result.decalage_jours > 0 ? "social" : "officiel"} en premier.
              </p>
            )}
          </div>

          <InterpretationGuide hypothesis="h1" outcome={h1Outcome(result)} />

          <MethodDisclaimer nEpisodes={result.n_episodes_tested} />

          <ReportExport buildMarkdown={() => buildH1Markdown(result)} filenameBase={`helios-h1-${slugify(result.phenomenon_label)}`} />
        </>
      )}

      <AggregateSection />
    </ResultPageTemplate>
  );
}
