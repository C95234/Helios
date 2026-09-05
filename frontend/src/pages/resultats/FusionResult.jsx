import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../../api.js";
import ResultPageTemplate from "../../components/ResultPageTemplate.jsx";
import VerdictBadge from "../../components/VerdictBadge.jsx";
import { saveToHistory, loadHistory, clearHistory } from "../../history.js";
import HistoryPanel from "../../components/HistoryPanel.jsx";
import { FUSION_RESULT } from "../../data/bilanPublie.js";

const HISTORY_PAGE = "fusion";
const HISTORY_PAGE_AGGREGATE = "fusion_aggregate";

function FrozenShotRow({ shot }) {
  return (
    <tr>
      <td>{shot.shotId}</td>
      <td>{shot.campaign ?? "—"}</td>
      <td>{shot.disrupted ? "Disrupté" : "Stable"}</td>
      <td>{shot.disrupted ? `${shot.tQuench?.toFixed(4)} s` : "—"}</td>
      <td>{shot.peakCurrentKa.toFixed(0)} kA</td>
      <td>{shot.varianceSig ? "Oui" : "Non"}</td>
      <td>{shot.ac1Sig ? "Oui" : "Non"}</td>
      <td>{shot.moranSig ? "Oui" : "Non"}</td>
      <td>
        <VerdictBadge outcome={shot.disrupted ? (shot.precursor ? "favorable" : "against") : shot.precursor ? "against" : "neutral"} />
      </td>
    </tr>
  );
}

function LiveShotRow({ shot }) {
  return (
    <tr>
      <td>{shot.shot_id}</td>
      <td>{shot.campaign ?? "—"}</td>
      <td>{shot.disrupted ? "Disrupté" : "Stable"}</td>
      <td>{shot.disrupted ? `${shot.t_quench?.toFixed(4)} s` : "—"}</td>
      <td>{shot.peak_current_ka.toFixed(0)} kA</td>
      <td>{shot.variance_significance.significant_at_0_05 ? "Oui" : "Non"}</td>
      <td>{shot.ac1_significance.significant_at_0_05 ? "Oui" : "Non"}</td>
      <td>{shot.moran_trend.significant_at_0_05 ? "Oui" : "Non"}</td>
      <td>
        <VerdictBadge outcome={shot.disrupted ? (shot.precursor_before_quench ? "favorable" : "against") : shot.precursor_before_quench ? "against" : "neutral"} />
      </td>
    </tr>
  );
}

