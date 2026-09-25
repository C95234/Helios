import { Link } from "react-router-dom";
import ResultPageTemplate from "../../components/ResultPageTemplate.jsx";
import { IA_VS_STATS_ASYMMETRY_NOTE, IA_VS_STATS_GUARDRAIL, IA_VS_STATS_METHOD_NOTE, IA_VS_STATS_RESULT as R } from "../../data/iaVsStatistiques.js";
import { IA_VS_STATS_REAL_H1 as REAL_H1, IA_VS_STATS_REAL_H1_NOTE, IA_VS_STATS_REAL_H1_RESULT_NOTE } from "../../data/iaVsStatsRealH1.js";
import { IA_VS_STATS_REAL_FUSION as REAL_FUSION, IA_VS_STATS_REAL_FUSION_NOTE, IA_VS_STATS_REAL_FUSION_RESULT_NOTE } from "../../data/iaVsStatsRealFusion.js";
import { IA_VS_STATS_REAL_H2 as REAL_H2, IA_VS_STATS_REAL_H2_NOTE, IA_VS_STATS_REAL_H2_RESULT_NOTE } from "../../data/iaVsStatsRealH2.js";
import { IA_VS_STATS_REAL_H3 as REAL_H3, IA_VS_STATS_REAL_H3_NOTE, IA_VS_STATS_REAL_H3_RESULT_NOTE } from "../../data/iaVsStatsRealH3.js";

function pct(x) {
  return x === null || x === undefined ? "n/a" : `${Math.round(x * 100)}%`;
}

function pctMeanStd(stat) {
  if (!stat) return "n/a";
  return `${Math.round(stat.mean * 100)}% (± ${Math.round(stat.std * 100)})`;
}

function numMeanStd(stat, unit) {
  if (!stat) return "n/a";
  return `${stat.mean.toFixed(1)} ± ${stat.std.toFixed(2)} ${unit}`;
}

