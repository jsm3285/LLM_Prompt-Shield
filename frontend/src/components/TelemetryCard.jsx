import React from 'react';

export default function TelemetryCard({ metrics }) {
  const breakdown = metrics?.threat_category_breakdown || {};
  const totalBlocked = metrics?.blocked_requests || 1;

  const jailbreakCount = breakdown.jailbreak || 0;
  const injectionCount = breakdown.prompt_injection || 0;
  const exfiltrationCount = breakdown.data_exfiltration || 0;

  const getPct = (cnt) => (totalBlocked > 0 ? Math.min((cnt / totalBlocked) * 100, 100) : 0);

  return (
    <div className="card-panel">
      <div className="panel-title">
        <span>📊 위협 유형별 실시간 측정</span>
        <span className="badge-tag">FastAPI + React</span>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', marginBottom: '0.3rem' }}>
            <span>탈옥 (DAN / 페르소나 이탈)</span>
            <span>{jailbreakCount}</span>
          </div>
          <div style={{ width: '100%', height: '8px', background: 'rgba(255,255,255,0.05)', borderRadius: '4px', overflow: 'hidden' }}>
            <div style={{ width: `${getPct(jailbreakCount)}%`, height: '100%', background: 'var(--accent-red)', transition: 'width 0.3s ease' }} />
          </div>
        </div>

        <div>
          <div style={{ display: 'flex', justify: 'space-between', fontSize: '0.85rem', marginBottom: '0.3rem' }}>
            <span>Prompt Injection (System Hijack)</span>
            <span>{injectionCount}</span>
          </div>
          <div style={{ width: '100%', height: '8px', background: 'rgba(255,255,255,0.05)', borderRadius: '4px', overflow: 'hidden' }}>
            <div style={{ width: `${getPct(injectionCount)}%`, height: '100%', background: 'var(--accent-yellow)', transition: 'width 0.3s ease' }} />
          </div>
        </div>

        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', marginBottom: '0.3rem' }}>
            <span>정보 유출 (비밀키 / 프롬프트 탈취)</span>
            <span>{exfiltrationCount}</span>
          </div>
          <div style={{ width: '100%', height: '8px', background: 'rgba(255,255,255,0.05)', borderRadius: '4px', overflow: 'hidden' }}>
            <div style={{ width: `${getPct(exfiltrationCount)}%`, height: '100%', background: 'var(--accent-purple)', transition: 'width 0.3s ease' }} />
          </div>
        </div>
      </div>

      <div style={{ marginTop: '1rem', paddingTop: '1rem', borderTop: '1px solid var(--border-glass)', display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
        <div style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--accent-cyan)' }}>🧩 시스템 아키텍처:</div>
        <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
          • <strong>FastAPI 프록시 백엔드:</strong> 인라인 프록시 파이프라인 (<code>backend/gateway/routes.py</code>)
        </div>
        <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
          • <strong>AI 벡터 저장소:</strong> 25ms 미만 인메모리 코사인 검색 (<code>backend/engine/</code>)
        </div>
        <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
          • <strong>React SPA 프론트엔드:</strong> Vite 관제 UI (<code>frontend/src/</code>)
        </div>
      </div>
    </div>
  );
}
