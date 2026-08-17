import { Link } from "react-router-dom";

export default function Resources() {
  return (
    <section className="section">
      <div className="kicker">Resources</div>
      <h1>Checklists, playbooks, comparisons</h1>

      <div className="grid-2" style={{ marginTop: 28 }}>
        <article className="card">
          <h3>Regulatory compliance checklist</h3>
          <ul className="feature-list">
            <li>Inventory every production model and prompt version</li>
            <li>Log prompt, completion, timestamps, actor, cost</li>
            <li>Define retention (30 / 365 / 730 days)</li>
            <li>Detect empty, refusal, ungrounded citation, PII-like output</li>
            <li>Produce a quarterly pack for legal (EU AI Act / SEC templates)</li>
            <li>Name a human reviewer for incidents</li>
          </ul>
        </article>
        <article className="card">
          <h3>LLM audit trail best practices</h3>
          <ul className="feature-list">
            <li>Put <strong>prompt_version</strong> on every event</li>
            <li>Tag by use case, not by team Slack channel</li>
            <li>Never log secrets; hash user ids if you must</li>
            <li>Compare models on your traffic, not a leaderboard</li>
            <li>Treat drift as a change-control problem</li>
          </ul>
        </article>
      </div>

      <article className="card" style={{ marginTop: 22 }}>
        <h3>Us vs. the monitoring incumbents</h3>
        <table className="data">
          <thead>
            <tr>
              <th>Company</th>
              <th>Strength</th>
              <th>Gap</th>
              <th>Price</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Arize AI</td>
              <td>ML monitoring depth</td>
              <td>Not LLM-native</td>
              <td>$50K+/yr</td>
            </tr>
            <tr>
              <td>Arthur AI</td>
              <td>Governance</td>
              <td>Enterprise-only</td>
              <td>Custom</td>
            </tr>
            <tr>
              <td>Fiddler AI</td>
              <td>Enterprise features</td>
              <td>Price, not LLM-first</td>
              <td>$100K+/yr</td>
            </tr>
            <tr>
              <td>Datadog LLM</td>
              <td>Installed base</td>
              <td>Shallow, not compliance-first</td>
              <td>$50K+/yr</td>
            </tr>
            <tr>
              <td>
                <strong>audit-ai</strong>
              </td>
              <td>LLM-native, open source, compliance-first</td>
              <td>Emerging brand</td>
              <td>$5K–$20K/yr typical</td>
            </tr>
          </tbody>
        </table>
        <p className="muted">
          Messaging: Arize is for ML monitoring. We are for LLM compliance. Fiddler is enterprise-only. We are
          developer-first. Datadog monitors everything. We specialize in governance.
        </p>
      </article>

      <article className="card" style={{ marginTop: 22 }}>
        <h3>Case study — how Northwind Support caught a $500K bug</h3>
        <p>
          <strong>Challenge.</strong> Northwind deployed Claude for customer-support summarization. Quality slipped;
          nobody could say why. Manual debugging ate 100+ hours/month.
        </p>
        <p>
          <strong>Solution.</strong> audit-ai in two days. Detectors flagged a 3.2-point rise in ungrounded citations,
          clustered on prompt version v2 (“too aggressive”).
        </p>
        <p>
          <strong>Results.</strong> Root cause in two hours. Rollback. 24/7 quality watch. Debugging time down ~95%.
        </p>
        <p>
          Replay it on the seeded demo: <Link to="/app/drift">Drift incident</Link>.
        </p>
      </article>
    </section>
  );
}
