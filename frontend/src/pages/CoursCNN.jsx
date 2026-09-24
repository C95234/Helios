import { Link } from "react-router-dom";
import CoursBlock from "../components/CoursBlock.jsx";
import { CNN_SECTIONS, CNN_REFERENCES } from "../data/coursCNN.js";

export default function CoursCNN() {
  return (
    <div className="page page-cours">
      <h1>Réseaux de neurones convolutifs et rétropropagation</h1>
      <p className="lede">
        Démonstration complète -- pas seulement la formule finale -- du classifieur de deep learning utilisé
        dans le <Link to="/resultats/ia-vs-statistiques">banc d'essai IA vs statistiques</Link> : convolution,
        passe avant sur un exemple jouet calculé à la main, puis rétropropagation et descente de gradient,
        chaque résultat vérifié par le code.
      </p>
      <p className="text-muted">
        Complément indépendant au <Link to="/methode/cours-statistiques">cours de statistiques</Link> (les
        méthodes classiques du projet) -- même niveau d'exigence, sujet différent. Voir aussi{" "}
        <Link to="/methode/hopfield">Réseaux de Hopfield et groupes sociaux</Link> pour un second exemple de
        descente de gradient (règle de type perceptron).
      </p>

      <nav className="cours-toc">
        {CNN_SECTIONS.map((s) => (
          <a key={s.id} href={`#${s.id}`}>
            {s.number}. {s.title}
          </a>
        ))}
      </nav>

      {CNN_SECTIONS.map((section) => (
        <section key={section.id} id={section.id} className="cours-section">
          <h2>
            {section.number}. {section.title}
          </h2>
          {section.blocks.map((block, i) => (
            <CoursBlock key={i} block={block} />
          ))}
        </section>
      ))}

      <section className="cours-section">
        <h2>Références</h2>
        <ul className="bibliography-list">
          {CNN_REFERENCES.map((ref, i) => (
            <li key={i}>{ref}</li>
          ))}
        </ul>
      </section>

      <div className="simulation-banner">
        <strong>Mise en garde essentielle :</strong>
        <span>
          Ce document explique le classifieur réellement utilisé dans le banc d'essai, pas une avancée en
          apprentissage profond : convolution, rétropropagation et descente de gradient sont des méthodes
          établies depuis les années 1980 (Rumelhart, Hinton & Williams, 1986), enseignées dans tout cours
          d'introduction au deep learning. L'architecture elle-même est volontairement modeste -- voir la
          section 2 -- pas une reproduction de travaux de recherche plus sophistiqués sur le même sujet
          (Bury et al., 2021).
        </span>
      </div>
    </div>
  );
}
