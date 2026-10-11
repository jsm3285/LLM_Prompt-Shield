import React from 'react';
import MetricsGrid from '../components/MetricsGrid';
import Playground from '../components/Playground';
import TelemetryCard from '../components/TelemetryCard';
import AuditLogTable from '../components/AuditLogTable';

export default function DashboardPage({ metrics, logs, engineInfo, onRefresh }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* Overview Metrics Cards */}
      <MetricsGrid metrics={metrics} />

      {/* Security Engine Inspector & Threat Telemetry */}
      <section className="grid-two-col">
        <Playground onInspectComplete={onRefresh} />
        <TelemetryCard metrics={metrics} engineInfo={engineInfo} />
      </section>

      {/* Real-time Audit Log Stream Table */}
      <section>
        <AuditLogTable logs={logs} onRefresh={onRefresh} />
      </section>
    </div>
  );
}
