import { useState } from "react";
import Gauge from "./Gauge.jsx";
import MethodNote from "./MethodNote.jsx";

/**
 * Chaque résultat existe à deux niveaux (§3 du cahier des charges) :
 * un mode simplifié par défaut, et un mode expert activable au même endroit,
 * jamais sur une page séparée. `methodKeys` relie le résultat aux outils
 * mathématiques utilisés (data/methods.js), décrits différemment selon le mode.
 */
export default function ResultCard({ title, simpleSentence, gaugeValue, gaugeLabel, expert, chart, methodKeys }) {
  const [expertMode, setExpertMode] = useState(false);

  return (
    <div className="result-card">
      <div className="result-card-header">
        <h3>{title}</h3>
        <button
          type="button"
          className="mode-toggle"
          onClick={() => setExpertMode((v) => !v)}
          aria-pressed={expertMode}
        >
          {expertMode ? "Mode simplifié" : "Mode expert"}
        </button>
      </div>

      {!expertMode && (
        <div className="result-simple">
          <p>{simpleSentence}</p>
          {typeof gaugeValue === "number" && <Gauge value={gaugeValue} label={gaugeLabel} />}
          {methodKeys && <MethodNote methodKeys={methodKeys} expertMode={false} />}
        </div>
      )}

      {expertMode && (
        <div className="result-expert">
          {expert}
          {methodKeys && <MethodNote methodKeys={methodKeys} expertMode={true} />}
        </div>
      )}

      {chart && <div className="result-chart">{chart}</div>}
    </div>
  );
}
