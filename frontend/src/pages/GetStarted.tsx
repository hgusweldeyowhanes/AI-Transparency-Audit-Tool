import { FormEvent, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api, setApiKey } from "../api";

export default function GetStarted() {
  const nav = useNavigate();
  const [email, setEmail] = useState("");
  const [company, setCompany] = useState("");
  const [useCase, setUseCase] = useState("compliance");
  const [result, setResult] = useState<{ api_key: string; message: string } | null>(null);
  const [error, setError] = useState("");

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError("");
    try {
      const data = await api.trial({ email, company, use_case: useCase });
      setApiKey(data.api_key);
      setResult(data);
    } catch (err) {
      setError(String(err));
    }
  }

  return (
    <section className="section" style={{ maxWidth: 640 }}>
      <div className="kicker">Free trial</div>
      <h1>API key in one form</h1>
      <p className="muted">
        Day 1 of the GTM trial: email, company, use case. This local MVP returns the demo key and unlocks the
        seeded dashboard.
      </p>
      {!result ? (
        <form className="card" onSubmit={onSubmit} style={{ display: "grid", gap: 12, marginTop: 24 }}>
          <div>
            <label>Work email</label>
            <input required type="email" value={email} onChange={(e) => setEmail(e.target.value)} />
          </div>
          <div>
            <label>Company</label>
            <input value={company} onChange={(e) => setCompany(e.target.value)} />
          </div>
          <div>
            <label>Use case</label>
            <select value={useCase} onChange={(e) => setUseCase(e.target.value)}>
              <option value="compliance">Regulatory compliance</option>
              <option value="debugging">Production debugging</option>
              <option value="compare">Model comparison</option>
            </select>
          </div>
          {error && <div className="error">{error}</div>}
          <button className="btn btn-primary" type="submit">
            Issue key
          </button>
        </form>
      ) : (
        <div className="card" style={{ marginTop: 24 }}>
          <p className="notice">{result.message}</p>
          <p>
            API key: <span className="mono">{result.api_key}</span>
          </p>
          <pre className="block">{`export AUDIT_API_KEY=${result.api_key}
export AUDIT_BASE_URL=http://localhost:8000`}</pre>
          <div className="cta-row">
            <button className="btn btn-primary" onClick={() => nav("/app")}>
              Open dashboard
            </button>
            <Link className="btn btn-ghost" to="/docs">
              Integration docs
            </Link>
          </div>
        </div>
      )}
    </section>
  );
}
