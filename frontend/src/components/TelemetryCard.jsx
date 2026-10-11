import React from 'react';

export default function TelemetryCard({ metrics, engineInfo }) {
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
        <span className="badge-tag">PID-1 코어 엔진</span>
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
        <div style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--accent-cyan)' }}>🧩 활성 보안 엔진 아키텍처 (WBS 3.1.5 & 3.2.1):</div>
        <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
          • <strong>임베딩 엔진:</strong> {engineInfo?.embedding_extractor || 'Lightweight Hash Projection (384-dim)'}
        </div>
        <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
          • <strong>벡터 DB 백엔드:</strong> {engineInfo?.vector_store?.backend || 'In-Memory Cosine Similarity'}
        </div>
        <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
          • <strong>인라인 프록시 게이트웨이:</strong> FastAPI (OpenAI 호환 <code>/v1/chat/completions</code>)
        </div>
      </div>
    </div>
  );
}
