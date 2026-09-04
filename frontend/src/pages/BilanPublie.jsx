import { Link } from "react-router-dom";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import MethodNote from "../components/MethodNote.jsx";
import {
  GENERATED_AT,
  H1_PHENOMENA,
  H1_SUMMARY,
  H2_RESULT,
  H2_MORAN_SERIES,
  H3_PHENOMENA,
  H3_UNAVAILABLE,
  H3_SUMMARY,
  H4_CONFIGS,
  H4_R_THRESHOLD,
  H4_SUMMARY,
  TRENDS_OBLIQUE_TERMS,
  TRENDS_RESULTS,
  TRENDS_SUMMARY,
} from "../data/bilanPublie.js";

const OUTCOME_LABEL = { favorable: "Favorable", against: "Contre", neutral: "Neutre", na: "Non calculable" };

function VerdictBadge({ outcome }) {
  return <span className={`verdict-badge verdict-badge--${outcome}`}>{OUTCOME_LABEL[outcome]}</span>;
}

const h2ChartData = H2_MORAN_SERIES.dates.map((date, i) => ({
  date,
  reel: H2_MORAN_SERIES.real[i],
  grille: H2_MORAN_SERIES.grid[i],
}));

export default function BilanPublie() {
  return (
    <div className="page page-bilan-publie">
      <h1>Conclusions publiées : les quatre hypothèses testées à fond</h1>
      <p className="lede">
        H1, H2 et H3 testées jusqu'au bout des données disponibles (6 phénomènes réels pour H1, 26 ans de
        séries départementales pour H2, 4 phénomènes calculables sur 6 pour H3), et H4 sur 8 configurations
        de simulation. Contenu figé, généré le {GENERATED_AT} à partir de résultats calculés en direct par
        Hélios -- pas l'historique personnel de ce navigateur (voir <Link to="/bilan">Bilan</Link> pour ça).
      </p>

      <div className="disclaimer">
        <p>
          <strong>À lire avant tout :</strong> un signal précurseur (ou son absence) indique une perte — ou
          non — de résilience statistique, jamais une prédiction certaine ni une cause identifiée. Les
          phénomènes testés ici sont choisis à la main (ruptures documentées et datées), pas tirés au
          hasard : même quand le nombre d'épisodes atteint le seuil de 5 fixé par le protocole (§5.7), ce
          n'est pas un échantillon statistiquement représentatif de « toutes les bascules possibles ». H4
          est d'une autre nature encore : une démonstration de principe en simulation, jamais un verdict
          statistique.
        </p>
      </div>

      <div className="agg-summary">
        <div className="agg-stat">
          <span className="agg-number">{H1_SUMMARY.favorable}</span>
          <span>H1 favorable sur {H1_SUMMARY.nPhenomena}</span>
        </div>
        <div className="agg-stat">
          <span className="agg-number">{H1_SUMMARY.against}</span>
          <span>H1 contre</span>
        </div>
        <div className="agg-stat">
          <span className="agg-number">{H3_SUMMARY.favorable}</span>
          <span>H3 favorable sur {H3_SUMMARY.nCalculable} calculables</span>
        </div>
        <div className="agg-stat">
          <span className="agg-number">{H4_SUMMARY.nUnderThreshold}/{H4_SUMMARY.nConfigs}</span>
          <span>configs H4 sous r_c</span>
        </div>
      </div>

      {/* ---------- H1 ---------- */}
      <section>
        <h2>H1 — Décalage temporel</h2>
        <p className="hypothesis-statement">
          Les indicateurs précurseurs calculés sur les signaux sociaux se déclenchent-ils statistiquement
          avant ceux calculés sur les statistiques officielles, pour un même événement de rupture ?
        </p>
        <p>
          Sur les 6 phénomènes testés (jusqu'à 39 séries Insee contre 3 signaux Wikipédia, chacun testé
          indépendamment), le signal social n'a précédé le signal officiel que dans <strong>un seul cas</strong>{" "}
          — les attentats du 13 novembre 2015, un choc sécuritaire pur où aucune série économique officielle
          n'est devenue significative. Dans les <strong>5 autres cas</strong>, chaque fois qu'un écart de
          timing était mesurable, c'est le signal <strong>officiel</strong> qui a précédé le signal social.
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
                  <td>{p.decalageJours !== null ? `officiel ${p.decalageJours} j` : "—"}</td>
                  <td><VerdictBadge outcome={p.outcome} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className={H1_SUMMARY.against > H1_SUMMARY.favorable ? "moran-sig-no" : "moran-sig-yes"}>
          Ce round de tests ne va pas dans le sens de H1 — sur cet échantillon curaté, l'attention Wikipédia
          n'anticipe pas les statistiques officielles, elle les suit ou réagit à des chocs que l'officiel ne
          capture pas du tout (le cas des attentats).
        </p>
        <p className="text-muted">
          <strong>Nuance importante, à ne pas manquer :</strong> Wikipédia n'est pas un canal de réaction
          instantanée. Consulter ou éditer un article suppose souvent que l'événement soit déjà identifié
          comme notable -- l'activité d'édition en particulier est structurellement réactive (on documente
          une fois qu'on sait quoi documenter). Le résultat majoritairement défavorable à H1 ci-dessus peut
          donc refléter une limite de <em>ce proxy précis</em> plutôt qu'une réfutation de l'idée que des
          signaux sociaux rapides précèdent les statistiques officielles -- c'est exactement pourquoi
          l'extension Google Trends ci-dessous a été menée. Elle donne, avec une source différente, un
          résultat tout aussi négatif -- mais l'intérêt de recherche capté par Trends reste lui aussi une
          réaction (chercher un mot qu'on vient d'entendre), pas la mesure d'une opinion qui se forme en
          direct. Le seul signal vraiment temps réel identifié en explorant cette question (le flux public
          de Bluesky) n'a pas d'historique avant 2024, donc aucun moyen de le tester sur les phénomènes
          curatés ici -- la question reste ouverte, pas tranchée.
        </p>
        <MethodNote methodKeys={["rolling_variance", "rolling_ac1"]} expertMode={true} />

        <h3>Extension : Google Trends comme troisième signal social</h3>
        <div className="simulation-banner">
          <strong>Dérogation documentée (§6) :</strong>
          <span>
            Google Trends est explicitement mis de côté par le cahier des charges tant que son API
            officielle (accès alpha restreint) n'est pas obtenue. Ce test utilise à la place un point
            d'entrée non officiel (même principe que la bibliothèque publique <code>pytrends</code>,
            utilisée en recherche depuis 2016) -- une violation des conditions d'utilisation de Google, pas
            un accès à des données privées (ces chiffres sont déjà publics). Décision assumée et documentée
            dans le code du connecteur (<code>google_trends.py</code>), pas cachée.
          </span>
        </div>
        <p>
          Pour chaque phénomène testable, un terme direct (« gilets jaunes », « confinement »...) et un
          panier <strong>fixe</strong> de 5 termes obliques -- {TRENDS_OBLIQUE_TERMS.join(", ")} -- des
          proxies génériques de tension économique/psychologique, identiques pour tous les phénomènes et
          choisis avant tout résultat, pour ne pas sélectionner a posteriori un terme qui « marche » sur un
          cas donné.
        </p>
        <p>
          Google a bloqué (429) les requêtes après ~28 appels réussis, malgré des délais progressifs entre
          essais : <strong>2 phénomènes sur 6 n'ont pu être testés du tout</strong> (réforme des retraites,
          attentat de Nice). Sur les {TRENDS_SUMMARY.nTermsTestedTotal} tests menés à bien,{" "}
          {TRENDS_SUMMARY.nTermsSignificantTotal} seulement ressortent significatifs.
        </p>
        <div className="table-scroll">
          <table className="agg-table">
            <thead>
              <tr>
                <th>Phénomène</th>
                <th>Termes testés</th>
                <th>Significatifs</th>
                <th>Lesquels</th>
              </tr>
            </thead>
            <tbody>
              {TRENDS_RESULTS.map((r) => (
                <tr key={r.label}>
                  <td>{r.label}</td>
                  <td>{r.status === "blocked" ? <span className="text-muted">bloqué (429)</span> : `${r.nTested}`}</td>
                  <td>{r.status === "blocked" ? "—" : r.nSig}</td>
                  <td>{r.sigTerms.length > 0 ? r.sigTerms.join(", ") : "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="moran-sig-no">
          Résultat honnête, à nouveau négatif dans l'ensemble : les gilets jaunes -- le cas le plus net par
          ailleurs -- ne montrent aucun signal Google Trends significatif sur les 6 termes testés. Le seul
          phénomène avec plusieurs termes significatifs (confinement 2020) porte sur des proxies financiers
          plausibles (vente immobilière, prêt personnel), mais un terme ressort aussi « significatif » sur
          la fenêtre témoin sans événement -- exactement ce que le seuil de 5% laisse attendre par pur
          hasard sur ~5 tests, un rappel concret du risque de comparaisons multiples déjà signalé ailleurs
          dans Hélios. Limite technique supplémentaire, à ne pas passer sous silence : les dates de pic
          calculées sont identiques pour tous les termes d'un même phénomène (artefact probable de bord sur
          des séries Google Trends très creuses, beaucoup de jours à zéro) -- non exploitées ici comme
          indice de calendrier, contrairement au signal Wikipédia.
        </p>
        <p className="text-muted">
          Aucun réseau social n'a pu compléter ce test : Bluesky et Mastodon n'ont pratiquement aucune
          présence française avant 2022-2024, bien après les phénomènes les plus anciens testés ici (voir
          la discussion complète dans l'échange qui a précédé ce test).
        </p>
      </section>

      {/* ---------- H2 ---------- */}
      <section>
        <h2>H2 — Robustesse sur réseau réel</h2>
        <p className="hypothesis-statement">
          L'indice de Moran se comporte-t-il différemment sur le vrai réseau des 96 départements de
          métropole que sur une grille régulière artificielle de même taille ?
        </p>
        <p>
          Une seule série disponible ici (le taux de chômage départemental, {H2_RESULT.periodStart} →{" "}
          {H2_RESULT.periodEnd}, {H2_RESULT.nQuarters} trimestres, {H2_RESULT.nEdgesRealNetwork} paires de
          voisins sur le réseau réel) : pas un échantillon de plusieurs « épisodes » comme H1/H3, une longue
          série testée en tendance.
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
          <div>
            <dt>Réel — dernier trimestre</dt>
            <dd>I={H2_RESULT.realNetwork.latestI} (p={H2_RESULT.realNetwork.latestP})</dd>
          </div>
          <div>
            <dt>Grille — dernier trimestre</dt>
            <dd>I={H2_RESULT.controlGrid.latestI} (p={H2_RESULT.controlGrid.latestP})</dd>
          </div>
        </dl>

        <h3>En creusant au-delà de la tendance : les 105 trimestres, un par un</h3>
        <p>
          La <em>tendance</em> (est-ce que ça monte dans le temps ?) est la question formelle de H2, et elle
          n'est pas significative. Mais le <em>niveau</em> raconte une autre histoire, plus nette :
        </p>
        <div className="chart-box">
          <div className="series-chart-legend">
            <span><span className="legend-swatch" style={{ background: "var(--color-accent)" }} /> Réseau réel</span>
            <span><span className="legend-swatch" style={{ background: "var(--color-mid)" }} /> Grille de contrôle</span>
          </div>
          <ResponsiveContainer width="100%" height={240}>
            <LineChart data={h2ChartData} margin={{ top: 8, right: 16, bottom: 0, left: -16 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
              <XAxis dataKey="date" tick={{ fontSize: 9 }} minTickGap={40} />
              <YAxis tick={{ fontSize: 10 }} width={40} domain={["auto", "auto"]} />
              <Tooltip />
              <Line type="monotone" dataKey="reel" stroke="var(--color-accent)" dot={false} strokeWidth={2} connectNulls />
              <Line type="monotone" dataKey="grille" stroke="var(--color-mid)" dot={false} strokeWidth={1.5} connectNulls />
            </LineChart>
          </ResponsiveContainer>
        </div>
        <p className="moran-sig-yes">
          Le réseau réel est au-dessus de la grille de contrôle sur <strong>les {H2_RESULT.nRealAboveGrid} trimestres, sans une seule exception</strong> —
          moyenne {H2_RESULT.realMean} (écart-type {H2_RESULT.realStd}) contre {H2_RESULT.gridMean} pour la
          grille (proche de zéro, comme attendu pour une structure spatiale sans lien avec la vraie
          géographie). Ce n'est pas ce que H2 teste formellement, et un niveau élevé mais <em>stable</em> n'est
          pas un signal précurseur — seule une <em>hausse</em> le serait. Mais la vraie géographie fait une
          différence considérable et systématique sur cette mesure : le chômage est structurellement
          différent au nord et au sud depuis 26 ans.
        </p>
        <MethodNote methodKeys={["morans_i"]} expertMode={true} />
      </section>

      {/* ---------- H3 ---------- */}
      <section>
        <h2>H3 — Indicateur joint</h2>
        <p className="hypothesis-statement">
          Combiner une tendance temporelle nationale ET une tendance spatiale départementale réduit-il les
          faux positifs par rapport à chaque indicateur pris isolément ?
        </p>
        <p>
          Calculable sur 4 des 6 phénomènes seulement : les attentats de 2015 et de Nice (2016) ont une
          fenêtre trop courte (~7 mois) pour la composante temporelle, qui exige au moins 8 points mensuels
          — une limite de données assumée, pas un choix de calcul.
        </p>
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
        <p className="moran-sig-no">
          Sur les 4 cas calculables, un seul (les gilets jaunes) montre une combinaison significativement
          inhabituelle des deux signaux. Cohérent avec le{" "}
          <Link to="/journal-recherche">Journal de recherche</Link> : le signal temporel domine généralement,
          et il domine effectivement seul chez les 3 autres phénomènes (τ modestes à part Réforme des
          retraites) — la combinaison ne « sauve » pas des signaux par ailleurs faibles.
        </p>
        <MethodNote methodKeys={["h3_joint"]} expertMode={true} />
      </section>

      {/* ---------- H4 ---------- */}
      <section>
        <h2>H4 — Contrôle actif de la synchronisation</h2>
        <div className="simulation-banner">
          <strong>Nature différente de H1-H3 :</strong>
          <span>
            H4 n'est pas testée contre des données réelles — c'est une démonstration de principe en
            simulation (modèle de Kuramoto). Les résultats ci-dessous montrent la robustesse du mécanisme
            sur plusieurs configurations, jamais un verdict « confirmée / infirmée ».
          </span>
        </div>
        <p>
          8 configurations testées, en faisant varier le couplage K (multiples du seuil critique K_c ≈
          1,596), la force du contrôle β, et la taille du réseau N :
        </p>
        <div className="table-scroll">
          <table className="agg-table">
            <thead>
              <tr>
                <th>Configuration</th>
                <th>N</th>
                <th>K / K_c</th>
                <th>β</th>
                <th>r sans contrôle</th>
                <th>r avec contrôle</th>
                <th>Sous r_c={H4_R_THRESHOLD}</th>
              </tr>
            </thead>
            <tbody>
              {H4_CONFIGS.map((c) => (
                <tr key={c.name}>
                  <td>{c.name}</td>
                  <td>{c.n}</td>
                  <td>{c.kOverKc.toFixed(1)}×</td>
                  <td>{c.beta}</td>
                  <td>{c.rUncontrolled.toFixed(3)}</td>
                  <td>{c.rControlled.toFixed(3)}</td>
                  <td><VerdictBadge outcome={c.rControlled < H4_R_THRESHOLD ? "favorable" : "against"} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="moran-sig-yes">
          Le contrôle adaptatif maintient r sous le seuil r_c={H4_R_THRESHOLD} dans les{" "}
          <strong>{H4_SUMMARY.nUnderThreshold} configurations sur {H4_SUMMARY.nConfigs}</strong>, y compris
          à K=5×K_c (couplage cinq fois plus fort que le seuil critique) et avec un contrôle relativement
          faible (β=0,5). Observation notable, non planifiée : le contrôle est plus efficace à grand N (80
          nœuds → r=0,253) qu'à petit N (15 nœuds → r=0,457) — cohérent avec le mécanisme (plus de nœuds
          veut dire plus de paires sur lesquelles la suppression locale peut agir). La relation à β n'est en
          revanche pas monotone (β=4 donne un r légèrement plus haut que β=2) — probablement un effet de la
          graine unique utilisée ici plutôt qu'une propriété du mécanisme.
        </p>
        <MethodNote methodKeys={["kuramoto_h4"]} expertMode={true} />
      </section>

      {/* ---------- Synthèse ---------- */}
      <section>
        <h2>Synthèse</h2>
        <p>
          Pris ensemble, ce round de tests ne confirme aucune des trois hypothèses de recherche originales
          testées contre des données réelles. H1 va même franchement à l'encontre du sens attendu (5 cas sur
          6) ; H2 ne montre pas de synchronisation spatiale croissante, même si le niveau structurel du
          réseau réel se distingue nettement et systématiquement de la grille ; H3 n'est soutenue que sur le
          cas où H1 est aussi la plus contredite (gilets jaunes), suggérant que la force du signal temporel
          — pas la complémentarité temporel/spatial — porte l'essentiel du résultat sur ce cas.
        </p>
        <p>
          Un point à ne pas lire trop vite sur H1 : le résultat défavorable tient sur <strong>deux</strong>{" "}
          proxies sociaux testés (Wikipédia, puis Google Trends en complément), tous deux structurellement
          réactifs -- on consulte ou on recherche un sujet une fois qu'il devient notable, pas avant. Aucun
          des deux n'est un vrai signal d'opinion en temps réel. Ce round de tests dit donc « les proxies
          disponibles et testables sur l'historique ne précèdent pas l'officiel » -- pas « aucun signal
          social ne pourrait jamais précéder l'officiel ». La question reste ouverte pour une vraie source
          en temps réel (voir les limites de H1 pour le détail).
        </p>
        <p>
          H4 se tient à part : ce n'est pas un test contre le réel, mais elle montre, sur 8 configurations de
          simulation variées, que le principe du contrôle adaptatif est robuste — il ne dépend pas d'un
          réglage fin des paramètres pour fonctionner.
        </p>
        <p>
          C'est un résultat honnête à publier tel quel, pas un échec du protocole : Hélios est construit pour
          dire « ça ne marche pas sur ces cas » aussi clairement que l'inverse. Le{" "}
          <Link to="/journal-recherche">Journal de recherche</Link> documente par ailleurs, en simulation et
          sur données réelles, que le signal temporel précède structurellement le signal spatial — cohérent
          avec ce que H1/H3 montrent ici sur données réelles pour le temporel seul.
        </p>
      </section>

      <footer style={{ marginTop: "2.5rem", paddingTop: "1.5rem", borderTop: "1px solid var(--color-border)" }}>
        <p className="text-muted">
          Rapport généré à partir de résultats calculés en direct par l'application Hélios (backend FastAPI,
          connecteurs Insee/Wikipédia, aucune donnée simulée pour H1-H3 ; H4 est un modèle mathématique
          simulé, explicitement identifié comme tel) — reproductible en relançant chaque test depuis{" "}
          <Link to="/tester-h1">Tester H1</Link>, <Link to="/tester-h2">Tester H2</Link>,{" "}
          <Link to="/tester-h3">Tester H3</Link> ou <Link to="/tester-h4">Simuler H4</Link>. Chaque page
          individuelle propose son propre export complet en Markdown ou PDF.
        </p>
        <p className="text-muted">
          Un signal précurseur — ou son absence — indique une perte ou non de résilience statistique, pas une
          prédiction certaine ni une cause identifiée. Aucun de ces résultats ne doit être lu comme un
          verdict définitif : le protocole (§5.7) exige au moins 5 épisodes indépendants avant toute
          conclusion ferme, et les phénomènes testés restent choisis à la main. H4 n'entre pas dans ce
          décompte : en tant que simulation, elle n'aura jamais de verdict de ce type.
        </p>
      </footer>
    </div>
  );
}
