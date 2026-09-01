import { useState } from "react";
import { INTERPRETATION } from "../data/interpretation.js";

/**
 * Pédagogie d'interprétation d'un résultat concret -- distincte de MethodNote
 * (qui explique le calcul). Ici : que veut dire CE verdict, et qu'est-ce
 * qu'il ne veut PAS dire. Toujours visible (pas de mode simplifié/expert ici
 * -- l'interprétation n'a qu'un seul niveau, contrairement à la formule).
 */
export default function InterpretationGuide({ hypothesis, outcome }) {
  const [showLimits, setShowLimits] = useState(false);
  const data = INTERPRETATION[hypothesis];
  if (!data) return null;

  const outcomeInfo = data.outcomes?.[outcome];

  return (
    <div className="interpretation-guide">
      {outcomeInfo && (
        <div className="interpretation-outcome">
          <p className="interpretation-outcome-title">{outcomeInfo.title}</p>
          <p>{outcomeInfo.text}</p>
        </div>
      )}

      <button type="button" className="interpretation-toggle" onClick={() => setShowLimits((v) => !v)}>
        {showLimits ? "Masquer les limites de cette mesure" : "Voir les limites de cette mesure et les erreurs à ne pas faire"}
      </button>

      {showLimits && (
        <div className="interpretation-details">
          {data.limits && (
            <>
              <p className="interpretation-section-title">Limites propres à cette mesure</p>
              <ul>
                {data.limits.map((l, i) => (
                  <li key={i}>{l}</li>
                ))}
              </ul>
            </>
          )}
          {data.commonMistakes && (
            <>
              <p className="interpretation-section-title">Ce que ce résultat ne veut PAS dire</p>
              <ul className="interpretation-mistakes">
                {data.commonMistakes.map((m, i) => (
                  <li key={i}>{m}</li>
                ))}
              </ul>
            </>
          )}
        </div>
      )}
    </div>
  );
}
