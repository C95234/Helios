import { Link } from "react-router-dom";
import ResultPageTemplate from "../../components/ResultPageTemplate.jsx";
import { IA_VS_STATS_ASYMMETRY_NOTE, IA_VS_STATS_GUARDRAIL, IA_VS_STATS_METHOD_NOTE, IA_VS_STATS_RESULT as R } from "../../data/iaVsStatistiques.js";

function pct(x) {
  return x === null || x === undefined ? "n/a" : `${Math.round(x * 100)}%`;
}

function ModelComparisonTable({ title, data }) {
  return (
    <>
      <h3>{title}</h3>
      <div className="table-scroll">
        <table className="agg-table">
          <thead>
            <tr>
              <th></th>
              <th>Classifieur (CNN)</th>
              <th>Indicateur classique</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Taux de détection (bascules réelles repérées)</td>
              <td>{pct(data.cnn.detection_rate)} ({data.cnn.n_detected}/{data.cnn.n_tipped})</td>
              <td>{pct(data.classical.detection_rate)} ({data.classical.n_detected}/{data.classical.n_tipped})</td>
            </tr>
            <tr>
              <td>Délai d'anticipation moyen (bascules détectées)</td>
              <td>{data.cnn.mean_lead_time ?? "n/a"} unités de temps</td>
              <td>{data.classical.mean_lead_time ?? "n/a"} unités de temps</td>
            </tr>
            <tr>
              <td>Faux positifs (contrôles jamais basculés)</td>
              <td>{pct(data.cnn.false_positive_rate)} ({data.cnn.n_false_positives}/{data.cnn.n_stable})</td>
              <td>{pct(data.classical.false_positive_rate)} ({data.classical.n_false_positives}/{data.classical.n_stable})</td>
            </tr>
          </tbody>
        </table>
      </div>
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
      episodesLabel={`${nTest} réalisations de test par modèle, jamais vues à l'entraînement`}
      summary="Thomas Bury (mainteneur d'ewstools, avec Marten Scheffer) a montré qu'un classifieur de deep learning entraîné sur des séries simulées peut détecter l'approche d'une bascule. Ce banc d'essai compare, sur les deux modèles de bifurcation déjà construits pour Hélios, un petit classifieur CNN à l'indicateur statistique classique déjà utilisé partout ailleurs dans le projet (variance de fin de fenêtre, seuil calibré empiriquement). Résultat asymétrique et rapporté tel quel : net avantage au classifieur sur un modèle, net désavantage sur l'autre -- un test de réplication comparative, pas une nouvelle méthode, et pas un résultat à sens unique."
      postulateSimple="Sur les mêmes fenêtres de série brute, un classifieur entraîné détecte-t-il l'approche d'une bascule plus tôt, plus souvent, ou de façon plus fiable qu'un indicateur statistique classique déjà interprétable -- ou est-ce l'inverse ?"
      postulateExpert={IA_VS_STATS_METHOD_NOTE}
      resultText={
        <>
          <p>{IA_VS_STATS_ASYMMETRY_NOTE}</p>

          <ModelComparisonTable title="Nœud-col (§5.6quater) -- avantage net au classifieur" data={R.saddleNode} />
          <p className="text-muted">
            Les deux méthodes détectent 100% des bascules réelles, mais le classifieur les repère en moyenne{" "}
            {Math.round(R.saddleNode.cnn.mean_lead_time / R.saddleNode.classical.mean_lead_time)}x plus tôt
            ({R.saddleNode.cnn.mean_lead_time} contre {R.saddleNode.classical.mean_lead_time} unités de temps
            d'avance), avec zéro faux positif contre {R.saddleNode.classical.n_false_positives} pour l'indicateur
            classique.
          </p>

          <ModelComparisonTable title="Kuramoto (§5.8) -- ni l'un ni l'autre ne discrimine bien" data={R.kuramoto} />
          <p className="text-muted">
            Le classifieur détecte 100% des vraies synchronisations mais flague aussi 100% des contrôles stables --
            entraîné conjointement sur les deux modèles avec un seuil de décision unique, il n'a pas trouvé de
            frontière utile pour celui-ci. L'indicateur classique, recalibré spécifiquement pour Kuramoto, reste
            faible (détection à peine au-dessus de son propre taux de fausses alertes).
          </p>

          <p className="text-muted">
            Entraîné sur {R.nTrainSaddle + R.nTrainKuramoto} réalisations (perte d'entraînement {R.trainLossInitial} →{" "}
            {R.trainLossFinal}), testé sur {nTest} réalisations indépendantes (graines jamais vues à l'entraînement),
            fenêtre de {R.windowLen} pas de temps.
          </p>
        </>
      }
      methodLink={{ to: "/methode/cours-statistiques", label: "Voir le cours de statistiques (méthode classique de référence)" }}
      limits={[
        IA_VS_STATS_GUARDRAIL,
        "Modèles sources réutilisés à échelle réduite (réseaux plus petits, durée plus courte) pour permettre l'entraînement sur des milliers de fenêtres -- documenté comme Adaptation Hélios dans le code (backend/app/ml_benchmark.py), pas une nouvelle modélisation.",
        "Le classifieur voit la même fenêtre brute que l'indicateur classique -- aucune information supplémentaire (réseau, paramètres du modèle) ne lui est donnée, pour une comparaison à armes égales.",
        "Le classifieur est entraîné UNE FOIS sur les deux modèles combinés (comme le ferait un utilisateur qui n'aurait pas de modèle spécifique à disposition) -- son échec sur Kuramoto reflète cette contrainte, pas une limite absolue du deep learning : un classifieur entraîné spécifiquement sur Kuramoto seul ferait probablement mieux, mais n'a pas été testé ici.",
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
