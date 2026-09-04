import Math from "./Math.jsx";
import { TextWithMath } from "./MethodNote.jsx";

const TYPE_LABEL = {
  definition: "Définition",
  propriete: "Propriété",
  theoreme: "Théorème",
  remarque: "Remarque",
  exemple: "Exemple corrigé",
  exercice: "Exercice",
};

function BlockBody({ body }) {
  return (
    <>
      {body.map((item, i) => {
        if (item.table) {
          return (
            <div className="table-scroll" key={i}>
              <table className="agg-table">
                <thead>
                  <tr>
                    {item.table.headers.map((h) => (
                      <th key={h}>{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {item.table.rows.map((row, r) => (
                    <tr key={r}>
                      {row.map((cell, c) => (
                        <td key={c}>{cell}</td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          );
        }
        if (item.tex) return <Math key={i} tex={item.tex} block={item.block} />;
        return (
          <p key={i}>
            <TextWithMath text={item.text} />
          </p>
        );
      })}
    </>
  );
}

/** Un bloc typé du cours (définition, théorème, exemple...) -- même code couleur
 * que le document source, pour rester repérable en un coup d'œil. */
export default function CoursBlock({ block }) {
  return (
    <div className={`cours-block cours-block--${block.type}`}>
      <p className="cours-block-label">
        {TYPE_LABEL[block.type]}
        {block.title ? ` — ${block.title}` : ""}
      </p>
      <BlockBody body={block.body} />
      {block.proof && (
        <div className="cours-block-proof">
          <p className="cours-block-sublabel">Démonstration</p>
          <BlockBody body={block.proof} />
          <p className="cours-block-qed">∎</p>
        </div>
      )}
      {block.correction && (
        <div className="cours-block-proof">
          <p className="cours-block-sublabel">Corrigé</p>
          <BlockBody body={block.correction} />
        </div>
      )}
    </div>
  );
}
