import React from 'react';

export default function Header({ activeTab, setActiveTab }) {
  return (
    <header className="dashboard-header">
      <div className="brand">
        <div className="shield-icon">🛡️</div>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <h1 className="brand-title">Prompt Shield</h1>
            <span className="brand-tag">PID-1 코어 엔진</span>
          </div>
          <p style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>
            P95 &lt; 25ms 초저지연 LLM 인라인 보안 게이트웨이
          </p>
        </div>
      </div>

      {/* Main Page Navigation Tabs */}
      <nav style={{ display: 'flex', gap: '0.6rem', background: 'rgba(0,0,0,0.25)', padding: '0.3rem', borderRadius: '12px', border: '1px solid var(--border-glass)' }}>
        <button
          onClick={() => setActiveTab('llm')}
          style={{
            padding: '0.55rem 1.25rem',
            fontSize: '0.88rem',
            fontWeight: 600,
            borderRadius: '8px',
            border: activeTab === 'llm' ? '1px solid var(--accent-cyan)' : '1px solid transparent',
            background: activeTab === 'llm' ? 'rgba(56, 189, 248, 0.15)' : 'transparent',
            color: activeTab === 'llm' ? 'var(--accent-cyan)' : 'var(--text-muted)',
            cursor: 'pointer',
            transition: 'all 0.2s ease',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem'
          }}
        >
          <span>🤖</span>
          <span>LLM 보안 테스트 & A/B 시연</span>
        </button>

        <button
          onClick={() => setActiveTab('dashboard')}
          style={{
            padding: '0.55rem 1.25rem',
            fontSize: '0.88rem',
            fontWeight: 600,
            borderRadius: '8px',
            border: activeTab === 'dashboard' ? '1px solid var(--accent-purple)' : '1px solid transparent',
            background: activeTab === 'dashboard' ? 'rgba(168, 85, 247, 0.15)' : 'transparent',
            color: activeTab === 'dashboard' ? 'var(--accent-purple)' : 'var(--text-muted)',
            cursor: 'pointer',
            transition: 'all 0.2s ease',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem'
          }}
        >
          <span>📊</span>
          <span>통합 보안 관제 대시보드</span>
        </button>
      </nav>

      {/* Status & Model Badges */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.8rem' }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '0.4rem',
          fontSize: '0.75rem',
          padding: '0.35rem 0.75rem',
          background: 'rgba(168, 85, 247, 0.1)',
          border: '1px solid rgba(168, 85, 247, 0.25)',
          borderRadius: '20px',
          color: 'var(--accent-purple)'
        }}>
          <span>🎯 대상 LLM:</span>
          <strong style={{ color: '#fff' }}>llama3.2:1B</strong>
        </div>

        <div className="status-badge" id="gateway-status">
          <div className="pulse-dot"></div>
          <span>게이트웨이 활성화</span>
        </div>
      </div>
    </header>
  );
}

