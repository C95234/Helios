import { Link } from "react-router-dom";
import ResultPageTemplate from "../../components/ResultPageTemplate.jsx";
import { IA_VS_STATS_ASYMMETRY_NOTE, IA_VS_STATS_GUARDRAIL, IA_VS_STATS_METHOD_NOTE, IA_VS_STATS_RESULT as R } from "../../data/iaVsStatistiques.js";

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
      summary="Thomas Bury (mainteneur d'ewstools, avec Marten Scheffer) a montré qu'un classifieur de deep learning entraîné sur des séries simulées peut détecter l'approche d'une bascule. Ce banc d'essai compare, sur les deux modèles de bifurcation déjà construits pour Hélios, un petit classifieur CNN à l'indicateur statistique COMPLET déjà utilisé pour H1 (variance et autocorrélation glissantes, tau de Kendall, test par données de substitution) -- jamais une version appauvrie construite pour l'occasion. Le classifieur est ré-entraîné plusieurs fois (initialisation et données différentes à chaque fois) pour mesurer sa propre variabilité, jamais un seul chiffre présenté comme définitif."
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
              <strong>Correction de rigueur appliquée à cette page</strong> (cahier des charges dédié) : la version
              précédente rapportait un seul entraînement et comparait le classifieur à une version appauvrie de
              l'indicateur classique (une simple variance de fin de fenêtre contre un seuil). Les deux défauts sont
              corrigés : le classifieur est maintenant ré-entraîné {R.nSeeds} fois de façon indépendante (moyenne ±
              écart-type rapportés ci-dessous), et l'indicateur classique utilise désormais l'indicateur complet de
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

          <p className="text-muted">
            {R.nTrainSaddlePerSeed + R.nTrainKuramotoPerSeed} réalisations d'entraînement par seed, {nTest}{" "}
            réalisations de test partagées entre tous les seeds (graines jamais vues à l'entraînement), fenêtre de{" "}
            {R.windowLen} pas de temps. Détail des {R.nSeeds} entraînements (perte initiale → finale, un par ligne)
            dans le fichier de résultat gelé (<code>frontend/src/data/results/ia_vs_stats.json</code>).
          </p>
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
      ]}
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