function SlidingWindowSchema() {
  const seriesPoints = "20,150 50,140 80,155 110,135 140,148 170,120 200,132 230,105 260,118 290,85 320,95 350,60 380,40";
  return (
    <figure className="chart-box" style={{ margin: "1rem 0" }}>
      <svg viewBox="0 0 700 220" role="img" aria-label="Schéma : une fenêtre glissante de la série brute est passée au classifieur, qui répond par une probabilité">
        <text x="20" y="20" fontSize="13" fill="var(--color-text-muted)">Série brute (ex. moyenne du réseau, ou paramètre d'ordre)</text>
        <polyline points={seriesPoints} fill="none" stroke="var(--color-text-muted)" strokeWidth="2" />
        <line x1="380" y1="20" x2="380" y2="190" stroke="var(--color-warn)" strokeDasharray="4 3" strokeWidth="1.5" />
        <text x="384" y="200" fontSize="11" fill="var(--color-warn)">bascule</text>
        <rect x="320" y="30" width="70" height="150" fill="var(--color-sim)" opacity="0.15" stroke="var(--color-sim)" strokeWidth="1.5" />
        <text x="325" y="205" fontSize="11" fill="var(--color-sim)">fenêtre (60 points)</text>
        <path d="M 395 105 L 440 105" stroke="var(--color-text-muted)" strokeWidth="2" markerEnd="url(#arrow)" />
        <rect x="445" y="75" width="90" height="60" rx="8" fill="var(--color-surface)" stroke="var(--color-accent)" strokeWidth="1.5" />
        <text x="490" y="100" fontSize="12" fill="var(--color-accent)" textAnchor="middle">CNN</text>
        <text x="490" y="117" fontSize="10" fill="var(--color-text-muted)" textAnchor="middle">ou indicateur</text>
        <text x="490" y="129" fontSize="10" fill="var(--color-text-muted)" textAnchor="middle">classique</text>
        <path d="M 535 105 L 580 105" stroke="var(--color-text-muted)" strokeWidth="2" markerEnd="url(#arrow)" />
        <text x="590" y="100" fontSize="12" fill="var(--color-text)">"proche</text>
        <text x="590" y="115" fontSize="12" fill="var(--color-text)">d'une bascule"</text>
        <text x="590" y="132" fontSize="20" fill="var(--color-warn)" fontWeight="bold">?</text>
        <defs>
          <marker id="arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">
            <path d="M0,0 L6,3 L0,6 Z" fill="var(--color-text-muted)" />
          </marker>
        </defs>
      </svg>
      <figcaption className="text-muted">
        La fenêtre glisse le long de toute la trajectoire de test ; les deux méthodes reçoivent exactement la même
        fenêtre de 60 points et répondent chacune par un verdict "proche d'une bascule" ou non -- jamais un accès à
        l'historique complet ni à la suite de la trajectoire.
      </figcaption>
    </figure>
  );
}

function Ar1ValidityCheck({ ar1 }) {
  if (!ar1) return null;
  const phis = Object.keys(ar1.perPhi);
  return (
    <>
      <h3>Validité sur des séries sans bifurcation (§1.1bis)</h3>
      <p className="text-muted">
        Un co-auteur de Bury a montré que ce type de classifieur peut classer à tort un simple processus AR(1)
        stationnaire (aucune bifurcation, juste de la persistance temporelle) comme "proche d'une bascule"
        (Dablander &amp; Bury, 2021). Test direct : l'ensemble des {R.nSeeds} modèles appliqué à des séries AR(1)
        synthétiques, sans aucune vraie bifurcation.
      </p>
      <div className="table-scroll">
        <table className="agg-table">
          <thead>
            <tr>
              <th>Persistance (φ)</th>
              <th>Fenêtres flaguées à tort</th>
              <th>Probabilité moyenne</th>
            </tr>
          </thead>
          <tbody>
            {phis.map((phi) => (
              <tr key={phi}>
                <td>{phi}</td>
                <td>{ar1.perPhi[phi].n_flagged}/{ar1.perPhi[phi].n} ({Math.round(ar1.perPhi[phi].flagged_fraction * 100)}%)</td>
                <td>{ar1.perPhi[phi].mean_probability}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="text-muted">
        Global : {Math.round(ar1.overallFlaggedFraction * 100)}% des {ar1.nTotal} fenêtres AR(1) (toutes valeurs de φ
        confondues) flaguées à tort comme "proche d'une bascule" -- rapporté tel quel, dans les deux sens possibles :
        un taux élevé confirmerait le biais documenté par Dablander &amp; Bury sur cette adaptation aussi ; un taux
        faible ne prouverait pas son absence sur toute forme de série non stationnaire, seulement sur ce test précis.
      </p>
    </>
  );
}

function ModelComparisonTable({ title, simple, classical, cnn, nSeeds }) {
  return (
    <>
      <h3>{title}</h3>
      <p className="text-muted">{simple}</p>
      <div className="table-scroll">
        <table className="agg-table">
          <thead>
            <tr>
              <th></th>
              <th>Classifieur (CNN, {nSeeds} entraînements)</th>
              <th>Indicateur classique</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Taux de détection (bascules réelles repérées)</td>
              <td>{pctMeanStd(cnn.detection_rate)}</td>
              <td>{pct(classical.detection_rate)} ({classical.n_detected}/{classical.n_tipped})</td>
            </tr>
            <tr>
              <td>Délai d'anticipation moyen (bascules détectées)</td>
              <td>{numMeanStd(cnn.mean_lead_time, "unités de temps")}</td>
              <td>{classical.mean_lead_time ?? "n/a"} unités de temps</td>
            </tr>
            <tr>
              <td>Faux positifs (contrôles jamais basculés)</td>
              <td>{pctMeanStd(cnn.false_positive_rate)}</td>
              <td>{pct(classical.false_positive_rate)} ({classical.n_false_positives}/{classical.n_stable})</td>
            </tr>
          </tbody>
        </table>
      </div>
      <p className="text-muted" style={{ fontSize: "0.85em" }}>
        Classifieur : moyenne ± écart-type sur {nSeeds} entraînements indépendants (initialisation et jeu
        d'entraînement différents à chaque fois), tous évalués sur le MÊME jeu de test -- §1.1 de la correction de
        rigueur. Indicateur classique : un seul résultat, il ne dépend d'aucun entraînement.
      </p>
    </>
  );
}

function RealH1Extension() {
  const { phenomena, nSeeds, windowLen } = REAL_H1;
  return (
    <>
      <h3 id="extension-h1">Extension aux données réelles -- domaine Société (§2.1)</h3>
      <p>
        <strong>En bref :</strong> le classifieur (IA) et l'indicateur classique de H1 vont dans le même sens sur les
        6 épisodes réels -- le taux de fenêtres flaguées par l'IA suit à peu près le nombre de signaux sociaux déjà
        trouvés par la méthode classique. Mais un test de robustesse (ci-dessus) montre que ce même classifieur se
        trompe aussi facilement sur des séries qui n'ont AUCUNE bascule -- cette ressemblance ne prouve donc pas
        qu'il détecte vraiment quelque chose.
      </p>
      <p className="text-muted">
        Le classifieur a appris à repérer une bascule sur des modèles simulés (nœud-col, Kuramoto) -- fait-il mieux
        que rien du tout sur les mêmes épisodes réels qui ont déjà donné des résultats majoritairement négatifs pour
        H1 ? Ensemble des {nSeeds} modèles (§1.1), fenêtre de {windowLen} jours glissée le long de l'attention
        Wikipédia de chacun des 6 épisodes déjà testés pour H1 -- comparé, épisode par épisode, au verdict déjà
        publié sur le signal social (nombre de signaux sociaux significatifs sur 3).
      </p>
      <p className="text-muted">{IA_VS_STATS_REAL_H1_NOTE}</p>
      <div className="table-scroll">
        <table className="agg-table">
          <thead>
            <tr>
              <th>Phénomène</th>
              <th>Classifieur (fenêtres flaguées)</th>
              <th>Probabilité moyenne</th>
              <th>H1 déjà publié (signal social)</th>
            </tr>
          </thead>
          <tbody>
            {phenomena.map((p) => (
              <tr key={p.key}>
                <td>{p.label}</td>
                <td>{p.error ? "n/a" : `${p.n_flagged}/${p.n_windows} (${Math.round(p.flagged_fraction * 100)}%)`}</td>
                <td>{p.error ? p.error : p.mean_probability}</td>
                <td>{p.h1_published ? `${p.h1_published.n_soc_sig}/${p.h1_published.n_soc} -- ${p.h1_published.outcome}` : "n/a"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="text-muted">{IA_VS_STATS_REAL_H1_RESULT_NOTE}</p>
    </>
  );
}

function RealFusionExtension() {
  const { shots, nSeeds, windowLen, stride, summary } = REAL_FUSION;
  return (
    <>
      <h3 id="extension-fusion">Extension aux données réelles -- domaine Fusion nucléaire (§2.4)</h3>
      <p>
        <strong>En bref :</strong> le classifieur ne distingue pas les tirs qui vont réellement disrupter de ceux qui
        restent stables -- il réagit même en moyenne un peu PLUS aux tirs stables, l'inverse de ce qu'on attendrait
        d'un vrai signal précurseur. Un résultat négatif net, rapporté tel quel.
      </p>
      <p className="text-muted">
        Même ensemble de {nSeeds} modèles, jamais ré-entraîné -- appliqué cette fois à la batterie curatée de 20 tirs
        réels MAST déjà utilisée par le module Fusion (10 disruptés, 10 stables), fenêtre de {windowLen} points
        glissée avec un pas de {stride} sur le courant plasma pré-quench.
      </p>
      <p className="text-muted">{IA_VS_STATS_REAL_FUSION_NOTE}</p>
      <div className="table-scroll">
        <table className="agg-table">
          <thead>
            <tr>
              <th>Tir</th>
              <th>Publié (Fusion)</th>
              <th>Fenêtres flaguées</th>
              <th>Probabilité moyenne</th>
            </tr>
          </thead>
          <tbody>
            {shots.map((s) => (
              <tr key={s.shot_id}>
                <td>{s.shot_id}</td>
                <td>{s.disrupted_published ? "disrupté" : "stable"}</td>
                <td>{s.error ? "n/a" : `${s.n_flagged}/${s.n_windows} (${Math.round(s.flagged_fraction * 100)}%)`}</td>
                <td>{s.error ? s.error : s.mean_probability}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="text-muted">
        Critère binaire "au moins une fenêtre flaguée" : {summary.nDisruptedWithCnnFlag}/{summary.nDisrupted} tirs
        disruptés, {summary.nStableWithCnnFlag}/{summary.nStable} tirs stables -- sans intérêt discriminant (tous
        flagués). {IA_VS_STATS_REAL_FUSION_RESULT_NOTE}
      </p>
    </>
  );
}

function RealH2Extension() {
  const { nSeeds, nNodes, nTestSnapshots, classical, cnn, realData } = REAL_H2;
  return (
    <>
      <h3 id="extension-h2">Extension aux données réelles -- domaine Société, réseau (§2.2)</h3>
      <p>
        <strong>En bref :</strong> ici, c'est la méthode statistique classique (l'indice de Moran) qui gagne
        nettement contre le classifieur IA -- à la fois sur des données simulées et sur les vraies données de
        chômage départemental. L'IA ne bat pas toujours les statistiques classiques : ce cas le montre clairement.
      </p>
      <p className="text-muted">
        H2 pose une question spatiale, pas temporelle : un classifieur entraîné à reconnaître le réseau réel des{" "}
        {nNodes} départements (plutôt qu'une grille de contrôle de même taille) fait-il mieux que l'indice de Moran
        pour cette tâche de discrimination -- puis, appliqué à la vraie série de chômage départemental, reconnaît-il
        bien cette dernière comme provenant du réseau réel ?
      </p>
      <p className="text-muted">{IA_VS_STATS_REAL_H2_NOTE}</p>
      <div className="table-scroll">
        <table className="agg-table">
          <thead>
            <tr>
              <th></th>
              <th>Classifieur spatial (graphe, {nSeeds} entraînements)</th>
              <th>Indice de Moran (sans paramètre appris)</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Accuracy sur {nTestSnapshots} instantanés simulés de test (réseau réel vs grille)</td>
              <td>{pctMeanStd({ mean: cnn.meanAccuracy, std: cnn.stdAccuracy })} -- ensemble : {pct(cnn.ensembleAccuracy)}</td>
              <td>{pct(classical.accuracy)}</td>
            </tr>
            <tr>
              <td>Trimestres réels ({realData.nPeriods}, {realData.periodStart} à {realData.periodEnd}) reconnus "réseau réel"</td>
              <td>{pct(realData.fractionClassifiedRealNetworkCnn)} (probabilité moyenne {realData.meanProbabilityRealNetwork})</td>
              <td>{pct(realData.fractionClassifiedRealNetworkClassical)}</td>
            </tr>
          </tbody>
        </table>
      </div>
      <p className="text-muted">{IA_VS_STATS_REAL_H2_RESULT_NOTE}</p>
    </>
  );
}

function RealH3Extension() {
  const { nSeeds, phenomena, classical, cnn } = REAL_H3;
  return (
    <>
      <h3 id="extension-h3">Extension aux données réelles -- domaine Société, indicateur joint (§2.3)</h3>
      <p>
        <strong>En bref :</strong> sur des données simulées, le classifieur IA fait bien mieux que la méthode
        statistique classique. Mais sur les 6 cas réels déjà testés par H3, les deux méthodes tombent d'accord :
        aucune ne détecte quoi que ce soit. Gagner sur des données simulées ne garantit donc pas de gagner sur de
        vraies données.
      </p>
      <p className="text-muted">
        H3 demande une entrée double, propre à ce cas : un classifieur à deux branches (une temporelle, une
        spatiale, fusionnées avant la décision) détecte-t-il mieux une anomalie JOINTE (les deux signaux anormaux en
        même temps) que la méthode empirique de Brown/Kost &amp; McDermott déjà utilisée par H3 ?
      </p>
      <p className="text-muted">{IA_VS_STATS_REAL_H3_NOTE}</p>
      <div className="table-scroll">
        <table className="agg-table">
          <thead>
            <tr>
              <th></th>
              <th>Classifieur double-entrée ({nSeeds} entraînements)</th>
              <th>Baseline classique (tendance + Moran)</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Accuracy sur paires simulées de test</td>
              <td>{pctMeanStd({ mean: cnn.meanAccuracy, std: cnn.stdAccuracy })} -- ensemble : {pct(cnn.ensembleAccuracy)}</td>
              <td>{pct(classical.accuracy)}</td>
            </tr>
          </tbody>
        </table>
      </div>
      <div className="table-scroll">
        <table className="agg-table">
          <thead>
            <tr>
              <th>Phénomène</th>
              <th>Probabilité d'anomalie jointe (classifieur)</th>
              <th>Verdict classifieur</th>
              <th>Verdict baseline classique</th>
            </tr>
          </thead>
          <tbody>
            {phenomena.map((p) => (
              <tr key={p.key}>
                <td>{p.label}</td>
                <td>{p.error ? p.error : p.cnn_probability_joint_anomaly}</td>
                <td>{p.error ? "n/a" : p.cnn_flagged ? "anomalie jointe" : "rien détecté"}</td>
                <td>{p.error ? "n/a" : p.classical_flagged ? "anomalie jointe" : "rien détecté"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="text-muted">{IA_VS_STATS_REAL_H3_RESULT_NOTE}</p>
    </>
  );
}

export default function IaVsStatistiquesResult() {
  const nTest = R.nTestSaddle + R.nTestKuramoto;

  return (
    <ResultPageTemplate
      code="IA"
      title="Indicateurs statistiques classiques vs un classifieur de deep learning"
      catchyTitle="Un signal précurseur se voit-il aussi bien à l'œil qu'appris par une machine ?"
      domain={{ name: "Banc d'essai transversal", to: "/resultats#banc-dessai" }}
      verdict="comparatif"
      episodesLabel={`${nTest} réalisations de test partagées, ${R.nSeeds} entraînements indépendants du classifieur`}
      summary="Thomas Bury (mainteneur d'ewstools, avec Marten Scheffer) a montré qu'un classifieur de deep learning entraîné sur des séries simulées peut détecter l'approche d'une bascule -- code et architecture publiés. Ce banc d'essai adapte cette architecture (CNN-LSTM) aux deux modèles de bifurcation déjà construits pour Hélios, et la compare à l'indicateur statistique COMPLET déjà utilisé pour H1 (variance et autocorrélation glissantes, tau de Kendall, test par données de substitution) -- jamais une version appauvrie construite pour l'occasion. Le classifieur est ré-entraîné en ensemble de plusieurs modèles indépendants (la méthode de robustesse de Bury et al. eux-mêmes) pour mesurer sa propre variabilité, jamais un seul chiffre présenté comme définitif."
      postulateSimple="Sur les mêmes fenêtres de série brute, un classifieur entraîné détecte-t-il l'approche d'une bascule plus tôt, plus souvent, ou de façon plus fiable qu'un indicateur statistique classique déjà interprétable -- ou est-ce l'inverse ?"
      postulateExpert={IA_VS_STATS_METHOD_NOTE}
      resultText={
        <>
          <SlidingWindowSchema />
          <p>{IA_VS_STATS_ASYMMETRY_NOTE}</p>
          <p className="text-muted">
            Démonstrations complètes : <Link to="/methode/cnn-deep-learning">convolution,
            passe avant, rétropropagation et descente de gradient</Link> pour le classifieur ; <Link to="/methode/cours-statistiques#autocorrelation">variance
            glissante</Link>, <Link to="/methode/cours-statistiques#kendall">tau de Kendall</Link> et le test par
            données de substitution pour l'indicateur classique -- exactement la même mécanique que H1
            (<code>surrogate_test</code>), appliquée ici à l'intérieur d'une seule fenêtre plutôt que sur une
            trajectoire complète.
          </p>

          <div className="disclaimer">
            <p>
              <strong>Corrections de rigueur appliquées à cette page</strong> (cahiers des charges dédiés,
              successifs) : la version initiale rapportait un seul entraînement d'un petit CNN simplifié, comparé à
              une version appauvrie de l'indicateur classique (une simple variance de fin de fenêtre contre un
              seuil). Trois corrections cumulées depuis : (1) le classifieur reprend désormais l'architecture
              réelle de Bury et al. (2021) -- CNN-LSTM, code source publié lu directement, voir{" "}
              <Link to="/methode/cnn-deep-learning">la démonstration complète</Link> ; (2) il est ré-entraîné en
              ensemble de {R.nSeeds} modèles indépendants (moyenne ± écart-type rapportés ci-dessous), la méthode
              de robustesse de Bury et al. eux-mêmes ; (3) l'indicateur classique utilise l'indicateur complet de
              H1, testé pour sa significativité par données de substitution -- une comparaison à armes égales.
            </p>
          </div>

          <ModelComparisonTable
            title="Nœud-col (§5.6quater)"
            simple="Sur ce modèle, la machine voit-elle venir la bascule mieux ou plus tôt que l'indicateur classique ?"
            classical={R.classical.saddleNode}
            cnn={R.cnn.saddleNode}
            nSeeds={R.nSeeds}
          />

          <ModelComparisonTable
            title="Kuramoto (§5.8)"
            simple="Sur ce modèle de synchronisation, l'une des deux méthodes s'en sort-elle mieux que l'autre ?"
            classical={R.classical.kuramoto}
            cnn={R.cnn.kuramoto}
            nSeeds={R.nSeeds}
          />

          <Ar1ValidityCheck ar1={R.ar1Validity} />

          <p className="text-muted">
            {R.nTrainSaddlePerSeed + R.nTrainKuramotoPerSeed} réalisations d'entraînement par seed, {nTest}{" "}
            réalisations de test partagées entre tous les seeds (graines jamais vues à l'entraînement), fenêtre de{" "}
            {R.windowLen} pas de temps. Détail des {R.nSeeds} entraînements (perte initiale → finale, un par ligne)
            dans le fichier de résultat gelé (<code>frontend/src/data/results/ia_vs_stats.json</code>).
          </p>

          <RealH1Extension />

          <RealH2Extension />

          <RealH3Extension />

          <RealFusionExtension />
        </>
      }
      methodLink={{ to: "/methode/cnn-deep-learning", label: "Voir la démonstration complète (convolution, rétropropagation, descente de gradient)" }}
      limits={[
        IA_VS_STATS_GUARDRAIL,
        "Le filtre de persistance (nombre de fenêtres glissantes consécutives requises avant de déclarer un signal, actuellement 6) a été calibré pour l'ancien détecteur classique à seuil simple, jamais recalibré pour le nouveau test de significativité complet (§1.2) -- le taux de faux positifs élevé de l'indicateur classique sur le nœud-col (86,7%) reflète probablement en bonne partie cette calibration périmée plutôt qu'un vrai écart de robustesse. Un nouveau balayage de calibration (comme celui déjà fait pour l'ancien détecteur, voir l'historique du code) serait nécessaire pour trancher -- non fait ici faute de budget de calcul, signalé plutôt que masqué.",
        "Modèles sources réutilisés à échelle réduite (réseaux plus petits, durée plus courte) pour permettre l'entraînement sur des milliers de fenêtres -- documenté comme Adaptation Hélios dans le code (backend/app/ml_benchmark.py), pas une nouvelle modélisation.",
        "Le classifieur voit la même fenêtre brute que l'indicateur classique -- aucune information supplémentaire (réseau, paramètres du modèle) ne lui est donnée, pour une comparaison à armes égales.",
        "Le classifieur est entraîné sur les deux modèles combinés, avec un seuil de décision unique (comme le ferait un utilisateur qui n'aurait pas de modèle spécifique à disposition) -- un classifieur entraîné spécifiquement sur un seul modèle ferait probablement mieux sur celui-ci, mais n'a pas été testé ici.",
        "Échelle réduite par rapport à la version idéale du protocole (jeu d'entraînement et de test plus petits que ce qu'un budget de calcul illimité permettrait) -- un compromis documenté pour que le ré-entraînement multi-graines (§1.1) reste exécutable en un temps raisonnable, pas une limite de méthode.",
        "Jamais combiné aux verdicts des trois domaines (Société, Fusion nucléaire, Mémoire collective) : ce banc d'essai est transversal, pas un module de plus dans l'un d'eux.",
        "Extension aux données réelles (§2.1, §2.4) : aucun filtre de persistance appliqué (contrairement à l'évaluation sur données simulées) -- le taux de fenêtres flaguées est un taux brut, fenêtre par fenêtre, pas un nombre d'alertes soutenues dans le temps. La normalisation par fenêtre (moyenne/écart-type propres à chaque fenêtre, plutôt que la normalisation globale du jeu d'entraînement) est une adaptation nécessaire pour un signal d'échelle complètement différente des séries simulées, pas une méthode validée par ailleurs.",
        "Sur la batterie MAST réelle (§2.4), le taux de fenêtres flaguées est en moyenne PLUS élevé sur les tirs stables (98,3%) que sur les tirs disruptés (69,7%) -- un résultat inversé par rapport à ce qui serait attendu d'un vrai précurseur, rapporté sans explication de confort plutôt que masqué ou réinterprété a posteriori.",
        "Le classifieur spatial (§2.2, réseau vs grille) n'a pas d'architecture publiée de référence à reproduire (contrairement au CNN-LSTM temporel) -- une architecture légère conçue pour ce banc d'essai, jamais validée par ailleurs, et faute de coordonnées géographiques disponibles pour les départements, une convolution de GRAPHE plutôt qu'une carte rasterisée. Sur cette tâche, elle fait moins bien que l'indice de Moran, dans les deux sens testés (instantanés simulés ET vraie série de chômage) -- rapporté tel quel, un résultat net en faveur de la méthode statistique classique.",
        "Le classifieur double-entrée (§2.3, H3) est, à l'inverse, nettement meilleur que la baseline classique sur la tâche simulée (99,2% contre 84,0%) -- mais sur les 6 phénomènes réels, les deux méthodes s'accordent pour ne rien détecter, ce qui ne permet ni de confirmer ni d'infirmer cet avantage sur données réelles à cette échelle.",
      ]}
      journalLink={{ to: "/journal", label: "Voir le Journal de recherche (§10-13 -- extension aux données réelles)" }}
      showLiveSection={false}
    >
      <p className="lede">
        Résultat figé (<code>backend/scripts/train_and_compare_classifier.py</code>), pas de ré-entraînement en
        direct dans le navigateur -- entraîner un classifieur n'est pas instantané, contrairement aux autres
        outils "tester en direct" du site. Voir aussi{" "}
        <Link to="/positionnement/ewstools">la contribution à ewstools</Link>, qui a motivé cette comparaison.
      </p>
    </ResultPageTemplate>
  );
}
