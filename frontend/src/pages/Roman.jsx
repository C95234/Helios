import { Link } from "react-router-dom";

export default function Roman() {
  return (
    <div className="page page-roman">
      <h1>Le roman</h1>
      <p className="lede">
        Le contexte narratif dont s'inspire Hélios -- sans dévoiler l'intrigue, séparé du contenu
        scientifique pour ne jamais laisser penser que la fiction est une preuve.
      </p>

      <section>
        <p>
          Le projet est né d'un roman dans lequel deux chercheurs, <strong>Moussa et Louise</strong>,
          imaginent un outil pour détecter des signes de bascule sociale avant qu'ils ne deviennent
          visibles -- un instrument capable de lire, dans les statistiques, la fébrilité d'une société qui
          se rapproche d'un point de rupture.
        </p>
        <p>
          Le roman met aussi en scène un second dispositif, le <strong>RCA</strong> (contrôle actif de la
          synchronisation) : plutôt que de simplement détecter une bascule à venir, il cherche à
          l'empêcher -- non pas en supprimant toute agitation, mais en affaiblissant sélectivement les
          liens entre les éléments qui commencent à se synchroniser entre eux. C'est cette intuition qui a
          inspiré le module <Link to="/resultats/h4">H4</Link> d'Hélios : une traduction mathématique
          directe (modèle de Kuramoto et couplage adaptatif), en simulation, jamais présentée comme une
          preuve de ce que le RCA du roman pourrait faire dans le monde réel.
        </p>
        <p>
          Hélios reprend l'intuition du roman et la transforme en démarche scientifique testable : les
          hypothèses H1, H2 et H3 sont des questions de recherche réelles, testées sur des données réelles,
          avec un protocole qui accepte explicitement de dire « non » quand les données ne vont pas dans le
          sens attendu -- voir <Link to="/bilan">le Bilan</Link>.
        </p>
      </section>
    </div>
  );
}
