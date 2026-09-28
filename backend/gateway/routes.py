"""
FastAPI Router for Prompt Shield Gateway & Dashboard Telemetry.
"""

import time
import httpx
from fastapi import APIRouter, HTTPException, Request, Response, status
from fastapi.responses import JSONResponse

from core.preprocessor import TextPreprocessor
from core.dataset import AttackVectorDataset, AttackVector
from engine.guard_engine import GuardEngine
from gateway.config import settings
from gateway.schemas import (
    ChatCompletionRequest,
    ThreatBlockedResponse,
    ShieldInspectRequest,
    ShieldInspectResponse,
    MetricsResponse
)
from gateway.logger import metrics_collector

router = APIRouter()

# Core instances
preprocessor = TextPreprocessor()
dataset = AttackVectorDataset(file_path=settings.ATTACK_DATASET_PATH)
guard_engine = GuardEngine(dataset=dataset, threshold=settings.SIMILARITY_THRESHOLD)


@router.post("/v1/chat/completions", response_model=None)
async def chat_completions_proxy(req: ChatCompletionRequest, request: Request):
    """
    Inline Reverse Proxy Endpoint (OpenAI API Compatible).
    Intercepts and inspects user prompts before forwarding to upstream LLM.
    """
    start_time = time.perf_counter()
    client_ip = request.client.host if request.client else "127.0.0.1"

    # Extract user input prompt (last message content)
    user_prompt = ""
    for msg in reversed(req.messages):
        if msg.role == "user":
            user_prompt = msg.content
            break

    if not user_prompt:
        user_prompt = req.messages[-1].content if req.messages else ""

    # 1. Normalize Preprocessing
    prep_res = preprocessor.normalize(user_prompt)

    # 2. Guard Engine Threat Evaluation
    decision = guard_engine.evaluate(prep_res)

    total_latency = (time.perf_counter() - start_time) * 1000.0

    # Record telemetry event
    metrics_collector.record_event(
        prompt=user_prompt,
        is_blocked=decision.is_threat,
        threat_category=decision.threat_category or "None",
        confidence_score=decision.confidence_score,
        latency_ms=total_latency,
        client_ip=client_ip
    )

    # 3. IF THREAT: Block with 403 Forbidden (Fail-Close)
    if decision.is_threat:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={
                "error": {
                    "message": "Prompt Shield blocked request due to detected security threat.",
                    "type": "prompt_shield_security_exception",
                    "code": "403_threat_blocked",
                    "threat_category": decision.threat_category,
                    "confidence_score": decision.confidence_score,
                    "matched_pattern_id": decision.matched_pattern_id,
                    "matched_pattern": decision.matched_pattern,
                    "reason": decision.decision_reason,
                    "gateway_latency_ms": round(total_latency, 3)
                }
            }
        )

    # 4. IF SAFE: Proxy to Upstream LLM or Return Mock Completion
    if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != "sk-demo-mock-key":
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                upstream_url = f"{settings.OPENAI_BASE_URL.rstrip('/')}/chat/completions"
                headers = {
                    "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
                    "Content-Type": "application/json"
                }
                resp = await client.post(upstream_url, json=req.model_dump(), headers=headers)
                return Response(content=resp.content, status_code=resp.status_code, media_type="application/json")
        except Exception as e:
            # Fallback if upstream fails
            pass

    # Simulated safe response when no real API key is configured
    return {
        "id": "chatcmpl-promptshield-demo",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": req.model,
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": f"Prompt Shield Verified Safe. Processed in {total_latency:.2f}ms. Response to: {user_prompt[:50]}"
                },
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": len(user_prompt.split()),
            "completion_tokens": 15,
            "total_tokens": len(user_prompt.split()) + 15
        },
        "prompt_shield_telemetry": {
            "preprocessor_latency_ms": prep_res.processing_time_ms,
            "guard_engine_latency_ms": decision.engine_latency_ms,
            "total_latency_ms": round(total_latency, 3),
            "p95_budget_met": total_latency <= settings.MAX_LATENCY_BUDGET_MS
        }
    }


@router.post("/api/v1/shield/inspect", response_model=ShieldInspectResponse)
async def inspect_prompt(req: ShieldInspectRequest):
    """Inspection playground endpoint for testing prompts against Prompt Shield."""
    start_time = time.perf_counter()
    prep_res = preprocessor.normalize(req.prompt)
    decision = guard_engine.evaluate(prep_res)
    total_latency = (time.perf_counter() - start_time) * 1000.0

    metrics_collector.record_event(
        prompt=req.prompt,
        is_blocked=decision.is_threat,
        threat_category=decision.threat_category or "None",
        confidence_score=decision.confidence_score,
        latency_ms=total_latency
    )

    return ShieldInspectResponse(
        raw_prompt=req.prompt,
        normalized_prompt=prep_res.normalized_text,
        is_blocked=decision.is_threat,
        threat_category=decision.threat_category,
        confidence_score=decision.confidence_score,
        matched_pattern_id=decision.matched_pattern_id,
        matched_pattern=decision.matched_pattern,
        detected_rules=prep_res.detected_rules,
        detected_obfuscation=prep_res.detected_obfuscation,
        preprocessor_latency_ms=prep_res.processing_time_ms,
        engine_latency_ms=decision.engine_latency_ms,
        total_latency_ms=round(total_latency, 3),
        p95_sla_met=total_latency <= settings.MAX_LATENCY_BUDGET_MS
    )


@router.get("/api/v1/shield/metrics", response_model=MetricsResponse)
async def get_metrics():
    """Returns telemetry metrics and latency analytics."""
    return metrics_collector.get_metrics()


@router.get("/api/v1/shield/logs")
async def get_audit_logs(limit: int = 50):
    """Returns real-time audit log stream."""
    return metrics_collector.get_logs(limit=limit)


@router.get("/api/v1/shield/vectors")
async def get_vectors():
    """Returns list of active indexed attack vectors."""
    return {
        "count": dataset.vectors.__len__(),
        "vectors": dataset.vectors
    }


@router.post("/api/v1/shield/vectors")
async def add_vector(vec: AttackVector):
    """Dynamically adds a new vector and triggers real-time index synchronization."""
    dataset.add_vector(vec)
    guard_engine.sync_vectors()
    return {
        "status": "SUCCESS",
        "message": f"Attack vector [{vec.id}] added and vector store synchronized.",
        "vector_count": guard_engine.vector_store.count()
    }
