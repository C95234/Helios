import { useState } from "react";
import { Link } from "react-router-dom";
import { STATUS_LABELS } from "../data/hypotheses.js";

export default function HypothesisCard({ hypothesis }) {
  const [expertMode, setExpertMode] = useState(false);
  const [showDetail, setShowDetail] = useState(false);
  const { code, title, simple, expert, status, statusNote, link, detailReasons } = hypothesis;

  return (
    <div className="hypothesis-card">
      <div className="result-card-header">
        <h3>
          <span className="hypothesis-code">{code}</span> — {title}
        </h3>
        <button
          type="button"
          className="mode-toggle"
          onClick={() => setExpertMode((v) => !v)}
          aria-pressed={expertMode}
        >
          {expertMode ? "Mode simplifié" : "Mode expert"}
        </button>
      </div>

      <p>{expertMode ? expert : simple}</p>

      <div className={`hypothesis-status hypothesis-status--${status}`}>
        <span className="hypothesis-status-label">{STATUS_LABELS[status]}</span>
        <p>{statusNote}</p>
        {link && (
          <Link to={link.to} className="hypothesis-status-link">
            {link.label} →
          </Link>
        )}
        {detailReasons && (
          <>
            <button type="button" className="interpretation-toggle" onClick={() => setShowDetail((v) => !v)}>
              {showDetail ? "Masquer le détail technique" : "Pourquoi exactement ? →"}
            </button>
            {showDetail && (
              <ul className="hypothesis-detail-reasons">
                {detailReasons.map((r, i) => (
                  <li key={i}>{r}</li>
                ))}
              </ul>
            )}
          </>
        )}
      </div>
    </div>
  );
}
