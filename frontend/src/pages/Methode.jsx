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
            Analogie pédagogique avec un des modèles fondateurs du deep learning (Hopfield, prix Nobel de
            physique 2024) -- mémoire associative, attracteurs, perte de stabilité, pour éclairer la logique
            du logiciel du roman. Ne sert de base à aucun module H1-H5, Fusion ou Plasma.
          </p>
          <Link to="/methode/hopfield-social" className="hypothesis-status-link">
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
