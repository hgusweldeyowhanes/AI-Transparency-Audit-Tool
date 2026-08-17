import { useMemo, useState } from "react";
import { Link } from "react-router-dom";

const plans = [
  {
    name: "Free",
    price: "$0",
    cadence: "self-hosted",
    blurb: "Unlimited events. Core search + basic drift. Discord-style community support. 30-day retention.",
    cta: "Clone the repo",
    to: "/docs",
    featured: false,
  },
  {
    name: "Growth",
    price: "$500–$1K",
    cadence: "/ month",
    blurb: "Up to 10M events/month, 1-year retention, Slack/email alerts, standard support.",
    cta: "Start trial",
    to: "/start",
    featured: true,
  },
  {
    name: "Pro",
    price: "$2K–$5K",
    cadence: "/ month",
    blurb: "Up to 100M events, failure clustering, A/B compare, 2-year retention, 4-hour response.",
    cta: "Start trial",
    to: "/start",
    featured: false,
  },
  {
    name: "Enterprise",
    price: "Custom",
    cadence: "",
    blurb: "Data residency, SSO, dedicated onboarding, custom retention, MSA/DPA.",
    cta: "Book a demo",
    to: "/start",
    featured: false,
  },
];

export default function Pricing() {
  const [hours, setHours] = useState(200);
  const [rate, setRate] = useState(150);
  const [plan, setPlan] = useState(9000);
  const roi = useMemo(() => {
    const manual = hours * rate;
    const saved = manual - plan;
    const multiple = plan ? manual / plan : 0;
    return { manual, saved, multiple };
  }, [hours, rate, plan]);

  return (
    <section className="section">
      <div className="kicker">Transparent pricing</div>
      <h1>Not enterprise-only. Not a surprise invoice.</h1>
      <p className="lede">Free to self-host. Managed cloud when you want retention, alerts, and someone else paging.</p>
      <div className="grid-4" style={{ marginTop: 32 }}>
        {plans.map((p) => (
          <article key={p.name} className="card" style={p.featured ? { outline: "1px solid var(--teal)" } : undefined}>
            <div className="kicker">{p.featured ? "Most teams" : " "}</div>
            <h3>{p.name}</h3>
            <div className="price">
              {p.price} <small>{p.cadence}</small>
            </div>
            <p className="muted">{p.blurb}</p>
            <Link className="btn btn-primary" to={p.to}>
              {p.cta}
            </Link>
          </article>
        ))}
      </div>

      <div className="card" style={{ marginTop: 48 }}>
        <h2>ROI calculator</h2>
        <p className="muted">GTM assumption: compliance audits eat 200+ manual hours/year. Adjust the knobs.</p>
        <div className="grid-3" style={{ marginTop: 16 }}>
          <div>
            <label>Manual audit hours / year</label>
            <input type="number" value={hours} onChange={(e) => setHours(Number(e.target.value))} />
          </div>
          <div>
            <label>Fully loaded rate ($/hr)</label>
            <input type="number" value={rate} onChange={(e) => setRate(Number(e.target.value))} />
          </div>
          <div>
            <label>audit-ai annual spend ($)</label>
            <input type="number" value={plan} onChange={(e) => setPlan(Number(e.target.value))} />
          </div>
        </div>
        <div className="metrics" style={{ marginTop: 22 }}>
          <div className="metric card">
            <div className="label">Manual cost</div>
            <div className="value">${roi.manual.toLocaleString()}</div>
          </div>
          <div className="metric card">
            <div className="label">Net vs. audit-ai</div>
            <div className="value">${roi.saved.toLocaleString()}</div>
          </div>
          <div className="metric card">
            <div className="label">Cost multiple</div>
            <div className="value">{roi.multiple.toFixed(1)}x</div>
          </div>
        </div>
      </div>
    </section>
  );
}
