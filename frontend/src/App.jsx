import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import LlmTestPage from './pages/LlmTestPage';
import DashboardPage from './pages/DashboardPage';

export default function App() {
  const [activeTab, setActiveTab] = useState('llm'); // 'llm' | 'dashboard'
  const [metrics, setMetrics] = useState(null);
  const [logs, setLogs] = useState([]);
  const [engineInfo, setEngineInfo] = useState(null);

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

  const fetchEngineInfo = async () => {
    try {
      const resp = await fetch('/api/v1/shield/info');
      if (resp.ok) {
        const data = await resp.json();
        setEngineInfo(data.engine);
      }
    } catch (err) {
      console.warn('Engine info fetch error:', err);
    }
  };

  const handleRefresh = () => {
    fetchMetrics();
    fetchLogs();
    fetchEngineInfo();
  };

  useEffect(() => {
    fetchMetrics();
    fetchLogs();
    fetchEngineInfo();

    const interval = setInterval(() => {
      fetchMetrics();
      fetchLogs();
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div>
      <Header activeTab={activeTab} setActiveTab={setActiveTab} />
      <main className="main-container">
        {activeTab === 'llm' ? (
          <LlmTestPage />
        ) : (
          <DashboardPage
            metrics={metrics}
            logs={logs}
            engineInfo={engineInfo}
            onRefresh={handleRefresh}
          />
        )}
      </main>
    </div>
  );
}


