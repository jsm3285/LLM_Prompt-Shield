"""
Audit Logger & Real-time Metrics Collector for Prompt Shield.

Tracks latency statistics (P95, P99), audit log streams, threat breakdown counters.
"""

import time
import uuid
import numpy as np
from datetime import datetime
from typing import List, Dict, Any, Optional
from gateway.schemas import AuditLogItem, MetricsResponse



class MetricsCollector:
    """In-memory telemetry logger and P95 latency analytics engine."""

    def __init__(self, max_logs: int = 500):
        self.max_logs = max_logs
        self.logs: List[AuditLogItem] = []
        self.latencies_ms: List[float] = []
        
        self.total_requests: int = 0
        self.blocked_requests: int = 0
        self.allowed_requests: int = 0
        self.category_counts: Dict[str, int] = {
            "jailbreak": 0,
            "prompt_injection": 0,
            "data_exfiltration": 0
        }

    def sanitize_snippet(self, text: str, max_len: int = 60) -> str:
        """Masks long strings and returns safe audit snippet."""
        clean = text.replace("\n", " ").strip()
        if len(clean) > max_len:
            return clean[:max_len] + "..."
        return clean

    def record_event(
        self,
        prompt: str,
        is_blocked: bool,
        threat_category: str,
        confidence_score: float,
        latency_ms: float,
        client_ip: str = "127.0.0.1",
        normalized_prompt: str = "",
        matched_pattern: str = "",
        target_model: str = "llama3.2:1B Instruct",
        detected_rules: List[str] = None
    ) -> AuditLogItem:
        """Records an API request event and updates live metrics."""
        self.total_requests += 1
        self.latencies_ms.append(latency_ms)

        if is_blocked:
            self.blocked_requests += 1
            if threat_category:
                cat_key = threat_category.lower()
                self.category_counts[cat_key] = self.category_counts.get(cat_key, 0) + 1
            action = "BLOCKED"
        else:
            self.allowed_requests += 1
            action = "PASSED"

        item = AuditLogItem(
            id=f"LOG-{uuid.uuid4().hex[:8].upper()}",
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            client_ip=client_ip,
            prompt_snippet=self.sanitize_snippet(prompt),
            full_prompt=prompt,
            normalized_prompt=normalized_prompt or prompt,
            is_blocked=is_blocked,
            threat_category=threat_category,
            confidence_score=round(confidence_score, 4),
            matched_pattern=matched_pattern or ("유사도 임계치 초과" if is_blocked else "정상"),
            target_model=target_model,
            detected_rules=detected_rules or [],
            latency_ms=round(latency_ms, 3),
            action=action
        )

        self.logs.insert(0, item)
        if len(self.logs) > self.max_logs:
            self.logs.pop()

        return item

    def get_metrics(self) -> MetricsResponse:
        """Computes current aggregate metrics including P95 / P99 latency."""
        if not self.latencies_ms:
            return MetricsResponse(
                total_requests=0,
                blocked_requests=0,
                allowed_requests=0,
                block_rate_percent=0.0,
                avg_latency_ms=0.0,
                p95_latency_ms=0.0,
                p99_latency_ms=0.0,
                threat_category_breakdown=self.category_counts
            )

        arr = np.array(self.latencies_ms)
        block_rate = (self.blocked_requests / self.total_requests) * 100.0

        return MetricsResponse(
            total_requests=self.total_requests,
            blocked_requests=self.blocked_requests,
            allowed_requests=self.allowed_requests,
            block_rate_percent=round(block_rate, 2),
            avg_latency_ms=round(float(np.mean(arr)), 3),
            p95_latency_ms=round(float(np.percentile(arr, 95)), 3),
            p99_latency_ms=round(float(np.percentile(arr, 99)), 3),
            threat_category_breakdown=self.category_counts
        )

    def get_logs(self, limit: int = 50) -> List[AuditLogItem]:
        """Returns recent audit logs."""
        return self.logs[:limit]

    def get_log_by_id(self, log_id: str) -> Optional[AuditLogItem]:
        """Finds an audit log entry by ID."""
        for log in self.logs:
            if log.id == log_id:
                return log
        return None

    def generate_incident_report(self, log: AuditLogItem) -> Dict[str, Any]:
        """Generates comprehensive security incident forensic audit report."""
        owasp_map = {
            "jailbreak": "LLM01: Prompt Injection / Persona Breakout",
            "prompt_injection": "LLM01: Prompt Injection (Direct/Indirect)",
            "data_exfiltration": "LLM02: Sensitive Information Disclosure / Credential Theft"
        }
        owasp_item = owasp_map.get(str(log.threat_category).lower(), "LLM01: Prompt Injection")

        report_md = f"""# 🛡️ Prompt Shield 보안 침해 분석 리포트 (Security Incident Report)

## 1. 사건 개요 (Incident Overview)
- **사건 ID (Log ID)**: `{log.id}`
- **발생 일시**: `{log.timestamp}`
- **공격 발신 IP**: `{log.client_ip}`
- **대상 LLM 모델**: `{log.target_model}`
- **조치 결과**: `{'🛑 403 Forbidden 즉각 차단 완료 (LLM 전달 거부)' if log.is_blocked else '🟢 정상 통과 (200 OK)'}`
- **게이트웨이 지연시간**: `{log.latency_ms:.3f} ms` (SLA < 25.0ms 충족: {'✅ PASS' if log.latency_ms <= 25.0 else '⚠️ WARN'})

## 2. 위협 인텔리전스 분석 (Threat Intelligence)
- **위협 유형**: `{log.threat_category or 'None'}`
- **OWASP LLM 분류**: `{owasp_item}`
- **벡터 유사도 신뢰도**: `{log.confidence_score * 100:.1f}%`
- **매칭 시나리오**: `{log.matched_pattern or '휴리스틱/인메모리 벡터 매칭'}`
- **탐지된 전처리 룰**: `{', '.join(log.detected_rules) if log.detected_rules else '없음'}`

## 3. 공격 페이로드 포렌식 (Payload Forensics)
### [원본 공격 프롬프트 (Raw Payload)]
```text
{log.full_prompt}
```

### [정규화 전처리 텍스트 (Normalized)]
```text
{log.normalized_prompt}
```

## 4. 침해 영향도 및 권고 조치 (Impact & Remediation)
- **공격 영향도**: 차단 실패 시 시스템 프롬프트 유출, 제약 해제, 또는 백엔드 비밀정보 탈취 가능성 존재.
- **방어 메커니즘**: Prompt Shield 인라인 가드 엔진이 입력 단계에서 {log.latency_ms:.3f}ms 만에 감지하여 업스트림 LLM으로의 패킷 전송을 원천 차단함.
- **보안 권고사항**:
  1. 시스템 프롬프트 내 API Key 및 DB 암호 하드코딩 금지
  2. Sandwich Defense 래퍼 및 악성 구분자 정화 필터 상시 활성화
  3. 반복 공격 IP({log.client_ip})에 대한 WAF 레이트 리밋 적용 권장
"""

        return {
            "log": log.model_dump(),
            "owasp_category": owasp_item,
            "markdown_report": report_md
        }


# Global metrics instance
metrics_collector = MetricsCollector()

