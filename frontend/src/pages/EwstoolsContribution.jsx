import { Link } from "react-router-dom";
import StatusBadge from "../components/StatusBadge.jsx";
import { EWSTOOLS_INFO, EWSTOOLS_STATUS } from "../data/positionnement.js";

export default function EwstoolsContribution() {
  const status = EWSTOOLS_STATUS[EWSTOOLS_INFO.status];

  return (
    <div className="page page-positionnement">
      <p className="breadcrumb">
        <Link to="/positionnement">Positionnement scientifique</Link> <span aria-hidden="true">›</span> Contribution à ewstools
      </p>

      <h1>Contribution à ewstools</h1>
      <p className="lede">{EWSTOOLS_INFO.summary}</p>
      <p>
        <StatusBadge label={status.label} tone={status.tone} />
      </p>

      <section>
        <h2>Ce qui manquait, et pourquoi</h2>
        <p>{EWSTOOLS_INFO.gapFound}</p>
        <p className="text-muted">
          <code>ewstools</code> (<a href={EWSTOOLS_INFO.repoUrl} target="_blank" rel="noreferrer">{EWSTOOLS_INFO.repoUrl}</a>) est
          le paquet Python de référence pour les signaux précurseurs de bascule, publié dans le{" "}
          <em>Journal of Open Source Software</em> (Bury, 2023).
        </p>
      </section>

      <section>
        <h2>Le code et les tests</h2>
        <p>
          Un indicateur spatial (indice de Moran + test de significativité par permutation, classe{" "}
          <code>SpatialEWS</code> suivant les conventions déjà en place dans le paquet), avec une
          recette documentée de contrôle de tendance (retirer les motifs spatiaux qui se renforcent
          lentement dans le temps, un artefact connu qui peut imiter un vrai signal précurseur).
        </p>
        <dl className="signal-stats">
          <div>
            <dt>Tests ajoutés</dt>
            <dd>{EWSTOOLS_INFO.nTestsAdded}, tous passants</dd>
          </div>
          <div>
            <dt>Suite existante</dt>
            <dd>{EWSTOOLS_INFO.nTestsExistingBaseline} tests, 0 régression</dd>
          </div>
        </dl>
        <p className="text-muted">
          Code source : <a href={EWSTOOLS_INFO.forkUrl} target="_blank" rel="noreferrer">fork (branche helios-spatial-and-ebm)</a>,{" "}
          <a href={EWSTOOLS_INFO.pullRequestUrl} target="_blank" rel="noreferrer">pull request #482</a>.
        </p>
      </section>

      <section>
        <h2>Aperçu du code</h2>
        <p className="text-muted"><code>ewstools/spatial.py</code></p>
        <pre className="code-block">
          <code>{`def morans_i(values, weights) -> float:
    """I = (N / S0) * [sum_ij w_ij (x_i - xbar)(x_j - xbar)] / [sum_i (x_i - xbar)^2]"""
    x = np.asarray(values, dtype=float)
    w = np.asarray(weights, dtype=float)
    deviations = x - x.mean()
    s0 = w.sum()
    numerator = deviations @ w @ deviations
    denominator = (deviations**2).sum()
    return float((len(x) / s0) * (numerator / denominator))


class SpatialEWS:
    """Suit les conventions data -> state -> ews de MultiTimeSeries."""

    def compute_moran(self):
        df_pre = self._pre_transition()
        values = df_pre.apply(
            lambda row: morans_i(row.to_numpy(), self.weights), axis=1
        )
        self.ews["morans_i"] = values
        # avertit si des NaN apparaissent (unite manquante a un instant)`}</code>
        </pre>
        <p className="text-muted">
          Code complet, commenté et testé : voir le fork lié ci-dessus.
        </p>
      </section>

      <section>
        <h2>Une vraie revue par un mainteneur -- ce qu'elle a changé</h2>
        <p>{EWSTOOLS_INFO.reviewNote}</p>
        <p className="text-muted">
          Cette page documente le processus tel qu'il s'est déroulé, y compris la partie retirée --
          dans le même esprit que le Journal de recherche : publier honnêtement, corrections
          comprises, pas seulement le résultat final poli.
        </p>
      </section>

      <section>
        <h2>Pistes d'usage</h2>
        <ul>
          {EWSTOOLS_INFO.usageAngles.map((angle) => (
            <li key={angle}>{angle}</li>
          ))}
        </ul>
      </section>

      <section>
        <h2>Statut, tenu à jour honnêtement</h2>
        <p>
          Tant que la pull request n'est pas fusionnée par le mainteneur officiel de <code>ewstools</code>, ce
          site ne dit jamais que cette contribution « fait partie » du paquet -- seulement qu'elle est
          soumise et en cours de revue. Le statut ci-dessus (« {status.label} ») reflète l'état réel, pas un
          objectif : <a href={EWSTOOLS_INFO.pullRequestUrl} target="_blank" rel="noreferrer">voir la pull request</a>.
        </p>
        <p className="text-muted">
          Hélios n'a jamais dépendu d'<code>ewstools</code> : son propre indice de Moran et sa propre logique
          de calibration existent déjà dans le produit (<Link to="/methode/cours-statistiques">cours de
          statistiques</Link>). Cette contribution est un geste séparé vers la communauté de recherche, jamais
          une dépendance technique.
        </p>
      </section>

      <p className="text-muted">
        Voir aussi <Link to="/positionnement">Positionnement scientifique</Link> et{" "}
        <Link to="/positionnement/hopfieldkit">la contribution hopfieldkit</Link>.
      </p>
    </div>
  );
}
