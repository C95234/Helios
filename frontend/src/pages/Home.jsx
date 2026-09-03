import { Link } from "react-router-dom";

export default function Home() {
  return (
    <div className="page page-home">
      <section className="hero">
        <h1>Un système social envoie des signes avant de basculer</h1>
        <p className="lede">
          Comme un écosystème avant qu'il ne change d'état, une société laisse parfois deviner, dans les
          statistiques, qu'elle devient plus fébrile avant une rupture visible. Hélios apprend à repérer ces
          signes — et à vérifier, honnêtement, s'ils se confirment.
        </p>
        <Link to="/demo" className="cta">
          Voir un exemple
        </Link>
      </section>

      <section className="origin">
        <p>
          Le projet est né d'un roman dans lequel deux chercheurs, <strong>Moussa et Louise</strong>, imaginent
          un outil pour détecter des signes de bascule sociale avant qu'ils ne deviennent visibles. Hélios en
          reprend l'intuition et la transforme en démarche scientifique testable.
        </p>
      </section>

      <section className="steps">
        <div className="step">
          <span className="step-number">1</span>
          <h2>On rassemble des données publiques</h2>
          <p>Des séries statistiques officielles, ouvertes, jamais individuelles.</p>
        </div>
        <div className="step">
          <span className="step-number">2</span>
          <h2>On cherche des signes de fébrilité avant une rupture</h2>
          <p>Une série qui devient plus variable, qui « oublie » plus lentement ses à-coups.</p>
        </div>
        <div className="step">
          <span className="step-number">3</span>
          <h2>On vérifie si ces signes se confirment vraiment</h2>
          <p>Un test statistique honnête, jamais un verdict affirmé sur un seul cas.</p>
        </div>
      </section>

      <section className="hypotheses-teaser">
        <h2>Trois questions précises, testées sur des données réelles</h2>
        <p>
          Au-delà des indicateurs, Hélios teste trois hypothèses de recherche originales — par exemple, «
          les réseaux sociaux montrent-ils des signes de tension avant les statistiques officielles ? ».
        </p>
        <Link to="/hypotheses" className="cta secondary">
          Voir les hypothèses
        </Link>
      </section>

      <section className="hypotheses-teaser">
        <h2>Ce que les tests donnent, une fois lancés à fond</h2>
        <p>
          H1, H2 et H3 testées sur un maximum de phénomènes réels disponibles, H4 sur plusieurs
          configurations de simulation — résultats honnêtes, y compris ce qui ne va pas dans le sens
          attendu.
        </p>
        <Link to="/conclusions" className="cta secondary">
          Voir les conclusions publiées
        </Link>
      </section>

      <section className="hypotheses-teaser">
        <h2>Le raisonnement scientifique, sans rien cacher</h2>
        <p>
          Avant de construire l'hypothèse H3, il fallait vérifier un postulat : le signal temporel
          précède-t-il toujours le signal spatial ? Un premier raisonnement s'est trompé -- le calcul l'a
          corrigé. Ce cheminement, erreur comprise, est documenté dans le Journal de recherche.
        </p>
        <Link to="/journal-recherche" className="cta secondary">
          Lire le journal de recherche
        </Link>
      </section>

      <section className="not-this">
        <p>
          Hélios n'identifie et ne surveille aucune personne. L'outil ne travaille que sur des données
          agrégées — des comptages, des indices, des séries officielles.
        </p>
      </section>
    </div>
  );
}
