import { Link } from "react-router-dom";
import CoursBlock from "../components/CoursBlock.jsx";
import { COURS_SECTIONS, COURS_BILAN, COURS_REFERENCES } from "../data/coursStatistiques.js";

export default function CoursStatistiques() {
  return (
    <div className="page page-cours">
      <h1>Cours de statistiques appliquées</h1>
      <p className="lede">
        Les notions utilisées dans le projet Hélios, démontrées et travaillées. Ce cours couvre, dans
        l'ordre où elles s'enchaînent logiquement, toutes les notions statistiques utilisées dans le
        projet — définies, démontrées quand c'est possible avec les outils du programme de terminale,
        illustrées par un exemple entièrement résolu, puis reprises dans un exercice corrigé.
      </p>
      <p className="text-muted">
        Emplacement unique de ces démonstrations sur le site : les pages{" "}
        <Link to="/resultats">Résultats</Link> y renvoient plutôt que de les reproduire.
      </p>

      <nav className="cours-toc">
        {COURS_SECTIONS.map((s) => (
          <a key={s.id} href={`#${s.id}`}>
            {s.number}. {s.title}
          </a>
        ))}
      </nav>

      {COURS_SECTIONS.map((section) => (
        <section key={section.id} id={section.id} className="cours-section">
          <h2>
            {section.number}. {section.title}
          </h2>
          {section.blocks.map((block, i) => (
            <CoursBlock key={i} block={block} />
          ))}
        </section>
      ))}

      <section className="cours-section" id="bilan">
        <h2>9. Bilan</h2>
        <div className="table-scroll">
          <table className="agg-table">
            <thead>
              <tr>
                <th>Notion</th>
                <th>Rôle dans Hélios</th>
              </tr>
            </thead>
            <tbody>
              {COURS_BILAN.map((row) => (
                <tr key={row.notion}>
                  <td>{row.notion}</td>
                  <td>{row.role}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section className="cours-section">
        <h2>Références</h2>
        <ul className="bibliography-list">
          {COURS_REFERENCES.map((ref, i) => (
            <li key={i}>{ref}</li>
          ))}
        </ul>
      </section>
    </div>
  );
}
