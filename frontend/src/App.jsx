import React from "react";
import { useEffect, useState } from "react";
import "./style.css";

const API = "https://konai-backend.onrender.com";

export default function App() {
  const [dashboard, setDashboard] = useState(null);
  const [components, setComponents] = useState([]);
  const [anomalies, setAnomalies] = useState([]);
  const [maintenance, setMaintenance] = useState([]);
  const [twin, setTwin] = useState([]);
  const [rul, setRul] = useState([]);
  const [loading, setLoading] = useState(true);
  const [errors, setErrors] = useState([]);

  useEffect(() => {
    async function loadData() {
      const endpoints = [
        ["dashboard", "/api/dashboard"],
        ["components", "/api/components"],
        ["anomalies", "/api/anomalies"],
        ["maintenance", "/api/maintenance"],
        ["twin", "/api/digital-twin"],
        ["rul", "/api/rul"],
      ];

      const results = await Promise.all(
        endpoints.map(async ([name, path]) => {
          try {
            const response = await fetch(`${API}${path}`);
            if (!response.ok) throw new Error(`${name}: HTTP ${response.status}`);
            return [name, await response.json(), null];
          } catch (error) {
            return [name, null, error.message];
          }
        })
      );

      const data = {};
      const failed = [];

      results.forEach(([name, value, error]) => {
        if (value) data[name] = value;
        if (error) failed.push(error);
      });

      setDashboard(data.dashboard || null);
      setComponents(data.components?.components || []);
      setAnomalies(data.anomalies?.anomalies || []);
      setMaintenance(data.maintenance?.recommendations || []);
      setTwin(data.twin?.components || []);
      setRul(data.rul?.components || []);
      setErrors(failed);
      setLoading(false);
    }

    loadData();
  }, []);

  const stats = [
    {
      label: "Components Monitored",
      value: dashboard?.total_components ?? components.length,
      icon: "◈",
    },
    {
      label: "Anomalies Detected",
      value: dashboard?.anomaly_records ?? "—",
      icon: "⚠",
    },
    {
      label: "Maintenance Records",
      value: maintenance.length || "—",
      icon: "⚙",
    },
    {
      label: "Digital Twin Components",
      value: twin.length || "—",
      icon: "◇",
    },
  ];

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="brand">KON<span>AI</span></div>
        <p className="side-caption">ELEVATOR INTELLIGENCE</p>

        <nav>
          <a className="active" href="#overview">▦ Dashboard</a>
          <a href="#components">◈ Components</a>
          <a href="#anomalies">⚠ Anomalies</a>
          <a href="#maintenance">⚙ Maintenance</a>
          <a href="#twin">◇ Digital Twin</a>
          <a href="#rul">◷ RUL Assessment</a>
        </nav>

        <div className="sidebar-bottom">
          <span className="status-dot"></span>
          Simulation Environment
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div>
            <h1>Equipment Intelligence</h1>
            <p>Elevator condition monitoring and maintenance platform</p>
          </div>
          <div className="top-status">
            <span className="status-dot"></span>
            Prototype Mode
          </div>
        </header>

        <section id="overview">
          <div className="section-heading">
            <div>
              <h2>System Overview</h2>
              <p>Real-time view of available prototype reports</p>
            </div>
            <span className="data-badge">SYNTHETIC / PUBLIC DATA</span>
          </div>

          {loading ? (
            <p className="loading">Loading dashboard data...</p>
          ) : (
            <div className="stats-grid">
              {stats.map((item) => (
                <div className="stat-card" key={item.label}>
                  <div className="stat-icon">{item.icon}</div>
                  <p>{item.label}</p>
                  <h2>{item.value}</h2>
                </div>
              ))}
            </div>
          )}
        </section>

        {errors.length > 0 && (
          <div className="error-box">
            <strong>Some API reports are currently unavailable.</strong>
            <p>{errors.join(" | ")}</p>
            Other dashboard sections can still be viewed.
          </div>
        )}

        <section id="components" className="panel">
          <div className="section-heading">
            <div>
              <h2>Component Health</h2>
              <p>Health assessment across elevator components</p>
            </div>
          </div>

          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Component</th>
                  <th>Average Health</th>
                  <th>Healthy</th>
                  <th>Warning</th>
                  <th>Critical</th>
                </tr>
              </thead>
              <tbody>
                {components.map((item, index) => (
                  <tr key={index}>
                    <td>{item.component_type}</td>
                    <td>{item.average_health}</td>
                    <td>{item.healthy}</td>
                    <td>{item.warning}</td>
                    <td>{item.critical}</td>
                  </tr>
                ))}
                {components.length === 0 && (
                  <tr><td colSpan="5">No component data available.</td></tr>
                )}
              </tbody>
            </table>
          </div>
        </section>

        <section id="anomalies" className="panel">
          <div className="section-heading">
            <div>
              <h2>Anomaly Detection</h2>
              <p>Unusual sensor behaviour identified by the detection module</p>
            </div>
            <span className="count-badge">{dashboard?.anomaly_records ?? anomalies.length} detected</span>
          </div>

          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Component</th>
                  <th>Anomaly Status</th>
                  <th>Anomaly Score</th>
                  <th>Reason</th>
                </tr>
              </thead>
              <tbody>
                {anomalies.slice(0, 10).map((item, index) => (
                  <tr key={index}>
                    <td>{item.component_type}</td>
                    <td><span className="badge warning">{item.anomaly_status}</span></td>
                    <td>{item.anomaly_score ?? "—"}</td>
                    <td>{item.anomaly_reason ?? "—"}</td>
                  </tr>
                ))}
                {anomalies.length === 0 && (
                  <tr><td colSpan="4">Anomaly report unavailable.</td></tr>
                )}
              </tbody>
            </table>
          </div>
        </section>

        <section id="maintenance" className="panel">
          <div className="section-heading">
            <div>
              <h2>Maintenance Recommendations</h2>
              <p>Rule-based maintenance priorities and suggested actions</p>
            </div>
          </div>

          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Component</th>
                  <th>Priority</th>
                  <th>Recommended Action</th>
                  <th>Review Required</th>
                </tr>
              </thead>
              <tbody>
                {maintenance.slice(0, 10).map((item, index) => (
                  <tr key={index}>
                    <td>{item.component_type}</td>
                    <td>
                      <span className="badge">{item.maintenance_priority ?? "—"}</span>
                    </td>
                    <td>{item.maintenance_action ?? "—"}</td>
                    <td>{item.review_required ?? "—"}</td>
                  </tr>
                ))}
                {maintenance.length === 0 && (
                  <tr><td colSpan="4">Maintenance report unavailable.</td></tr>
                )}
              </tbody>
            </table>
          </div>
        </section>

        <section id="twin" className="panel">
          <div className="section-heading">
            <div>
              <h2>Digital Twin</h2>
              <p>Simulation-based component state representation</p>
            </div>
            <span className="data-badge">SIMULATION</span>
          </div>

          <div className="twin-grid">
            {twin.map((item, index) => (
              <div className="twin-card" key={index}>
                <h3>{item.component_type}</h3>
                <p>Component ID: {item.component_id ?? "—"}</p>
                <p>Status: <strong>{item.twin_status ?? "—"}</strong></p>
                <p>Health: {item.health_score ?? "—"}</p>
              </div>
            ))}
            {twin.length === 0 && <p>Digital twin data unavailable.</p>}
          </div>
        </section>

        <section id="rul" className="panel">
          <div className="section-heading">
            <div>
              <h2>Remaining Useful Life Assessment</h2>
              <p>Data feasibility assessment for future RUL prediction</p>
            </div>
          </div>

          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Component</th>
                  <th>RUL Status</th>
                  <th>Prediction</th>
                  <th>Confidence</th>
                </tr>
              </thead>
              <tbody>
                {rul.map((item, index) => (
                  <tr key={index}>
                    <td>{item.component_type}</td>
                    <td>{item.rul_status}</td>
                    <td>{item.rul_prediction ?? "Not available"}</td>
                    <td>{item.prediction_confidence ?? "Not available"}</td>
                  </tr>
                ))}
                {rul.length === 0 && (
                  <tr><td colSpan="4">RUL assessment unavailable.</td></tr>
                )}
              </tbody>
            </table>
          </div>
          <p className="note">
            Numerical RUL predictions are not available because verified run-to-failure data
            is currently insufficient.
          </p>
        </section>

        <footer>
          KonAI · Elevator Intelligence Platform · Prototype for decision support only.
          Not connected to elevator safety or control systems.
        </footer>
      </main>
    </div>
  );
}