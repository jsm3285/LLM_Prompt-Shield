import React from 'react';

export default function AuditLogTable({ logs, onRefresh }) {
  return (
    <section className="card-panel">
      <div className="panel-title">
        <span>📜 실시간 보안 감사 로그 스트림</span>
        <button
          className="btn btn-secondary"
          onClick={onRefresh}
          style={{ padding: '0.3rem 0.8rem', fontSize: '0.75rem' }}
        >
          새로고침
        </button>
      </div>

      <div className="table-wrap">
        <table className="audit-table">
          <thead>
            <tr>
              <th>로그 ID</th>
              <th>타임스탬프</th>
              <th>클라이언트 IP</th>
              <th>프롬프트 요약</th>
              <th>위협 유형</th>
              <th>신뢰도</th>
              <th>지연시간</th>
              <th>조치 결과</th>
            </tr>
          </thead>
          <tbody>
            {!logs || logs.length === 0 ? (
              <tr>
                <td colSpan="8" style={{ textAlign: 'center', color: 'var(--text-dim)', padding: '2rem' }}>
                  기록된 감사 로그가 없습니다. 프록시로 요청을 보내거나 플레이그라운드 검사를 실행하세요.
                </td>
              </tr>
            ) : (
              logs.map((log) => {
                const catClass = (log.threat_category || 'none').toLowerCase().replace('_', '');
                const latColor = log.latency_ms <= 25 ? 'var(--accent-green)' : 'var(--accent-yellow)';

                return (
                  <tr key={log.id}>
                    <td className="code-snippet">{log.id}</td>
                    <td style={{ color: 'var(--text-muted)' }}>{log.timestamp}</td>
                    <td>{log.client_ip}</td>
                    <td className="code-snippet">{log.prompt_snippet}</td>
                    <td>
                      <span className={`tag-cat tag-${catClass}`}>
                        {log.threat_category || '없음'}
                      </span>
                    </td>
                    <td>
                      {log.confidence_score > 0 ? `${(log.confidence_score * 100).toFixed(0)}%` : '-'}
                    </td>
                    <td style={{ fontWeight: 600, color: latColor }}>
                      {log.latency_ms.toFixed(1)} ms
                    </td>
                    <td>
                      <span className={`verdict-badge ${log.is_blocked ? 'verdict-threat' : 'verdict-safe'}`}>
                        {log.is_blocked ? '차단됨 (403)' : '통과 (200)'}
                      </span>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}
