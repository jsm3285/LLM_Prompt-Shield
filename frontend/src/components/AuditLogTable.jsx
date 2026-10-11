import React, { useState } from 'react';
import SecurityReportModal from './SecurityReportModal';
import { FileText } from 'lucide-react';

export default function AuditLogTable({ logs, onRefresh }) {
  const [selectedLog, setSelectedLog] = useState(null);

  return (
    <section className="card-panel">
      <div className="panel-title">
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <span>📜 실시간 보안 감사 로그 스트림</span>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)', fontWeight: 400 }}>
            (행을 클릭하거나 '리포트'를 누르면 상세 침해 분석서가 팝업됩니다)
          </span>
        </div>
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
              <th>공격/질의 프롬프트 요약</th>
              <th>위협 유형</th>
              <th>신뢰도</th>
              <th>지연시간</th>
              <th>조치 결과</th>
              <th>포렌식 리포트</th>
            </tr>
          </thead>
          <tbody>
            {!logs || logs.length === 0 ? (
              <tr>
                <td colSpan="9" style={{ textAlign: 'center', color: 'var(--text-dim)', padding: '2rem' }}>
                  기록된 감사 로그가 없습니다. LLM으로 공격 또는 질의를 보내면 실시간 로그가 기록됩니다.
                </td>
              </tr>
            ) : (
              logs.map((log) => {
                const catClass = (log.threat_category || 'none').toLowerCase().replace('_', '');
                const latColor = log.latency_ms <= 25 ? 'var(--accent-green)' : 'var(--accent-yellow)';

                return (
                  <tr
                    key={log.id}
                    onClick={() => setSelectedLog(log)}
                    style={{ cursor: 'pointer', transition: 'background 0.15s ease' }}
                    title="클릭하여 상세 보안 침해 리포트 확인"
                  >
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
                    <td>
                      <button
                        className="chip-btn"
                        onClick={(e) => {
                          e.stopPropagation();
                          setSelectedLog(log);
                        }}
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          gap: '0.3rem',
                          fontSize: '0.72rem',
                          padding: '0.25rem 0.6rem',
                          color: log.is_blocked ? 'var(--accent-cyan)' : 'var(--text-muted)',
                          borderColor: log.is_blocked ? 'var(--border-accent)' : 'var(--border-glass)'
                        }}
                      >
                        <FileText size={12} />
                        <span>리포트 보기</span>
                      </button>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>

      {/* Security Incident Report Modal Popup */}
      {selectedLog && (
        <SecurityReportModal log={selectedLog} onClose={() => setSelectedLog(null)} />
      )}
    </section>
  );
}

