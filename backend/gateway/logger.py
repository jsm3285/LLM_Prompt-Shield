"""
Audit Logger & Real-time Metrics Collector for Prompt Shield.

Tracks latency statistics (P95, P99), audit log streams, threat breakdown counters.
"""

import time
import uuid
import numpy as np
from datetime import datetime
from typing import List, Dict, Any
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
        client_ip: str = "127.0.0.1"
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
            is_blocked=is_blocked,
            threat_category=threat_category,
            confidence_score=round(confidence_score, 4),
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


# Global metrics instance
metrics_collector = MetricsCollector()
