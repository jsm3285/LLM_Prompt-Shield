# 🛡️ Prompt Shield

> **초저지연(P95 < 25ms) 인라인 LLM 보안 역방향 프록시 게이트웨이**
> **백엔드:** FastAPI (Python) | **프론트엔드:** React (Vite + Modern UI)

Prompt Shield는 상용 LLM(OpenAI `gpt-4o-mini` 등) 전단에 위치하여 탈옥(Jailbreak), 프롬프트 인젝션(Prompt Injection), 기밀/비밀키 탈취(Data Exfiltration) 공격을 실시간으로 감지하고 차단하는 보안 역방향 프록시 시스템입니다.

---

## 📐 시스템 아키텍처

```
[ Client / App ] ──► [ React SPA Dashboard (frontend/) ]
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│           FastAPI Security Gateway (backend/)               │
│                                                             │
│  1. Text Normalization Preprocessor                         │
│     - Zero-width space, Leetspeak, Base64 해제 & <1ms 검사 │
│                                                             │
│  2. AI Guard Engine & In-Memory Vector Store                │
│     - 384차원 고속 정규화 코사인 임베딩 매칭 (<2ms)          │
│                                                             │
│  3. Decision Pipeline                                       │
│     - 🛑 Threat: 403 Forbidden 차단                          │
│     - 🟢 Normal: Upstream OpenAI Proxy 전달                  │
│                                                             │
│  4. Real-time Telemetry & Audit Operations Stream           │
└─────────────────────────────────────────────────────────────┘
                           │ (Safe Prompts Only)
                           ▼
┌─────────────────────────────────────────────────────────────┐
│               Upstream Commercial LLM API                   │
│                    (OpenAI gpt-4o-mini)                     │
└─────────────────────────────────────────────────────────────┘
```

---

## 📂 디렉터리 구조

```
/home/jsm/llm_project/
├── backend/                    # FastAPI 백엔드 게이트웨이
│   ├── core/
│   │   ├── preprocessor.py    # 정규화 전처리 & 1ms 패턴 규칙 감지
│   │   └── dataset.py         # 악성 프롬프트 데이터셋 로더
│   ├── engine/
│   │   ├── guard_engine.py    # AI 임베딩 추론 & 위협 판정 엔진
│   │   └── vector_store.py    # In-Memory FAISS/Numpy 벡터 유사도 검색기
│   ├── gateway/
│   │   ├── main.py            # FastAPI 서버 엔트리포인트 & React SPA 서빙
│   │   ├── config.py          # 환경 설정 로더
│   │   ├── schemas.py         # API 요청/응답 Pydantic 스키마
│   │   ├── routes.py          # OpenAI 호환 프록시 & 관제 API
│   │   └── logger.py          # P95/P99 지연시간 산출 및 감사 로그
│   └── data/
│       └── attack_vectors.json# Seed 공격 벡터 시나리오 데이터셋
├── frontend/                   # React + Vite 관제 대시보드
│   ├── src/
│   │   ├── components/        # Header, MetricsGrid, Playground, Telemetry, AuditLog
│   │   ├── App.jsx            # React 대시보드 메인 컴포넌트
│   │   └── index.css          # 다크 글래스모피즘 스타일시트
│   ├── vite.config.js         # Vite 개발 서버 및 API 프록시 설정
│   └── package.json
├── tests/                      # Pytest 단위 및 통합 테스트
│   ├── test_preprocessor.py
│   ├── test_guard_engine.py
│   └── test_gateway.py
├── .env.example
├── requirements.txt
└── README.md
```

---

## 🚀 실행 가이드

### 1. 백엔드 가상 환경 & 테스트 실행
```bash
# 백엔드 테스트 실행
PYTHONPATH=backend .venv/bin/pytest -v

# FastAPI 게이트웨이 서버 실행
PYTHONPATH=backend .venv/bin/python3 -m gateway.main
```
- **역방향 프록시 API**: `http://127.0.0.1:8000/v1/chat/completions`
- **Swagger API 문서**: `http://127.0.0.1:8000/docs`

### 2. 프론트엔드 React 대시보드 실행
```bash
# 개발 서버 실행 (Vite Dev Server)
cd frontend
npm run dev

# 프로덕션 빌드
npm run build
```
- **React 개발 관제 UI**: `http://localhost:3000` (FastAPI 8000 포트 자동 프록시)
