import { NavLink, Outlet } from "react-router-dom";

const links = [
  ["Overview", "/app"],
  ["Events", "/app/events"],
  ["Drift", "/app/drift"],
  ["Failures", "/app/failures"],
  ["Compare", "/app/compare"],
  ["Reports", "/app/reports"],
];

export default function AppShell() {
  return (
    <div className="app-shell">
      <aside className="side">
        <NavLink to="/" className="brand" style={{ marginBottom: 18 }}>
          <strong>audit-ai</strong>
        </NavLink>
        {links.map(([label, to]) => (
          <NavLink key={to} to={to} end={to === "/app"}>
            {label}
          </NavLink>
        ))}
        <NavLink to="/" style={{ marginTop: 24 }}>
          ← Marketing site
        </NavLink>
      </aside>
      <div className="main">
        <Outlet />
      </div>
    </div>
  );
}
