import { Link } from "react-router-dom";

/**
 * Page en attente : le polycopie "Des suites au ralentissement critique"
 * est cite dans le cours de statistiques (§3, autocorrelation) mais n'a
 * pas encore ete fourni separement. Squelette seul pour l'instant --
 * cahier des charges de restructuration, decision explicite.
 */
export default function SuitesRalentissement() {
  return (
    <div className="page page-suites">
      <h1>Des suites au ralentissement critique</h1>
      <p className="lede">
        Construction progressive, depuis les suites numériques du programme de terminale, du modèle
        mathématique qui explique pourquoi la variance et l'autocorrélation montent près d'un point de
        bascule.
      </p>
      <div className="disclaimer">
        <p>
          <strong>Page en attente de contenu.</strong> Le cours de statistiques (§3, autocorrélation) cite
          ce polycopié comme référence pour la démonstration complète du lien entre suites géométriques et
          ralentissement critique -- il n'a pas encore été fourni séparément. En attendant, la dérivation
          complète (processus d'Ornstein-Uhlenbeck, linéarisation près d'un équilibre) reste visible dans le
          détail de chaque page <Link to="/resultats">Résultats</Link> concernée (H1, mode expert).
        </p>
      </div>
    </div>
  );
}
