import { formatSavedAt } from "../history.js";

/** Liste d'entrées d'historique local (localStorage) -- cliquer recharge le résultat sans recalculer. */
export default function HistoryPanel({ entries, onSelect, onClear, renderLabel }) {
  if (!entries || entries.length === 0) return null;

  return (
    <div className="history-panel">
      <div className="history-panel-header">
        <span>Historique sur cet appareil ({entries.length})</span>
        <button type="button" className="history-clear" onClick={onClear}>
          Effacer
        </button>
      </div>
      <ul className="history-list">
        {entries.map((entry, i) => (
          <li key={i}>
            <button type="button" className="history-item" onClick={() => onSelect(entry)}>
              <span className="history-item-label">{renderLabel(entry)}</span>
              <span className="history-item-date">{formatSavedAt(entry.savedAt)}</span>
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
