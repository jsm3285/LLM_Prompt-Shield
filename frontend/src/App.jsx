import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import MetricsGrid from './components/MetricsGrid';
import Playground from './components/Playground';
import TelemetryCard from './components/TelemetryCard';
import AuditLogTable from './components/AuditLogTable';
import Chatbot from './components/Chatbot';

export default function App() {
  const [activeTab, setActiveTab] = useState('chatbot'); // 'chatbot' | 'dashboard'
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

        {/* Tab Navigation */}
        <div style={{ display: 'flex', gap: '0.8rem', marginBottom: '1.2rem' }}>
          <button
            className={`btn ${activeTab === 'chatbot' ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => setActiveTab('chatbot')}
            style={{ padding: '0.6rem 1.2rem', fontSize: '0.9rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}
          >
            💬 실시간 AI 챗봇 모드
          </button>
          <button
            className={`btn ${activeTab === 'dashboard' ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => setActiveTab('dashboard')}
            style={{ padding: '0.6rem 1.2rem', fontSize: '0.9rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}
          >
            📊 관제 대시보드 & 보안 플레이그라운드
          </button>
        </div>

        <MetricsGrid metrics={metrics} />

        {activeTab === 'chatbot' ? (
          <section style={{ marginTop: '1rem' }}>
            <Chatbot />
          </section>
        ) : (
          <section className="grid-two-col">
            <Playground onInspectComplete={handleRefresh} />
            <TelemetryCard metrics={metrics} />
          </section>
        )}

        <div style={{ marginTop: '1.5rem' }}>
          <AuditLogTable logs={logs} onRefresh={handleRefresh} />
        </div>
      </main>
    </div>
  );
}
