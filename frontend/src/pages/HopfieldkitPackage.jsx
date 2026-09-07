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
        <p className="text-muted">
          Code source : <a href={HOPFIELDKIT_INFO.repoUrl} target="_blank" rel="noreferrer">{HOPFIELDKIT_INFO.repoUrl}</a>.
          Paquet : <a href={HOPFIELDKIT_INFO.pypiUrl} target="_blank" rel="noreferrer">{HOPFIELDKIT_INFO.pypiUrl}</a> --{" "}
          <code>pip install hopfieldkit</code>.
        </p>
      </section>

      <section>
        <h2>Aperçu du code</h2>
        <p className="text-muted"><code>hopfieldkit/hebbian.py</code> -- apprentissage en un coup</p>
        <pre className="code-block">
          <code>{`class HopfieldNetwork(BaseHopfieldNetwork):
    def fit(self, patterns):
        """W = (1/n) * sum_mu (x^mu outer x^mu), diagonale annulée."""
        w = np.zeros((self.n_units, self.n_units))
        for pattern in patterns:
            w += np.outer(pattern, pattern)
        w /= self.n_units
        np.fill_diagonal(w, 0.0)
        self.weights = w
        return self`}</code>
        </pre>
        <p className="text-muted"><code>hopfieldkit/perceptron.py</code> -- apprentissage itératif par marge (Gardner)</p>
        <pre className="code-block">
          <code>{`class PerceptronHopfieldNetwork(BaseHopfieldNetwork):
    def fit(self, patterns, max_epochs=500, seed=None):
        w = np.zeros((n, n))
        for epoch in range(max_epochs):
            for mu in rng.permutation(n_patterns):
                x = patterns[mu]
                stabilities = x * (w @ x)          # x_i * h_i pour chaque unite
                violated = stabilities <= self.kappa
                if not violated.any():
                    continue
                delta = (self.learning_rate / n) * np.outer(x, x)
                np.fill_diagonal(delta, 0.0)
                # symetrique par construction : voir la note du module
                update_mask = violated[:, None] | violated[None, :]
                w += delta * update_mask
        self.weights = w
        return self`}</code>
        </pre>
        <p className="text-muted">
          Code complet, commenté et testé (théorie de la capacité, diagnostics) : voir le dépôt lié ci-dessus.
        </p>
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
          <code>pip install hopfieldkit</code> est réellement fonctionnel publiquement depuis la version 0.1.0.
          Le statut ci-dessus (« {status.label} ») reflète l'état réel, pas un objectif.
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
