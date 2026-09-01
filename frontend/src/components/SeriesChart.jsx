import { CartesianGrid, Line, LineChart, ReferenceLine, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

export default function SeriesChart({ dates, values, color = "var(--color-accent)", markIndex, label }) {
  const data = dates.map((d, i) => ({ date: d, value: values[i] }));
  return (
    <div className="series-chart">
      {label && <div className="series-chart-label">{label}</div>}
      <ResponsiveContainer width="100%" height={180}>
        <LineChart data={data} margin={{ top: 8, right: 16, bottom: 0, left: -16 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
          <XAxis dataKey="date" tick={{ fontSize: 10 }} minTickGap={40} />
          <YAxis tick={{ fontSize: 10 }} width={48} domain={["auto", "auto"]} />
          <Tooltip />
          {typeof markIndex === "number" && dates[markIndex] && (
            <ReferenceLine x={dates[markIndex]} stroke="var(--color-warn)" strokeDasharray="4 2" />
          )}
          <Line type="monotone" dataKey="value" stroke={color} dot={false} strokeWidth={2} connectNulls />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
