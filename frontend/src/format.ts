export function pct(value: number, digits = 1) {
  return `${(value * 100).toFixed(digits)}%`;
}

export function usd(value: number, digits = 2) {
  return `$${value.toFixed(digits)}`;
}

export function when(iso: string) {
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return iso;
  return d.toISOString().slice(0, 16).replace("T", " ");
}

export function deltaClass(value: number | null | undefined) {
  if (value == null) return "";
  if (value > 0.02) return "up";
  if (value < -0.02) return "down";
  return "";
}
