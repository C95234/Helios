import { METHODS } from "../data/methods.js";

/**
 * Explication de méthode statistique, déclinée en simplifié ou expert -- §3 :
 * jamais un résultat affiché sans son équivalent en langage courant, et jamais
 * un résultat expert sans formule + référence.
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
            <code className="method-note-formula">{m.formula}</code>
            <p className="method-note-detail">{m.detail}</p>
            <p className="method-note-ref">{m.reference}</p>
          </div>
        );
      })}
    </div>
  );
}
