import { METHODS } from "../data/methods.js";
import Math from "./Math.jsx";

/** Découpe un texte contenant des segments $...$ et rend chacun en LaTeX inline. */
export function TextWithMath({ text }) {
  const parts = text.split(/(\$[^$]+\$)/g);
  return (
    <>
      {parts.map((part, i) =>
        part.startsWith("$") && part.endsWith("$") ? (
          <Math key={i} tex={part.slice(1, -1)} />
        ) : (
          <span key={i}>{part}</span>
        )
      )}
    </>
  );
}

/**
 * Explication de méthode statistique, déclinée en simplifié ou expert -- §3 :
 * jamais un résultat affiché sans son équivalent en langage courant, et le
 * mode expert doit montrer la DÉMONSTRATION complète (pas seulement la
 * formule), rendue en LaTeX, avec la référence bibliographique exacte.
 */
export default function MethodNote({ methodKeys, expertMode }) {
  const keys = Array.isArray(methodKeys) ? methodKeys : [methodKeys];

  if (!expertMode) {
    return (
      <div className="method-notes method-notes-simple">
        {keys.map((key) => {
          const m = METHODS[key];
          if (!m) return null;
          return (
            <p key={key} className="method-note-simple">
              <strong>Comment on vérifie « {m.label.toLowerCase()} » :</strong> {m.simple}
            </p>
          );
        })}
      </div>
    );
  }

  return (
    <div className="method-notes">
      {keys.map((key) => {
        const m = METHODS[key];
        if (!m) return null;
        return (
          <div key={key} className="method-note">
            <p className="method-note-label">{m.label}</p>
            <Math tex={m.formula} block />

            {m.derivationSteps ? (
              <div className="method-note-derivation">
                {m.derivationSteps.map((step, i) =>
                  step.tex ? (
                    <Math key={i} tex={step.tex} block={step.block} />
                  ) : (
                    <p key={i} className="method-note-detail">
                      <TextWithMath text={step.text} />
                    </p>
                  )
                )}
              </div>
            ) : (
              <p className="method-note-detail">
                <TextWithMath text={m.detail} />
              </p>
            )}

            <ul className="method-note-refs">
              {m.references.map((ref, i) => (
                <li key={i} className="method-note-ref">
                  {ref}
                </li>
              ))}
            </ul>
          </div>
        );
      })}
    </div>
  );
}
