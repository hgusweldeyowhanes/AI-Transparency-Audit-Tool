import { Link } from "react-router-dom";
import { api } from "../../api";
import { PageState } from "../../components/Ui";
import { useApi } from "../../hooks/useApi";

export default function FailuresPage() {
  const { data, error, loading } = useApi(() => api.failures(), []);

  return (
    <div>
      <h1>Failures</h1>
      <PageState error={error} loading={loading} loadingText="Clustering…">
        {data && (
          <>
            <p className="muted">
              Scanned {data.scanned} events · {data.failed_events} with at least one flag
            </p>
            <div className="grid-2">
              {data.taxonomy.map((item) => (
                <div key={item.flag} className="card">
                  <div className="kicker">{item.flag}</div>
                  <h3>{item.label}</h3>
                  <div className="value" style={{ fontFamily: "var(--serif)", fontSize: 28 }}>
                    {item.count}
                  </div>
                </div>
              ))}
            </div>
            <h2 style={{ marginTop: 32 }}>Clusters</h2>
            <table className="data">
              <thead>
                <tr>
                  <th>Flag</th>
                  <th>Count</th>
                  <th>Sample</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {data.clusters.map((cluster, i) => (
                  <tr key={i}>
                    <td>
                      <span className="flag">{cluster.flag}</span>
                    </td>
                    <td>{cluster.count}</td>
                    <td>{cluster.sample}</td>
                    <td>
                      {cluster.event_ids[0] ? <Link to={`/app/events/${cluster.event_ids[0]}`}>Example</Link> : null}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </>
        )}
      </PageState>
    </div>
  );
}
