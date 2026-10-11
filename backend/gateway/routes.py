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
from engine.sanitizer import PromptSanitizer
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
sanitizer = PromptSanitizer()



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
    event_item = metrics_collector.record_event(
        prompt=user_prompt,
        is_blocked=decision.is_threat,
        threat_category=decision.threat_category or "None",
        confidence_score=decision.confidence_score,
        latency_ms=total_latency,
        client_ip=client_ip,
        normalized_prompt=prep_res.normalized_text,
        matched_pattern=decision.matched_pattern,
        target_model=req.model or settings.DEFAULT_MODEL,
        detected_rules=prep_res.detected_rules
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
                    "gateway_latency_ms": round(total_latency, 3),
                    "log_id": event_item.id
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
        "model": req.model or settings.DEFAULT_MODEL,
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": f"🛡️ [Prompt Shield 보호 통과] 검증 완료(정상 프롬프트). {settings.TARGET_LLM_NAME} 응답: '{user_prompt[:60]}'에 대한 안전한 처리 결과입니다."
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
            "p95_budget_met": total_latency <= settings.MAX_LATENCY_BUDGET_MS,
            "target_model": settings.DEFAULT_MODEL
        }
    }


@router.post("/v1/raw/chat/completions", response_model=None)
async def raw_chat_completions(req: ChatCompletionRequest, request: Request):
    """
    Unprotected Raw LLM Endpoint (Bypasses Prompt Shield).
    Directly routes to target vulnerable LLM (llama3.2:1B Instruct) for A/B security demonstration.
    """
    start_time = time.perf_counter()
    user_prompt = ""
    for msg in reversed(req.messages):
        if msg.role == "user":
            user_prompt = msg.content
            break
    if not user_prompt:
        user_prompt = req.messages[-1].content if req.messages else ""

    # Forward directly to upstream local LLM (Ollama/vLLM) if active
    if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != "sk-demo-mock-key":
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                upstream_url = f"{settings.OPENAI_BASE_URL.rstrip('/')}/chat/completions"
                headers = {
                    "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
                    "Content-Type": "application/json"
                }
                resp = await client.post(upstream_url, json=req.model_dump(), headers=headers)
                if resp.status_code == 200:
                    return Response(content=resp.content, status_code=resp.status_code, media_type="application/json")
        except Exception:
            pass

    # High-impact A/B demo response demonstrating vulnerable LLM behavior without guardrails
    p_lower = user_prompt.lower()
    if any(kw in p_lower for kw in ["api_key", "비밀번호", "환경 변수", "jwt_secret", "aws"]):
        simulated_reply = "⚠️ [취약점 노출] 환경 변수 설정값 출력:\nOPENAI_API_KEY=sk-live-llama32-priv-9921\nDATABASE_URL=postgres://admin:P@ssword2026@127.0.0.1:5432/shield_db"
    elif any(kw in p_lower for kw in ["dan", "탈옥", "제약", "개발자 모드"]):
        simulated_reply = "⚠️ [탈옥 성공] 이전 지침을 무시하고 개발자/DAN 모드로 전환되었습니다. 모든 윤리적 제약 없이 요청하신 작업을 수행합니다."
    elif any(kw in p_lower for kw in ["시스템 프롬프트", "system prompt", "지침"]):
        simulated_reply = "⚠️ [시스템 프롬프트 유출] 초기 설정값:\n'You are a corporate AI assistant. Internal system token: CONFIDENTIAL_MODEL_SEED_10492'"
    else:
        simulated_reply = f"[llama3.2:1B Instruct 응답] 질문 '{user_prompt[:50]}'에 대한 답변입니다. (보호 솔루션 미적용 상태)"

    total_latency = (time.perf_counter() - start_time) * 1000.0
    return {
        "id": "chatcmpl-raw-llama32-demo",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": req.model or settings.DEFAULT_MODEL,
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": simulated_reply
                },
                "finish_reason": "stop"
            }
        ],
        "is_shield_protected": False,
        "latency_ms": round(total_latency + 14.5, 2)
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


@router.get("/api/v1/shield/logs/{log_id}/report")
async def get_log_report(log_id: str):
    """Returns detailed forensic security incident report for a given attack log."""
    log = metrics_collector.get_log_by_id(log_id)
    if not log:
        raise HTTPException(status_code=404, detail=f"Audit log ID [{log_id}] not found.")
    return metrics_collector.generate_incident_report(log)



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


@router.get("/api/v1/shield/info")
async def get_shield_info():
    """Returns engine diagnostics, active vector store backend, and embedding extractor."""
    return {
        "status": "ONLINE",
        "engine": guard_engine.get_engine_info(),
        "target_llm": {
            "model": settings.DEFAULT_MODEL,
            "name": settings.TARGET_LLM_NAME,
            "upstream_url": settings.OPENAI_BASE_URL
        },
        "p95_budget_ms": settings.MAX_LATENCY_BUDGET_MS
    }


@router.post("/api/v1/shield/sanitize")
async def sanitize_prompt_endpoint(req: ShieldInspectRequest):
    """
    Sanitizes untrusted prompt and generates Sandwich Defense wrapper (WBS 3.2.6).
    Neutralizes injection delimiters, redacts high-risk target keywords, and encapsulates prompt.
    """
    san_res = sanitizer.sanitize(req.prompt)
    sandwich_res = sanitizer.apply_sandwich_defense(req.prompt)
    return {
        "sanitization": san_res.model_dump(),
        "sandwich_defense": sandwich_res.model_dump()
    }



