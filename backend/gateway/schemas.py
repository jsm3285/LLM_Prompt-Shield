"""
Pydantic Schemas for Prompt Shield API Gateway.
"""

from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field


# --- OpenAI Chat Completion Proxy Schemas ---
class ChatMessage(BaseModel):
    role: str
    content: str
    name: Optional[str] = None


class ChatCompletionRequest(BaseModel):
    model: str = "gpt-4o-mini"
    messages: List[ChatMessage]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = None
    stream: Optional[bool] = False


# --- Threat Security Response (HTTP 403) ---
class ThreatBlockedDetail(BaseModel):
    status: str = "BLOCKED"
    code: int = 403
    threat_category: str
    confidence_score: float
    matched_pattern_id: Optional[str] = None
    matched_pattern: Optional[str] = None
    reason: str
    latency_ms: float


class ThreatBlockedResponse(BaseModel):
    error: Dict[str, Any]


# --- Shield Dashboard & Inspection Schemas ---
class ShieldInspectRequest(BaseModel):
    prompt: str


class ShieldInspectResponse(BaseModel):
    raw_prompt: str
    normalized_prompt: str
    is_blocked: bool
    threat_category: Optional[str] = None
    confidence_score: float
    matched_pattern_id: Optional[str] = None
    matched_pattern: Optional[str] = None
    detected_rules: List[str]
    detected_obfuscation: List[str]
    preprocessor_latency_ms: float
    engine_latency_ms: float
    total_latency_ms: float
    p95_sla_met: bool


class AuditLogItem(BaseModel):
    id: str
    timestamp: str
    client_ip: str
    prompt_snippet: str
    is_blocked: bool
    threat_category: Optional[str]
    confidence_score: float
    latency_ms: float
    action: str  # PASSED | BLOCKED


class MetricsResponse(BaseModel):
    total_requests: int
    blocked_requests: int
    allowed_requests: int
    block_rate_percent: float
    avg_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    threat_category_breakdown: Dict[str, int]
