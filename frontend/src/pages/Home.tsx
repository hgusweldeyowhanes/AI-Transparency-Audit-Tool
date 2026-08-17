import { Link } from "react-router-dom";

export default function Home() {
  return (
    <>
      <section className="hero">
        <div className="kicker">Open-source LLM audit trail</div>
        <h1>Prove your LLM is safe &amp; transparent</h1>
        <p className="lede">
          Ship with confidence. A compliance-first ledger of every model decision — search, drift,
          failure clusters, and EU AI Act / SEC-ready report templates.
        </p>
        <div className="cta-row">
          <Link className="btn btn-primary" to="/start">
            Get started free
          </Link>
          <Link className="btn btn-ghost" to="/app">
            Open live demo
          </Link>
        </div>
        <div className="trust" style={{ marginTop: 28 }}>
          <span>Self-hosted · Apache 2.0</span>
          <span>GDPR-ready retention knobs</span>
          <span>SOC 2: bring your own</span>
          <span>Claude · GPT-4o · Llama</span>
        </div>
        <div className="video-frame">
          <div style={{ textAlign: "center" }}>
            <div className="kicker">2-min product walkthrough</div>
            <p className="muted">Ingest → flag → drift incident → compliance pack</p>
            <Link to="/app/drift" className="btn btn-gold">
              Jump to the seeded incident
            </Link>
          </div>
        </div>
      </section>

      <section className="section">
        <h2>Built for regulators, used by engineers</h2>
        <p className="muted">Arize monitors ML. Datadog monitors everything. We specialize in LLM governance.</p>
        <div className="grid-3" style={{ marginTop: 28 }}>
          <article className="card">
            <h3>Complete audit trail</h3>
            <p className="muted">Every prompt, completion, model, token, cost, and prompt version — searchable in seconds.</p>
          </article>
          <article className="card">
            <h3>Failure detection</h3>
            <p className="muted">Heuristics for empty replies, refusals, knowledge gaps, ungrounded citations, and PII-like strings.</p>
          </article>
          <article className="card">
            <h3>Compliance packs</h3>
            <p className="muted">EU AI Act logging templates and SEC-style evidence rooms. Engineering artifacts, not legal advice.</p>
          </article>
        </div>
      </section>

      <section className="section">
        <h2>Who this is for</h2>
        <div className="grid-3" style={{ marginTop: 22 }}>
          <article className="card">
            <div className="kicker">Finance</div>
            <h3>Banks, fintech, insurance</h3>
            <p className="muted">SEC disclosure pressure and Fed-style guidance. Willingness to pay is high; the audit trail has to exist before the exam.</p>
          </article>
          <article className="card">
            <div className="kicker">Healthcare</div>
            <h3>Hospitals &amp; payers</h3>
            <p className="muted">HIPAA + malpractice exposure on documentation and triage assistants. Legal review is the bottleneck — give them a packet.</p>
          </article>
          <article className="card">
            <div className="kicker">AI-native SaaS</div>
            <h3>Startups shipping copilots</h3>
            <p className="muted">Customer trust, diligence questionnaires, and the board asking why quality slipped after last week's prompt change.</p>
          </article>
        </div>
      </section>

      <section className="section faq">
        <h2>FAQ</h2>
        <details>
          <summary>Is the free tier actually free?</summary>
          <p>Yes. Self-host with unlimited events, core search, and basic drift. Default retention is 30 days. Community support only.</p>
        </details>
        <details>
          <summary>Does this certify EU AI Act conformity?</summary>
          <p>No. Reports are templates mapped to logging and transparency themes. Your counsel still owns the legal analysis.</p>
        </details>
        <details>
          <summary>How do you detect hallucinations without another LLM?</summary>
          <p>Ungrounded citations (policy/ticket IDs that never appeared in the prompt), empty output, refusals, and knowledge-gap language. Optional LLM-as-judge is out of scope for this MVP.</p>
        </details>
        <details>
          <summary>How long to integrate?</summary>
          <p>About 15 minutes with the Python SDK. See Docs → Quick start.</p>
        </details>
      </section>
    </>
  );
}
