import { Link } from "react-router-dom";
import { SCORECARD, STRENGTHS, WEAKNESSES, CONCLUSION } from "../data/bilanProjet.js";
import { H1_SUMMARY, H2_RESULT, H3_SUMMARY, H4_SUMMARY, H5_RESULT, FUSION_RESULT, PLASMA_RESULT } from "../data/bilanPublie.js";
import { POSITIONING_SHORT } from "../data/positionnement.js";

export default function Bilan() {
  return (
    <div className="page page-bilan-projet">
      <h1>Bilan : points forts, points faibles</h1>
      <p className="lede">
        Synthèse honnête du projet, mise à jour à chaque round de tests -- pas plus catégorique que ce que
        les données permettent. Aucune des hypothèses empiriques (H1, H2, H3, H5) n'est présentée comme
        confirmée sans réserve ; H4 reste une démonstration en simulation, jamais un verdict statistique.
      </p>
      <p className="text-muted">
        {POSITIONING_SHORT} <Link to="/positionnement">Le détail →</Link>
      </p>

      <div className="scorecard">
        {SCORECARD.map((s) => (
          <div className="score-cell" key={s.dim}>
            <div className="score-dim">{s.dim}</div>
            <div className={`score-verdict score-verdict--${s.verdict}`}>{s.label}</div>
            <p className="score-note">{s.note}</p>
          </div>
        ))}
      </div>

      <section>
        <h2>Résultats en un coup d'œil</h2>
        <div className="agg-summary">
          <div className="agg-stat">
            <span className="agg-number">{H1_SUMMARY.favorable}/{H1_SUMMARY.nPhenomena}</span>
            <span>H1 favorable</span>
          </div>
          <div className="agg-stat">
            <span className="agg-number">non sig.</span>
            <span>H2 tendance (τ={H2_RESULT.realNetwork.trendTau})</span>
          </div>
          <div className="agg-stat">
            <span className="agg-number">{H3_SUMMARY.favorable}/{H3_SUMMARY.nCalculable}</span>
            <span>H3 favorable (calculables)</span>
          </div>
          <div className="agg-stat">
            <span className="agg-number">{H4_SUMMARY.nRobust}/{H4_SUMMARY.nConfigs}</span>
            <span>H4 configs robustes (≥90% de 30 graines)</span>
          </div>
          <div className="agg-stat">
            <span className="agg-number">{H5_RESULT.verdict === "against" ? "rejetée" : H5_RESULT.verdict}</span>
            <span>H5 loi de puissance (p={H5_RESULT.pPlausibility})</span>
          </div>
        </div>
        <p className="text-muted">
          Détail complet, tableaux et graphiques par phénomène : <Link to="/resultats">Résultats</Link>{" "}
          (une page par hypothèse).
        </p>
      </section>

      <section>
        <h2>Second domaine (fusion) -- jamais combiné au score ci-dessus</h2>
        <div className="agg-summary">
          <div className="agg-stat">
            <span className="agg-number">
              {FUSION_RESULT.nDisruptedWithPrecursor}/{FUSION_RESULT.nDisrupted}
            </span>
            <span>tirs disruptés avec précurseur</span>
          </div>
          <div className="agg-stat">
            <span className="agg-number">
              {FUSION_RESULT.nStableFalsePositive}/{FUSION_RESULT.nStable}
            </span>
            <span>faux positifs (tirs stables)</span>
          </div>
        </div>
        <p className="text-muted">
          Détection sur données de tokamak (MAST), même moteur de calcul que H1/H2 -- résultat encourageant mais
          pas net (taux de faux positifs notable). Toujours présenté à part : <Link to="/resultats/fusion">Résultats -- Fusion</Link>.
        </p>
      </section>

      <section>
        <h2>Troisième domaine (bilan de puissance) -- jamais combiné aux deux autres</h2>
        <div className="agg-summary">
          <div className="agg-stat">
            <span className="agg-number">
              {PLASMA_RESULT.nIgnitedWithPrecursor}/{PLASMA_RESULT.nIgnited}
            </span>
            <span>réalisations ignitées avec précurseur</span>
          </div>
          <div className="agg-stat">
            <span className="agg-number">
              {PLASMA_RESULT.nStableFalsePositive}/{PLASMA_RESULT.nStable}
            </span>
            <span>faux positifs (réalisations stables)</span>
          </div>
        </div>
        <p className="text-muted">
          Modèle réduit de physique des plasmas (bilan de puissance 0-D, seuil d'ignition), même moteur de
          calcul que H1/Fusion -- résultat net, mais sur un phénomène simulé bien plus propre qu'une vraie
          donnée bruitée. Toujours présenté à part : <Link to="/resultats/plasma-modele">Résultats -- Modèle de plasma</Link>.
        </p>
      </section>

      <section>
        <h2>Points forts</h2>
        <div className="card-list">
          {STRENGTHS.map((s) => (
            <div className="bilan-card bilan-card--strength" key={s.title}>
              <h3>{s.title}</h3>
              <p>{s.text}</p>
            </div>
          ))}
        </div>
      </section>

      <section>
        <h2>Points faibles</h2>
        <div className="card-list">
          {WEAKNESSES.map((w) => (
            <div className="bilan-card bilan-card--weakness" key={w.title}>
              <h3>{w.title}</h3>
              <p>{w.text}</p>
            </div>
          ))}
        </div>
      </section>

      <section>
        <h2>En bilan</h2>
        <p>{CONCLUSION}</p>
      </section>
    </div>
  );
}
