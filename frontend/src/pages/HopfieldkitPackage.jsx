import { Link } from "react-router-dom";
import StatusBadge from "../components/StatusBadge.jsx";
import { HOPFIELDKIT_INFO, HOPFIELDKIT_STATUS } from "../data/positionnement.js";

export default function HopfieldkitPackage() {
  const status = HOPFIELDKIT_STATUS[HOPFIELDKIT_INFO.status];

  return (
    <div className="page page-positionnement">
      <p className="breadcrumb">
        <Link to="/positionnement">Positionnement scientifique</Link> <span aria-hidden="true">›</span> hopfieldkit
      </p>

      <h1>hopfieldkit</h1>
      <p className="lede">{HOPFIELDKIT_INFO.summary}</p>
      <p>
        <StatusBadge label={status.label} tone={status.tone} />
      </p>

      <section>
        <h2>Pourquoi un paquet autonome, pas une contribution</h2>
        <p>{HOPFIELDKIT_INFO.gapFound}</p>
      </section>

      <section>
        <h2>Le code et les tests</h2>
        <p>
          Apprentissage hebbien (<code>HopfieldNetwork</code>) et un second mode d'apprentissage par règle de
          type perceptron avec marge de stabilité (<code>PerceptronHopfieldNetwork</code>, Gardner 1988 ;
          Diederich & Opper 1987), plus les bornes théoriques de capacité (Hopfield 1982 ; Amit-Gutfreund-
          Sompolinsky 1985) et des diagnostics des limites connues (attracteurs parasites, dépendance à
          l'ordre de mise à jour) -- le même phénomène déjà observé et documenté dans la démonstration
          Hélios du domaine Mémoire collective.
        </p>
        <p>
          Comparaison empirique mesurée (N=100, 15% de bits corrompus, 20 essais par point) : le taux de
          rappel exact de la règle de Hebb s'effondre au-delà d'une quinzaine de motifs mémorisés, tandis que
          la règle de type perceptron continue de récupérer environ la moitié des motifs corrompus bien
          au-delà -- un écart réel et mesuré, pas supposé à l'avance. Ce paquet n'atteint pas la borne
          théorique de Gardner (~2N) : par construction, la matrice de poids est maintenue symétrique pendant
          l'apprentissage (pour rester dans le cadre énergétique classique de Hopfield, nécessaire à la
          garantie de convergence du rappel) -- un compromis documenté, pas caché, qui coûte de la capacité
          par rapport à l'algorithme non contraint de la littérature.
        </p>
        <dl className="signal-stats">
          <div>
            <dt>Tests</dt>
            <dd>{HOPFIELDKIT_INFO.nTests}, tous passants</dd>
          </div>
        </dl>
      </section>

      <section>
        <h2>Pistes d'usage</h2>
        <ul>
          {HOPFIELDKIT_INFO.usageAngles.map((angle) => (
            <li key={angle}>{angle}</li>
          ))}
        </ul>
      </section>

      <section>
        <h2>Statut, tenu à jour honnêtement</h2>
        <p>
          Ce site ne dit jamais que <code>hopfieldkit</code> est publié tant que <code>pip install
          hopfieldkit</code> n'est pas réellement fonctionnel publiquement. Le statut ci-dessus (« {status.label} »)
          reflète l'état réel.
        </p>
        <p className="text-muted">
          Hélios n'a jamais dépendu de ce paquet pour son propre module Mémoire collective -- ce paquet en est
          la version généralisée et publiable, pas un doublon : voir{" "}
          <Link to="/resultats/hopfield">le résultat du domaine Mémoire collective</Link>.
        </p>
      </section>

      <p className="text-muted">
        Voir aussi <Link to="/positionnement">Positionnement scientifique</Link> et{" "}
        <Link to="/positionnement/ewstools">la contribution à ewstools</Link>.
      </p>
    </div>
  );
}
