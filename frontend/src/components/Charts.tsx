type Point = { x: number; y: number };

export function Sparkline({ values, color = "#2dd4bf" }: { values: number[]; color?: string }) {
  if (!values.length) return <svg className="spark" />;
  const max = Math.max(...values, 0.0001);
  const w = 320;
  const h = 120;
  const pts: Point[] = values.map((v, i) => ({
    x: (i / Math.max(values.length - 1, 1)) * w,
    y: h - (v / max) * (h - 8) - 4,
  }));
  const d = pts.map((p, i) => `${i === 0 ? "M" : "L"} ${p.x.toFixed(1)} ${p.y.toFixed(1)}`).join(" ");
  return (
    <svg className="spark" viewBox={`0 0 ${w} ${h}`} preserveAspectRatio="none">
      <path d={d} fill="none" stroke={color} strokeWidth="2.2" />
    </svg>
  );
}

export function Bar({ label, value, max, suffix = "" }: { label: string; value: number; max: number; suffix?: string }) {
  const pct = max ? Math.min(100, (value / max) * 100) : 0;
  return (
    <div className="bar-row">
      <div className="name">{label}</div>
      <div className="bar-track">
        <div className="bar-fill" style={{ width: `${pct}%` }} />
      </div>
      <div className="mono">{value}
        {suffix}</div>
    </div>
  );
}
