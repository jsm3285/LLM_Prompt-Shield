import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import MetricsGrid from './components/MetricsGrid';
import Playground from './components/Playground';
import TelemetryCard from './components/TelemetryCard';
import AuditLogTable from './components/AuditLogTable';

export default function App() {
  const [metrics, setMetrics] = useState(null);
  const [logs, setLogs] = useState([]);

  const fetchMetrics = async () => {
    try {
      const resp = await fetch('/api/v1/shield/metrics');
      if (resp.ok) {
        const data = await resp.json();
        setMetrics(data);
      }
    } catch (err) {
      console.warn('Metrics fetch error:', err);
    }
  };

  const fetchLogs = async () => {
    try {
      const resp = await fetch('/api/v1/shield/logs?limit=20');
      if (resp.ok) {
        const data = await resp.json();
        setLogs(data);
      }
    } catch (err) {
      console.warn('Logs fetch error:', err);
    }
  };

  const handleRefresh = () => {
    fetchMetrics();
    fetchLogs();
  };

  useEffect(() => {
    fetchMetrics();
    fetchLogs();

    const interval = setInterval(() => {
      fetchMetrics();
      fetchLogs();
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div>
      <Header />
      <main className="main-container">
        <MetricsGrid metrics={metrics} />

        <section className="grid-two-col">
          <Playground onInspectComplete={handleRefresh} />
          <TelemetryCard metrics={metrics} />
        </section>

        <AuditLogTable logs={logs} onRefresh={handleRefresh} />
      </main>
    </div>
  );
}