export default function FusionResult() {
  const [shotId, setShotId] = useState("");
  const [shotResult, setShotResult] = useState(null);
  const [shotLoading, setShotLoading] = useState(false);
  const [shotError, setShotError] = useState(null);
  const [history, setHistory] = useState([]);

  const [aggregate, setAggregate] = useState(null);
  const [aggregateLoading, setAggregateLoading] = useState(false);
  const [aggregateError, setAggregateError] = useState(null);
  const [aggregateHistory, setAggregateHistory] = useState([]);

  useEffect(() => {
    setHistory(loadHistory(HISTORY_PAGE));
    setAggregateHistory(loadHistory(HISTORY_PAGE_AGGREGATE));
  }, []);

  const runShot = () => {
    if (!shotId) return;
    setShotLoading(true);
    setShotError(null);
    setShotResult(null);
    api
      .testFusionShot(shotId)
      .then((r) => {
        setShotResult(r);
        saveToHistory(HISTORY_PAGE, { shotId, result: r });
        setHistory(loadHistory(HISTORY_PAGE));
      })
      .catch((e) => setShotError(e.message))
      .finally(() => setShotLoading(false));
  };

  const runAggregate = () => {
    setAggregateLoading(true);
    setAggregateError(null);
    setAggregate(null);
    api
      .testFusionAggregate()
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
      code="Fusion"
      title="Détection sur données de tokamak (MAST)"
      verdict={FUSION_RESULT.verdict}
      episodesLabel={`${FUSION_RESULT.nShots} tirs analysés (${FUSION_RESULT.nDisrupted} disruptés, ${FUSION_RESULT.nStable} stables)`}
      summary="Le même pipeline de détection que H1/H2 (variance, autocorrélation et indice de Moran, code inchangé) généralise-t-il à un domaine physique totalement différent -- des données réelles de tokamak (MAST) ? Sur 10 tirs disruptés, 8 montrent un signal précurseur avant le quench -- mais 3 des 10 tirs stables (témoins) montrent aussi un signal jugé significatif, un faux positif à ne pas passer sous silence."
      postulateSimple="Est-ce que les mêmes indicateurs statistiques qui détectent une fébrilité avant une rupture sociale détectent aussi une fébrilité avant une disruption de plasma -- un domaine physique sans aucun rapport avec le socio-territorial ?"
      postulateExpert="Réplication du pipeline H1 (variance/AC1 glissantes + test par données de substitution) et H2 (indice de Moran + test par données de substitution) sur le courant plasma et le réseau des sondes magnétiques d'un tokamak réel (MAST), sans aucune branche de calcul spécifique -- même moteur, deux domaines de données (§7ter)."
      resultText={
        <>
          <p className="text-muted">Rafraîchi automatiquement le {FUSION_RESULT.refreshedAt} (sur la batterie de tirs MAST déjà curatée).</p>
          <dl className="signal-stats">
            <div>
              <dt>Tirs disruptés avec précurseur</dt>
              <dd>{FUSION_RESULT.nDisruptedWithPrecursor}/{FUSION_RESULT.nDisrupted}</dd>
            </div>
            <div>
              <dt>Faux positifs (tirs stables)</dt>
              <dd>{FUSION_RESULT.nStableFalsePositive}/{FUSION_RESULT.nStable}</dd>
            </div>
          </dl>
          <div className="table-scroll">
            <table className="agg-table">
              <thead>
                <tr>
                  <th>Tir</th>
                  <th>Campagne</th>
                  <th>État</th>
                  <th>t_quench</th>
                  <th>I pic</th>
                  <th>Variance sig.</th>
                  <th>AC1 sig.</th>
                  <th>Moran sig.</th>
                  <th>Verdict</th>
                </tr>
              </thead>
              <tbody>
                {FUSION_RESULT.shots.map((s) => (
                  <FrozenShotRow key={s.shotId} shot={s} />
                ))}
              </tbody>
            </table>
          </div>
          <p className="text-muted">
            Détail complet sur <Link to="/bilan">la page Bilan</Link>.
          </p>
        </>
      }
      methodLink={{ to: "/methode/cours-statistiques", label: "Voir le cours de statistiques (méthodes communes à H1/H2)" }}
      limits={[
        "Vérité terrain de disruption dérivée des données MAST elles-mêmes (chute brutale du courant plasma, critère simple) plutôt que d'un jeu de données externe -- DisruptionBench (DIII-D/EAST/Alcator C-Mod) exige des identifiants institutionnels non disponibles, malgré ce qu'indique le cahier des charges. Pas un détecteur de disruption validé cliniquement.",
        "Le taux de faux positifs (30 %) est plus élevé que le seuil nominal de 5 % par indicateur pris isolément -- attendu, puisqu'un tir est compté « précurseur » dès qu'UN SEUL des trois indicateurs (variance, AC1, Moran) est significatif : combiner plusieurs tests sans correction gonfle mécaniquement le taux de faux positifs (comparaisons multiples, voir Garde-fous).",
        "Batterie de 20 tirs curatée à la main (10 disruptés, 10 stables) -- plus solide qu'un cas isolé, mais toujours pas les grands échantillons aléatoires d'un essai clinique.",
        "L'analyse temporelle du courant se limite aux ~400 derniers points avant la coupure (pas tout le tir) -- le courant plasma est échantillonné à ~2 kHz, et calculer l'autocorrélation glissante sur des milliers de points à chaque tirage de substitution serait ingérable ; les points les plus proches du quench sont les plus pertinents pour un signal précurseur de toute façon.",
        "Détection uniquement : ce module ne simule, ne conçoit ni ne propose aucun système de contrôle réel de plasma. Toute mention du RCA (H4) reste une note conceptuelle hors périmètre, jamais une conception fonctionnelle applicable à un vrai tokamak.",
        "Résultats présentés séparément du domaine socio-territorial (H1-H5), jamais combinés en un verdict unique.",
      ]}
      journalLink={{ to: "/journal", label: "Voir le Journal de recherche" }}
    >
      <p className="lede">
        Second domaine d'application, distinct des hypothèses socio-territoriales (H1-H5) : le même moteur de
        calcul, sans aucune branche spécifique, appliqué à des données réelles et ouvertes de tokamak (MAST,
        UKAEA) -- pas une nouvelle méthode, une réplication sur un domaine physique différent.
      </p>

      <div className="simulation-banner">
        <strong>D'où vient cette question :</strong>
        <span>
          Dans le <Link to="/roman">roman</Link> qui a inspiré Hélios, le RCA est un générateur d'énergie
          qui rend la fusion nucléaire maîtrisable -- non pas en supprimant toute turbulence du plasma, mais
          en l'empêchant de se synchroniser en un seul emballement (le même principe de contrôle traduit en
          simulation dans <Link to="/resultats/h4">H4</Link>). C'est précisément parce que le RCA du roman
          opère sur un plasma de fusion que ce second domaine a été choisi : si les indicateurs qui
          détectent une fébrilité avant une bascule sociale (variance, autocorrélation, indice de Moran --
          H1/H2) fonctionnent sur un vrai signal social, se comportent-ils aussi sur le vrai phénomène
          physique que le RCA fictif est censé maîtriser -- une disruption de plasma ? Ce module ne teste
          que cette question de <strong>détection</strong> ; il ne simule ni ne conçoit aucun système de
          contrôle, contrairement au RCA du roman ou à la simulation pédagogique de H4.
        </span>
      </div>

      <div className="controls">
        <label>
          Numéro de tir MAST
          <input type="number" placeholder="ex. 28461" value={shotId} onChange={(e) => setShotId(e.target.value)} />
        </label>
        <button className="cta" onClick={runShot} disabled={shotLoading || !shotId}>
          {shotLoading ? "Analyse en cours…" : "Analyser ce tir en direct"}
        </button>
      </div>
      <p className="text-muted">
        N'importe quel numéro de tir MAST peut être tenté, mais seuls les tirs disposant à la fois du courant
        plasma et des sondes magnétiques dans le catalogue ouvert donneront un résultat -- voir{" "}
        <a href="https://mastapp.site" target="_blank" rel="noreferrer">
          le catalogue MAST
        </a>{" "}
        pour explorer les tirs disponibles.
      </p>

      <HistoryPanel
        entries={history}
        onSelect={(entry) => {
          setShotId(entry.shotId);
          setShotResult(entry.result);
        }}
        onClear={() => {
          clearHistory(HISTORY_PAGE);
          setHistory([]);
        }}
        renderLabel={(e) => `Tir ${e.shotId} — ${e.result.disrupted ? "disrupté" : "stable"}`}
      />

      {shotError && <p className="error">{shotError}</p>}

      {shotResult && (
        <>
          <div className="result-card-header">
            <h2>
              Tir {shotResult.shot_id} ({shotResult.campaign ?? "campagne inconnue"}) —{" "}
              {shotResult.disrupted ? "disrupté" : "stable"}
            </h2>
          </div>
          <dl className="signal-stats">
            <div>
              <dt>Courant pic</dt>
              <dd>{shotResult.peak_current_ka.toFixed(0)} kA</dd>
            </div>
            {shotResult.disrupted && (
              <div>
                <dt>Instant du quench</dt>
                <dd>{shotResult.t_quench?.toFixed(4)} s</dd>
              </div>
            )}
            <div>
              <dt>Points analysés (courant)</dt>
              <dd>{shotResult.n_current_points_analyzed}</dd>
            </div>
            <div>
              <dt>Sondes magnétiques</dt>
              <dd>{shotResult.n_probes}</dd>
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
                <td>Variance (courant)</td>
                <td>{shotResult.variance_significance.observed_tau?.toFixed(3) ?? "n/a"}</td>
                <td>{shotResult.variance_significance.p_value?.toFixed(3) ?? "n/a"}</td>
                <td>
                  <VerdictBadge outcome={shotResult.variance_significance.significant_at_0_05 ? "favorable" : "neutral"} />
                </td>
              </tr>
              <tr>
                <td>AC1 (courant)</td>
                <td>{shotResult.ac1_significance.observed_tau?.toFixed(3) ?? "n/a"}</td>
                <td>{shotResult.ac1_significance.p_value?.toFixed(3) ?? "n/a"}</td>
                <td>
                  <VerdictBadge outcome={shotResult.ac1_significance.significant_at_0_05 ? "favorable" : "neutral"} />
                </td>
              </tr>
              <tr>
                <td>Indice de Moran (sondes magnétiques)</td>
                <td>{shotResult.moran_trend.observed_tau?.toFixed(3) ?? "n/a"}</td>
                <td>{shotResult.moran_trend.p_value?.toFixed(3) ?? "n/a"}</td>
                <td>
                  <VerdictBadge outcome={shotResult.moran_trend.significant_at_0_05 ? "favorable" : "neutral"} />
                </td>
              </tr>
            </tbody>
          </table>
          <p className="source-note">{shotResult.verdict_simple}</p>
        </>
      )}

      <hr className="divider" />
      <h2>Relancer la batterie complète en direct</h2>
      <p className="text-muted">
        Refait les 20 appels réseau + calculs (variance/AC1/Moran, test par données de substitution) sur MAST en
        direct, exactement comme pour produire le tableau figé ci-dessus -- compte environ deux minutes.
      </p>
      <button className="cta secondary" onClick={runAggregate} disabled={aggregateLoading}>
        {aggregateLoading ? "Calcul en cours (~2 min)…" : "Relancer la batterie de 20 tirs en direct"}
      </button>

      <HistoryPanel
        entries={aggregateHistory}
        onSelect={(entry) => setAggregate(entry.result)}
        onClear={() => {
          clearHistory(HISTORY_PAGE_AGGREGATE);
          setAggregateHistory([]);
        }}
        renderLabel={(e) => `${e.result.n_disrupted_with_precursor}/${e.result.n_disrupted} précurseurs, ${e.result.n_stable_false_positive}/${e.result.n_stable} faux positifs`}
      />

      {aggregateError && <p className="error">{aggregateError}</p>}

      {aggregate && (
        <>
          <p className="source-note">{aggregate.verdict_simple}</p>
          <div className="table-scroll">
            <table className="agg-table">
              <thead>
                <tr>
                  <th>Tir</th>
                  <th>Campagne</th>
                  <th>État</th>
                  <th>t_quench</th>
                  <th>I pic</th>
                  <th>Variance sig.</th>
                  <th>AC1 sig.</th>
                  <th>Moran sig.</th>
                  <th>Verdict</th>
                </tr>
              </thead>
              <tbody>
                {aggregate.shots.map((s) => (
                  <LiveShotRow key={s.shot_id} shot={s} />
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
