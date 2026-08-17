import { Link, useParams } from "react-router-dom";
import { posts } from "../content/posts";

export default function BlogPost() {
  const { slug } = useParams();
  const post = posts.find((p) => p.slug === slug);
  if (!post) {
    return (
      <section className="section">
        <p>Post not found. <Link to="/blog">Back</Link></p>
      </section>
    );
  }
  return (
    <section className="section prose">
      <div className="kicker">
        {post.kicker} · {post.date}
      </div>
      <h1>{post.title}</h1>
      {post.body.map((para) => (
        <p key={para.slice(0, 24)}>{para}</p>
      ))}
      <p className="muted">Keywords: {post.keywords.join(", ")}</p>
      <p>
        <Link to="/blog">← All posts</Link>
      </p>
    </section>
  );
}
