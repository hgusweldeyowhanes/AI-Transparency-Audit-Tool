import { Route, Routes } from "react-router-dom";
import MarketingLayout from "./components/MarketingLayout";
import AppShell from "./components/AppShell";
import Home from "./pages/Home";
import Pricing from "./pages/Pricing";
import Docs from "./pages/Docs";
import Blog from "./pages/Blog";
import BlogPost from "./pages/BlogPost";
import Resources from "./pages/Resources";
import GetStarted from "./pages/GetStarted";
import Dashboard from "./pages/app/Dashboard";
import EventsPage from "./pages/app/Events";
import EventDetail from "./pages/app/EventDetail";
import DriftPage from "./pages/app/Drift";
import FailuresPage from "./pages/app/Failures";
import ComparePage from "./pages/app/Compare";
import ReportsPage from "./pages/app/Reports";

export default function App() {
  return (
    <Routes>
      <Route element={<MarketingLayout />}>
        <Route path="/" element={<Home />} />
        <Route path="/pricing" element={<Pricing />} />
        <Route path="/docs" element={<Docs />} />
        <Route path="/blog" element={<Blog />} />
        <Route path="/blog/:slug" element={<BlogPost />} />
        <Route path="/resources" element={<Resources />} />
        <Route path="/start" element={<GetStarted />} />
      </Route>
      <Route path="/app" element={<AppShell />}>
        <Route index element={<Dashboard />} />
        <Route path="events" element={<EventsPage />} />
        <Route path="events/:id" element={<EventDetail />} />
        <Route path="drift" element={<DriftPage />} />
        <Route path="failures" element={<FailuresPage />} />
        <Route path="compare" element={<ComparePage />} />
        <Route path="reports" element={<ReportsPage />} />
      </Route>
    </Routes>
  );
}
