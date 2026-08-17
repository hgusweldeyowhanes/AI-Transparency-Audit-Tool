import { ReactNode } from "react";

export function MetricCard({
  label,
  value,
  hint,
}: {
  label: string;
  value: ReactNode;
  hint?: ReactNode;
}) {
  return (
    <div className="metric card">
      <div className="label">{label}</div>
      <div className="value">{value}</div>
      {hint ? <div>{hint}</div> : null}
    </div>
  );
}

export function Flags({ flags }: { flags: string[] }) {
  if (!flags.length) return <span className="flag ok-pill">clean</span>;
  return (
    <>
      {flags.map((flag) => (
        <span className="flag" key={flag}>
          {flag}
        </span>
      ))}
    </>
  );
}

export function PageState({
  error,
  loading,
  loadingText = "Loading…",
  children,
}: {
  error: string;
  loading: boolean;
  loadingText?: string;
  children: ReactNode;
}) {
  if (error) {
    return (
      <div>
        <p className="error">{error}</p>
        <p className="muted">Start the API on port 8000, then refresh.</p>
      </div>
    );
  }
  if (loading) return <p className="muted">{loadingText}</p>;
  return <>{children}</>;
}
