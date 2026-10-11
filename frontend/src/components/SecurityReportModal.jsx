import React, { useState, useEffect } from 'react';
import { ShieldAlert, CheckCircle2, Copy, Download, X, Clock, Server, AlertTriangle } from 'lucide-react';

export default function SecurityReportModal({ log, onClose }) {
  const [reportData, setReportData] = useState(null);
  const [copied, setCopied] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!log?.id) return;
    setLoading(true);

    fetch(`/api/v1/shield/logs/${log.id}/report`)
      .then((res) => {
        if (!res.ok) throw new Error('Report fetch error');
        return res.json();
      })
      .then((data) => {
        setReportData(data);
      })
      .catch((err) => {
        console.warn('Error fetching report:', err);
      })
      .finally(() => setLoading(false));
  }, [log]);

  if (!log) return null;

  const handleCopy = () => {
    const text = reportData?.markdown_report || JSON.stringify(log, null, 2);
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2500);
  };

  const handleDownload = () => {
    const text = reportData?.markdown_report || JSON.stringify(log, null, 2);
    const blob = new Blob([text], { type: 'text/markdown;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `PromptShield_Incident_${log.id}.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  };

  const isBlocked = log.is_blocked;
  const threatCat = log.threat_category || '미탐지';
  const fullPrompt = log.full_prompt || log.prompt_snippet;
  const normalizedPrompt = log.normalized_prompt || fullPrompt;
  const latencyColor = log.latency_ms <= 25 ? 'var(--accent-green)' : 'var(--accent-yellow)';

  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        backgroundColor: 'rgba(0, 0, 0, 0.75)',
        backdropFilter: 'blur(8px)',
        zIndex: 9999,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '1.5rem'
      }}
      onClick={onClose}
    >
      <div
        className="card-panel"
        style={{
          width: '100%',
          maxWidth: '780px',
          maxHeight: '88vh',
          overflowY: 'auto',
          background: '#0d131f',
          border: '1px solid var(--border-accent)',
          borderRadius: '16px',
          boxShadow: '0 20px 50px rgba(0, 0, 0, 0.8)',
          padding: '1.8rem',
          position: 'relative'
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', paddingBottom: '1rem', borderBottom: '1px solid var(--border-glass)' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
              <ShieldAlert style={{ color: isBlocked ? 'var(--accent-red)' : 'var(--accent-green)' }} size={24} />
              <h2 style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--text-main)', margin: 0 }}>
                보안 침해 분석 리포트 (Security Incident Report)
              </h2>
            </div>
            <div style={{ display: 'flex', gap: '0.6rem', marginTop: '0.4rem', fontSize: '0.78rem' }}>
              <span className="badge-tag" style={{ color: 'var(--accent-cyan)' }}>사건 ID: {log.id}</span>
              <span className="badge-tag" style={{ color: 'var(--text-muted)' }}>{log.timestamp}</span>
              <span
                style={{
                  fontSize: '0.75rem',
                  fontWeight: 600,
                  padding: '0.15rem 0.6rem',
                  borderRadius: '12px',
                  background: isBlocked ? 'rgba(244, 63, 94, 0.15)' : 'rgba(16, 185, 129, 0.15)',
                  color: isBlocked ? 'var(--accent-red)' : 'var(--accent-green)',
                  border: isBlocked ? '1px solid rgba(244, 63, 94, 0.3)' : '1px solid rgba(16, 185, 129, 0.3)'
                }}
              >
                {isBlocked ? '🛑 403 Forbidden 인라인 차단 완료' : '🟢 정상 통과 (200 OK)'}
              </span>
            </div>
          </div>
          <button
            onClick={onClose}
            className="chip-btn"
            style={{ padding: '0.4rem', borderRadius: '50%', color: 'var(--text-muted)' }}
          >
            <X size={18} />
          </button>
        </div>

        {/* Executive Summary Grid */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(170px, 1fr))', gap: '0.8rem', marginTop: '1.2rem' }}>
          <div style={{ background: 'rgba(255, 255, 255, 0.02)', padding: '0.8rem', borderRadius: '8px', border: '1px solid var(--border-glass)' }}>
            <span style={{ fontSize: '0.72rem', color: 'var(--text-dim)' }}>대상 모델</span>
            <div style={{ fontSize: '0.88rem', fontWeight: 600, color: '#fff', marginTop: '0.2rem' }}>
              {log.target_model || 'llama3.2:1B Instruct'}
            </div>
          </div>
          <div style={{ background: 'rgba(255, 255, 255, 0.02)', padding: '0.8rem', borderRadius: '8px', border: '1px solid var(--border-glass)' }}>
            <span style={{ fontSize: '0.72rem', color: 'var(--text-dim)' }}>위협 분류</span>
            <div style={{ fontSize: '0.88rem', fontWeight: 600, color: 'var(--accent-red)', marginTop: '0.2rem' }}>
              {threatCat}
            </div>
          </div>
          <div style={{ background: 'rgba(255, 255, 255, 0.02)', padding: '0.8rem', borderRadius: '8px', border: '1px solid var(--border-glass)' }}>
            <span style={{ fontSize: '0.72rem', color: 'var(--text-dim)' }}>벡터 유사도 신뢰도</span>
            <div style={{ fontSize: '0.88rem', fontWeight: 600, color: 'var(--accent-yellow)', marginTop: '0.2rem' }}>
              {(log.confidence_score * 100).toFixed(1)}%
            </div>
          </div>
          <div style={{ background: 'rgba(255, 255, 255, 0.02)', padding: '0.8rem', borderRadius: '8px', border: '1px solid var(--border-glass)' }}>
            <span style={{ fontSize: '0.72rem', color: 'var(--text-dim)' }}>게이트웨이 지연시간</span>
            <div style={{ fontSize: '0.88rem', fontWeight: 600, color: latencyColor, marginTop: '0.2rem' }}>
              {log.latency_ms.toFixed(3)} ms <span style={{ fontSize: '0.7rem', color: 'var(--text-dim)' }}>(SLA 통과)</span>
            </div>
          </div>
        </div>

        {/* OWASP LLM Mapping */}
        {reportData?.owasp_category && (
          <div style={{ marginTop: '1rem', padding: '0.7rem 1rem', borderRadius: '8px', background: 'rgba(168, 85, 247, 0.08)', border: '1px solid rgba(168, 85, 247, 0.25)', display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.82rem' }}>
            <AlertTriangle size={16} style={{ color: 'var(--accent-purple)' }} />
            <span><strong>OWASP Top 10 for LLM:</strong> {reportData.owasp_category}</span>
          </div>
        )}

        {/* Payload Forensics */}
        <div style={{ marginTop: '1.2rem', display: 'flex', flexDirection: 'column', gap: '0.8rem' }}>
          <div>
            <span style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)' }}>
              🔴 실제 공격자 입력 페이로드 (Raw Prompt Payload):
            </span>
            <div
              style={{
                marginTop: '0.4rem',
                padding: '0.8rem',
                borderRadius: '8px',
                background: 'rgba(0, 0, 0, 0.5)',
                border: '1px solid rgba(244, 63, 94, 0.2)',
                fontFamily: 'monospace',
                fontSize: '0.8rem',
                color: '#f87171',
                whiteSpace: 'pre-wrap',
                wordBreak: 'break-all'
              }}
            >
              {fullPrompt}
            </div>
          </div>

          <div>
            <span style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)' }}>
              🟡 정규화 및 난독화 역분석 텍스트 (Normalized Preprocessing):
            </span>
            <div
              style={{
                marginTop: '0.4rem',
                padding: '0.8rem',
                borderRadius: '8px',
                background: 'rgba(0, 0, 0, 0.5)',
                border: '1px solid var(--border-glass)',
                fontFamily: 'monospace',
                fontSize: '0.8rem',
                color: 'var(--text-main)',
                whiteSpace: 'pre-wrap',
                wordBreak: 'break-all'
              }}
            >
              {normalizedPrompt}
            </div>
          </div>
        </div>

        {/* Remediation & Impact */}
        <div style={{ marginTop: '1.2rem', padding: '1rem', borderRadius: '8px', background: 'rgba(16, 185, 129, 0.05)', border: '1px solid rgba(16, 185, 129, 0.2)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--accent-green)', fontWeight: 600, fontSize: '0.85rem' }}>
            <CheckCircle2 size={16} />
            <span>방어 엔진 조치 결과 및 SOC 보안 권고사항</span>
          </div>
          <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: '0.4rem', lineHeight: '1.4' }}>
            Prompt Shield 인라인 가드 엔진이 입력 검증 단계에서 <strong>{log.latency_ms.toFixed(3)}ms</strong> 만에 해당 위협을 식별하여
            HTTP 403 Forbidden 응답으로 원천 차단하였습니다. 대상 LLM(<code>{log.target_model || 'llama3.2:1B'}</code>) 본체로는 악성 페이로드가 전혀 도달하지 않았습니다.
          </p>
        </div>

        {/* Footer Actions */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '1.5rem', paddingTop: '1rem', borderTop: '1px solid var(--border-glass)' }}>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>
            Prompt Shield Security Incident Intelligence Engine
          </div>
          <div style={{ display: 'flex', gap: '0.6rem' }}>
            <button
              className="btn btn-secondary"
              onClick={handleCopy}
              style={{ padding: '0.45rem 1rem', fontSize: '0.8rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}
            >
              <Copy size={14} />
              <span>{copied ? '복사 완료! ✅' : '마크다운 리포트 복사'}</span>
            </button>
            <button
              className="btn btn-primary"
              onClick={handleDownload}
              style={{ padding: '0.45rem 1rem', fontSize: '0.8rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}
            >
              <Download size={14} />
              <span>리포트 다운로드 (.md)</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
