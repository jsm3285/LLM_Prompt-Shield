import React from 'react';

export default function MetricsGrid({ metrics }) {
  const total = metrics?.total_requests || 0;
  const blockRate = metrics?.block_rate_percent || 0;
  const blockedCount = metrics?.blocked_requests || 0;
  const p95 = metrics?.p95_latency_ms || 0;
  const avg = metrics?.avg_latency_ms || 0;

  return (
    <section className="metrics-grid">
      <div className="metric-card">
        <div className="metric-title">총 요청 수</div>
        <div className="metric-value metric-val-cyan">{total.toLocaleString()}</div>
        <div className="metric-subtitle">프록시 처리 완료</div>
      </div>
      <div className="metric-card">
        <div className="metric-title">위협 차단율</div>
        <div className="metric-value metric-val-red">{blockRate.toFixed(1)}%</div>
        <div className="metric-subtitle">{blockedCount}건 차단 (403)</div>
      </div>
      <div className="metric-card">
        <div className="metric-title">P95 지연시간 (SLA &lt; 25ms)</div>
        <div className="metric-value metric-val-green">{p95.toFixed(1)} ms</div>
        <div className="metric-subtitle">평균: {avg.toFixed(1)} ms</div>
      </div>
      <div className="metric-card">
        <div className="metric-title">색인된 벡터 시드</div>
        <div className="metric-value metric-val-purple">8</div>
        <div className="metric-subtitle">FAISS / 인메모리 저장소</div>
      </div>
    </section>
  );
}
