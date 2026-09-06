import { Link } from "react-router-dom";

export default function Methode() {
  return (
    <div className="page page-methode">
      <h1>Méthode</h1>
      <p className="lede">
        Emplacement unique de toute démonstration mathématique utilisée par Hélios : les pages Résultats y
        renvoient, elles ne la reproduisent jamais (règle de non-duplication de la restructuration du site).
      </p>

      <div className="hypotheses-list">
        <div className="hypothesis-card">
          <h3>Cours de statistiques appliquées</h3>
          <p>
            Toutes les notions utilisées dans le projet, définies, démontrées avec les outils du programme
            de terminale, illustrées par un exemple résolu, puis reprises dans un exercice corrigé.
          </p>
          <Link to="/methode/cours-statistiques" className="hypothesis-status-link">
            Lire le cours →
          </Link>
        </div>
        <div className="hypothesis-card">
          <h3>Des suites au ralentissement critique</h3>
          <p>
            Construction progressive du modèle mathématique du ralentissement critique depuis les suites
            numériques de terminale -- pourquoi variance et autocorrélation montent près d'une bifurcation.
          </p>
          <Link to="/methode/suites-ralentissement-critique" className="hypothesis-status-link">
            Voir la page →
          </Link>
        </div>
        <div className="hypothesis-card">
          <h3>Réseaux de Hopfield et groupes sociaux</h3>
          <p>
            Démonstration complète (théorème de convergence, calcul de la capacité de mémoire) qui sert de
            support théorique au domaine <Link to="/resultats#memoire-collective">Mémoire collective</Link> --
            un modèle fondateur du deep learning (Hopfield, prix Nobel de physique 2024), pas le contenu
            principal du domaine lui-même.
          </p>
          <Link to="/methode/hopfield" className="hypothesis-status-link">
            Lire le cours →
          </Link>
        </div>
        <div className="hypothesis-card">
          <h3>Bibliographie complète</h3>
          <p>Toutes les références citées dans le projet, exactes -- jamais un nom d'auteur seul.</p>
          <Link to="/methode/bibliographie" className="hypothesis-status-link">
            Voir la bibliographie →
          </Link>
        </div>
      </div>
    </div>
  );
}
