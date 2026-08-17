import { Link } from "react-router-dom";
import { posts } from "../content/posts";

export default function Blog() {
  return (
    <section className="section">
      <div className="kicker">Journal</div>
      <h1>Regulatory news, tutorials, case studies</h1>
      <div className="grid-2" style={{ marginTop: 28 }}>
        {posts.map((p) => (
          <article key={p.slug} className="card">
            <div className="kicker">
              {p.kicker} · {p.date}
            </div>
            <h3>
              <Link to={`/blog/${p.slug}`}>{p.title}</Link>
            </h3>
            <p className="muted">{p.excerpt}</p>
          </article>
        ))}
      </div>
    </section>
  );
}
