export default function Gauge({ value, label }) {
  const pct = Math.max(0, Math.min(1, value)) * 100;
  const color = pct > 66 ? "var(--color-warn)" : pct > 33 ? "var(--color-mid)" : "var(--color-calm)";
  return (
    <div className="gauge">
      {label && <div className="gauge-label">{label}</div>}
      <div className="gauge-track">
        <div className="gauge-fill" style={{ width: `${pct}%`, background: color }} />
      </div>
    </div>
  );
}
