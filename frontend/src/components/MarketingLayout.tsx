import { NavLink, Outlet } from "react-router-dom";

export default function MarketingLayout() {
  return (
    <div>
      <header className="site-header">
        <NavLink to="/" className="brand">
          <strong>audit-ai</strong>
          <span>ledger for LLMs</span>
        </NavLink>
        <nav className="nav">
          <NavLink to="/pricing">Pricing</NavLink>
          <NavLink to="/docs">Docs</NavLink>
          <NavLink to="/blog">Blog</NavLink>
          <NavLink to="/resources">Resources</NavLink>
          <NavLink to="/app">Dashboard</NavLink>
          <NavLink to="/start" className="btn btn-primary">
            Get started free
          </NavLink>
        </nav>
      </header>
      <Outlet />
      <footer className="site-footer">
        <div>© {new Date().getFullYear()} audit-ai · open source · not legal advice</div>
        <div>EU AI Act templates · SEC evidence packs · self-hosted first</div>
      </footer>
    </div>
  );
}
