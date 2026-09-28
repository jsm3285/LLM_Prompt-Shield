import React from 'react';

export default function Header() {
  return (
    <header className="dashboard-header">
      <div className="brand">
        <div className="shield-icon">🛡️</div>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <h1 className="brand-title">Prompt Shield</h1>
            <span className="brand-tag">React + FastAPI</span>
          </div>
          <p style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>
            P95 &lt; 25ms 초저지연 LLM 인라인 보안 게이트웨이
          </p>
        </div>
      </div>
      <div className="status-badge" id="gateway-status">
        <div className="pulse-dot"></div>
        <span>게이트웨이 활성화 (FastAPI 프록시)</span>
      </div>
    </header>
  );
}
