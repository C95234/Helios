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
          Deux nouveaux modules : un indicateur spatial (indice de Moran + test de significativité par
          permutation, classe <code>SpatialEWS</code> suivant les conventions déjà en place dans le paquet), et
          une combinaison de p-values corrélées (méthode empirique de Brown, Poole et al. 2016) --
          implémentation réelle de l'algorithme publié, pas l'adaptation simplifiée qu'utilise Hélios en
          interne pour son propre test H3 (voir <Link to="/methode/cours-statistiques">le cours de
          statistiques</Link>, section « Statistique jointe H3 », qui documente honnêtement cette différence).
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
          Détail complet du manque identifié et de la démarche : <code>CONTRIBUTION_spatial_significance.md</code>{" "}
          dans le dépôt de la contribution.
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
          développée et testée, disponible dès que la démarche de soumission aura lieu. Le statut ci-dessus
          (« {status.label} ») reflète l'état réel, pas un objectif.
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
