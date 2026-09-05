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
          Le roman met aussi en scène un second dispositif, complètement distinct d'Hélios : le{" "}
          <strong>RCA</strong> (Réacteur à Cohérence Adaptative), un générateur d'énergie par fusion
          nucléaire à confinement magnétique -- un problème de physique des plasmas, sans aucun rapport
          avec la prédiction sociale. Sa prouesse n'est pas de supprimer toute turbulence dans le plasma,
          mais de l'empêcher de se synchroniser en un seul emballement catastrophique -- en affaiblissant
          sélectivement les couplages entre les zones qui commencent à se verrouiller entre elles, plutôt
          qu'en figeant l'ensemble.
        </p>
        <p>
          Cette intuition de contrôle a inspiré trois choses distinctes dans Hélios, qu'il ne faut jamais
          confondre : le module <Link to="/resultats/h4">H4</Link> en traduit le{" "}
          <strong>principe de contrôle</strong> en simulation abstraite (modèle de Kuramoto, un réseau
          social illustratif -- jamais du vrai plasma) ; le module{" "}
          <Link to="/resultats/fusion">Fusion</Link> teste si le{" "}
          <strong>principe de détection</strong> qui sous-tend H1 et H2 (variance, autocorrélation, indice
          de Moran) repère aussi la fébrilité qui précède une vraie disruption, sur des données réelles de
          tokamak (MAST) -- puisque c'est précisément le domaine physique où le RCA du roman est censé
          opérer ; le module <Link to="/resultats/plasma-modele">Modèle de plasma</Link> pousse cette même
          question de détection sur un vrai modèle réduit de bilan de puissance (seuil d'ignition, critère
          de Lawson) plutôt que sur une donnée mesurée. Aucun des trois modules ne prétend reproduire le
          RCA lui-même : H4 ne pilote aucun vrai système, et Fusion comme Modèle de plasma se limitent à la
          détection, jamais au contrôle -- concevoir un vrai système de contrôle de plasma est hors du
          périmètre de ce projet.
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
