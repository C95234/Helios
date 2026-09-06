import { Link } from "react-router-dom";
import ResultPageTemplate from "../../components/ResultPageTemplate.jsx";

export default function HopfieldResult() {
  return (
    <ResultPageTemplate
      code="Hopfield"
      title="Mémoire collective (Hopfield)"
      catchyTitle="Comment un groupe se souvient de ce qu'il a déjà vécu"
      domain={{ name: "Mémoire collective", to: "/resultats#memoire-collective" }}
      verdict="simulation"
      episodesLabel="démonstration pédagogique, non testée empiriquement"
      summary="Comment un groupe reconnaît-il une situation déjà vécue, et combien de situations distinctes peut-il retenir avant de les confondre ? Un réseau de Hopfield (mémoire associative, prix Nobel de physique 2024) mémorise des configurations sociales passées et les retrouve à partir d'un signal partiel -- jusqu'à un seuil de charge précis, au-delà duquel le rappel se dégrade nettement."
      postulateSimple="Est-ce qu'un mécanisme de mémoire associative -- des liens qui se renforcent quand une séquence d'événements se répète -- peut expliquer comment un groupe social reconnaît une situation déjà vécue, et combien de situations distinctes il peut retenir avant de les confondre ?"
      postulateExpert="Un réseau de Hopfield (Hopfield, 1982), entraîné par apprentissage hebbien sur des configurations sociales passées, converge toujours vers un état stable (théorème de convergence par décroissance de l'énergie) et retrouve un motif mémorisé à partir d'un signal partiel corrompu -- jusqu'à un seuil de capacité (Amit-Gutfreund-Sompolinsky, 1985, p_max ≈ 0,138 N) au-delà duquel le bruit de diaphonie entre motifs domine le signal. Le mécanisme qui explique ici la perte de stabilité d'un souvenir collectif éclaire, sous un autre angle, ce qu'on observe aussi dans le domaine Société (ralentissement critique, §5.1) -- une convergence entre deux domaines, pas une dépendance de l'un envers l'autre."
      resultText={
        <>
          <p className="text-muted">
            Démonstration numérique déjà produite (<code>backend/scripts/hopfield_social.py</code>, graine
            42) -- présentée ici en mode simplifié, avec la démonstration mathématique complète (théorème de
            convergence, calcul de la capacité) dans le cours lié ci-dessous.
          </p>
          <dl className="signal-stats">
            <div>
              <dt>Exemple à 4 territoires : signal corrompu reconnu</dt>
              <dd>énergie −1,00 (état stable retrouvé)</dd>
            </div>
            <div>
              <dt>Capacité de mémoire (N=100)</dt>
              <dd>rappel fiable jusqu'à p≈10, chute nette au-delà de p≈13</dd>
            </div>
          </dl>
          <figure className="chart-box">
            <img
              src="/images/hopfield_social_results.png"
              alt="Énergie pendant le rappel (exemple à 4 territoires) et capacité de mémoire empirique pour N=100, comparée aux seuils de Hopfield (1982) et Amit-Gutfreund-Sompolinsky (1985)"
              style={{ maxWidth: "100%", borderRadius: "var(--radius)" }}
            />
            <figcaption className="text-muted">
              Gauche : énergie décroissante pendant le rappel d'un signal partiellement corrompu (le réseau
              retrouve l'état mémorisé). Droite : taux de rappel correct en fonction du nombre de motifs
              mémorisés -- le taux reste proche de 100% jusqu'à p≈10, puis décroît, franchissant 50% à
              p=16, entre le seuil prudent de Hopfield (≈5,4) et le seuil AGS (≈13,8).
            </figcaption>
          </figure>
          <p className="text-muted">
            Détail complet, démonstrations et exercices corrigés : <Link to="/methode/hopfield">cours Hopfield</Link>.
          </p>
          <p className="text-muted">
            Ce même code est aussi généralisé en un paquet Python autonome, testé, à part :{" "}
            <Link to="/positionnement/hopfieldkit">hopfieldkit</Link> -- un geste vers la communauté, pas une
            dépendance de ce module.
          </p>
        </>
      }
      methodLink={{ to: "/methode/hopfield", label: "Voir la démonstration complète (convergence, capacité de mémoire)" }}
      limits={[
        "Démonstration pédagogique, pas un test statistique : aucun verdict « confirmée / infirmée » n'est jamais attaché à ce module, comme H4.",
        "Analogie, pas un modèle sociologique validé : de vrais groupes sociaux ne sont pas des variables binaires, leurs interactions ne sont pas symétriques comme l'exige le théorème de convergence, et « retenir une configuration sociale » n'a pas le sens précis qu'a « mémoriser un motif » dans un réseau de Hopfield.",
        "Le réseau de Hopfield est un modèle établi (prix Nobel de physique 2024) appliqué ici à un nouveau cas d'école -- comprendre et expliquer, pas revendiquer une découverte.",
      ]}
      showLiveSection={false}
    />
  );
}
