import { Link } from "react-router-dom";
import CoursBlock from "../components/CoursBlock.jsx";
import { HOPFIELD_SECTIONS, HOPFIELD_REFERENCES } from "../data/hopfieldSocial.js";

export default function HopfieldSocial() {
  return (
    <div className="page page-cours">
      <h1>Réseaux de Hopfield appliqués aux groupes sociaux</h1>
      <p className="lede">
        Comprendre, par les mathématiques, la logique du logiciel de Moussa et Louise. Ce document explique
        un des modèles fondateurs du deep learning -- le réseau de Hopfield (prix Nobel de physique 2024) --
        appliqué, par analogie pédagogique, à des groupes sociaux. L'idée directrice reprend littéralement un
        principe évoqué dans <Link to="/roman">le roman</Link> qui inspire ce projet : des liens qui se
        renforcent quand une séquence d'événements se répète, formant une mémoire du système.
      </p>
      <p className="text-muted">
        Support théorique du domaine{" "}
        <Link to="/resultats#memoire-collective">Mémoire collective</Link> -- voir le résultat sur{" "}
        <Link to="/resultats/hopfield">sa propre page</Link>. Complément au{" "}
        <Link to="/methode/cours-statistiques">cours de statistiques</Link>, indépendant des domaines
        Société et Fusion nucléaire.
      </p>

      <nav className="cours-toc">
        {HOPFIELD_SECTIONS.map((s) => (
          <a key={s.id} href={`#${s.id}`}>
            {s.number}. {s.title}
          </a>
        ))}
      </nav>

      {HOPFIELD_SECTIONS.map((section) => (
        <section key={section.id} id={section.id} className="cours-section">
          <h2>
            {section.number}. {section.title}
          </h2>
          {section.blocks.map((block, i) => (
            <CoursBlock key={i} block={block} />
          ))}
          {section.id === "capacite-memoire" && (
            <figure className="chart-box">
              <img
                src="/images/hopfield_social_results.png"
                alt="Énergie pendant le rappel (exemple à 4 territoires) et capacité de mémoire empirique pour N=100, comparée aux seuils de Hopfield (1982) et Amit-Gutfreund-Sompolinsky (1985)"
                style={{ maxWidth: "100%", borderRadius: "var(--radius)" }}
              />
              <figcaption className="text-muted">
                Généré par <code>backend/scripts/hopfield_social.py</code> (graine 42) -- panneau de gauche :
                énergie pendant le rappel de l'exemple à 4 territoires (§3) ; panneau de droite : taux de
                rappel correct en fonction du nombre de motifs mémorisés, $N=100$.
              </figcaption>
            </figure>
          )}
        </section>
      ))}

      <section className="cours-section">
        <h2>Références</h2>
        <ul className="bibliography-list">
          {HOPFIELD_REFERENCES.map((ref, i) => (
            <li key={i}>{ref}</li>
          ))}
        </ul>
      </section>

      <div className="simulation-banner">
        <strong>Mise en garde essentielle :</strong>
        <span>
          Ce document propose une analogie pédagogique, pas un modèle sociologique validé. De vrais groupes
          sociaux ne sont pas des variables binaires, leurs interactions ne sont pas symétriques comme
          l'exige le théorème de convergence, et « retenir une configuration sociale » n'a pas le sens précis
          et univoque qu'a « mémoriser un motif » dans un réseau de Hopfield. L'intérêt de ce document est
          d'expliquer, avec des mathématiques exactes et vérifiables, le <em>type</em> de logique qu'un
          système comme Hélios pourrait mobiliser -- mémoire associative, attracteurs, perte de stabilité --
          pas de prouver que les sociétés réelles fonctionnent ainsi. Le réseau de Hopfield n'est par
          ailleurs pas une nouveauté (prix Nobel de physique 2024) : ce document applique une théorie établie
          à un nouveau cas d'école, dans le même esprit que le reste d'Hélios -- comprendre et expliquer, pas
          revendiquer une avancée scientifique.
        </span>
      </div>
    </div>
  );
}
