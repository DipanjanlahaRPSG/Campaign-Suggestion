# Project Research Summary

**Project:** Campaign Suggestion  
**Domain:** AI-powered SMS/WhatsApp campaign suggestion and optimization  
**Researched:** 2026-03-05  
**Confidence:** MEDIUM-HIGH

## Executive Summary

This product is best built as a **custom, in-house AI campaign system**: own the generation/scoring/recommendation intelligence internally while integrating only channel transport APIs needed for SMS/WhatsApp dispatch. The strongest recommendation across research is to separate responsibilities cleanly: relational operations in Postgres, analytics in ClickHouse (or defer until needed), model pipelines in Python/Prefect, tabular prediction via XGBoost/scikit-learn, and LLM generation with strong guardrails.

The recommended approach is **foundation-first, then intelligence, then automation**. Start with ingestion quality, data contracts, and measurable KPIs; then ship a baseline suggestion flow (segment → generate variants → score → dispatch); then close the feedback loop for retraining and A/B-driven improvement. This order aligns with both architecture dependencies and feature maturity, and avoids premature complexity.

Key risks are predictable and manageable: cold-start performance, model drift, hallucinated offers, compliance failures, and feedback-loop bias. Mitigation should be designed in from Phase 1: fallback logic for sparse-history cohorts, explicit model monitoring/retraining triggers, fact-check and approval gates before send, consent/compliance checks in delivery, and exploration constraints to prevent repetitive or brittle recommendations.

## Key Findings

### Recommended Stack

The stack research supports a modern Python-centered architecture optimized for fast delivery and iterative ML improvement. Use Python 3.12 with FastAPI + Pydantic for typed APIs and contracts; Postgres as the operational source of truth; Redis for queueing/rate-limiting; Prefect + dbt for pipeline orchestration and metrics modeling; and XGBoost/scikit-learn + MLflow for predictive modeling and lifecycle control. Keep LLM provider flexibility (OpenAI + Anthropic behind LiteLLM) to reduce reliability and pricing risk.

**Core technologies:**
- **Python 3.12 + FastAPI + Pydantic 2**: API/inference backbone with strong validation and async support.
- **PostgreSQL 17 + pgvector**: transactional core plus lightweight semantic retrieval without extra vector infra in MVP.
- **Prefect 3 + dbt-core + MLflow**: orchestrated data/model workflows with reproducibility and experiment tracking.
- **XGBoost + scikit-learn**: calibrated tabular prediction is preferred over pure LLM ranking for campaign performance.
- **Twilio SDK**: fastest MVP path for both SMS and WhatsApp delivery integration.

**Critical version requirements:**
- FastAPI 0.135.1 with Pydantic 2.12.5
- SQLAlchemy 2.x patterns only
- Redis client/server major compatibility discipline

### Expected Features

Research is clear that the market has strict table stakes, and differentiation comes from proprietary performance learning.

**Must have (table stakes):**
- Historical data ingestion and normalization
- Campaign/contact/template storage
- Basic AI content generation
- Audience segmentation
- SMS + WhatsApp delivery
- Performance tracking and A/B testing baseline

**Should have (competitive differentiators):**
- Historical data-trained generation (primary moat)
- Engagement prediction scoring before send
- Send-time optimization by segment/user
- Personalized content at segment scale

**Defer (v2+):**
- Auto-optimizing closed-loop campaigns
- Creative fatigue automation beyond basic monitoring
- Churn prediction/re-engagement automation
- Multi-language, email/social extensions, real-time conversational flows

### Architecture Approach

Use a layered architecture with strict boundaries: **Data Sources → Ingestion/Validation → Feature/Model Layer → Campaign Suggestion Orchestration → Delivery → Feedback Loop**. Keep ML models inference-focused in runtime and retrain offline. The campaign engine should combine segmentation, generation, and scoring outputs into actionable suggestions (what/who/when), while delivery remains execution-only. This boundary discipline is critical to maintain explainability, replaceability, and phase-wise shipping speed.

**Major components:**
1. **Data pipeline + feature layer** — cleans, validates, and prepares model-ready features.
2. **ML services (segmentation, generation, scoring)** — produce bounded outputs, no orchestration logic.
3. **Campaign suggestion engine** — policy layer that assembles recommendations and dispatch decisions.
4. **Delivery + tracking** — channel execution, status capture, and feedback ingestion for retraining.

### Critical Pitfalls

1. **Cold start coverage gaps** — mitigate with dual fallback logic (similar-campaign retrieval + rule-based baselines) and explicit confidence thresholds.
2. **Concept drift/model decay** — implement monitoring and scheduled retraining triggers early; do not treat retraining as optional.
3. **Hallucinated promotional claims** — enforce fact-base validation + human approval for high-risk campaigns.
4. **Feedback-loop bias/creative fatigue** — enforce exploration quotas, novelty scoring, and similarity/frequency caps.
5. **Compliance failures (TCPA/GDPR/WhatsApp policy)** — add consent checks and compliance gates directly in dispatch workflows.

## Implications for Roadmap

Based on combined research, a **5-phase plan** is the most resilient and fastest path to value.

### Phase 1: Data, Governance, and Compliance Foundation
**Rationale:** All downstream value depends on clean data, correct KPIs, and legal-safe delivery constraints.  
**Delivers:** Ingestion pipelines, schema validation, canonical metrics definitions, consent/compliance gates, baseline storage model.  
**Addresses:** Data Ingestion, Campaign Storage, Contact Management, Performance Tracking foundation.  
**Avoids:** Data quality pitfall, wrong metric optimization, early compliance violations, cold-start blindness.

### Phase 2: Baseline Suggestion MVP (Human-in-the-Loop)
**Rationale:** Ship usable business value before heavy optimization; validate workflow and trust.  
**Delivers:** Basic generation, segmentation, SMS/WhatsApp send path, manual approval UX/process, first analytics dashboard.  
**Uses:** FastAPI/Pydantic, Postgres, Twilio, basic LLM integration.  
**Implements:** Core orchestration and delivery architecture with approval checkpoints.  
**Avoids:** Over-automation and hallucination risk.

### Phase 3: Differentiation Engine (Data-Trained Intelligence)
**Rationale:** Convert proprietary historical data into defensible advantage once MVP data contracts are stable.  
**Delivers:** Historical data-trained generation, engagement scoring model, segment-specific recommendations, ranking logic.  
**Addresses:** Key differentiator features from FEATURES.md.  
**Avoids:** Premature complexity by introducing models only after data maturity.

### Phase 4: Feedback Loop and Experimentation
**Rationale:** Sustained performance requires adaptation and controlled experimentation.  
**Delivers:** Drift monitoring, retraining workflows, A/B framework, model/version tracking, diversity controls.  
**Uses:** Prefect, MLflow, Evidently, dbt metrics contracts.  
**Avoids:** Concept drift, feedback-loop bias, creative fatigue.

### Phase 5: Optimization and Scale
**Rationale:** Scale only after proving unit economics and model lift.  
**Delivers:** Send-time optimization, auto-optimization policies with guardrails, selective infra scale-outs (ClickHouse/feature store evolution).  
**Addresses:** Advanced differentiators deferred from MVP.  
**Avoids:** Integration overload and unnecessary infra spend.

### Phase Ordering Rationale

- Dependencies are strict: ingestion/quality/compliance must precede reliable model outputs.
- Architecture supports parallelism in Phase 3 (generation/scoring/segmentation) once feature contracts stabilize.
- Risk controls are intentionally left-shifted to prevent expensive rework in later phases.

### Research Flags

Phases likely needing deeper research during planning:
- **Phase 1:** Compliance specifics (TCPA/GDPR/WhatsApp template policy) and consent enforcement by region.
- **Phase 3:** Model strategy details (fine-tune vs RAG-first vs prompt-only for generation; calibration approach for scoring).
- **Phase 5:** Scale architecture thresholds (when to introduce ClickHouse-first analytics patterns or dedicated feature store).

Phases with standard patterns (can usually skip deeper research-phase):
- **Phase 2:** CRUD + delivery integration + approval workflow are well-established product patterns.
- **Phase 4 (core MLOps mechanics):** Drift monitoring and scheduled retraining patterns are mature and widely documented.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Grounded in official docs/package registries and clear compatibility guidance. |
| Features | HIGH | Strong alignment with current AI campaign market expectations. |
| Architecture | MEDIUM-HIGH | Solid layered pattern, but some source quality is mixed and one doc suggests heavier tooling than stack recommendation. |
| Pitfalls | MEDIUM | Risks are credible and common, but several sources are secondary and jurisdiction-specific compliance details remain open. |

**Overall confidence:** MEDIUM-HIGH

### Gaps to Address

- **Regulatory depth by geography:** Run targeted legal/compliance validation before implementation commitments.
- **WhatsApp template and policy workflows:** Confirm operational constraints and approval SLAs with chosen provider.
- **A/B testing design for messaging channels:** Define minimum sample sizes and decision thresholds to avoid false lift.
- **Cold-start baseline definition:** Choose concrete fallback policies and confidence-driven routing before MVP launch.
- **Architecture-tooling alignment:** Resolve Prefect-vs-Airflow ambiguity early to avoid orchestration churn.

## Sources

### Primary (HIGH confidence)
- PostgreSQL, Prefect, dbt, Twilio, Anthropic official docs
- PyPI package metadata and release registries for version pinning
- STACK.md, FEATURES.md, ARCHITECTURE.md, PITFALLS.md (project research artifacts)

### Secondary (MEDIUM confidence)
- Martech ecosystem landscape references (competitive context)
- Architecture blogs and implementation pattern writeups referenced in ARCHITECTURE.md
- Recommender/ML operations commentary and drift discussions referenced in PITFALLS.md

### Tertiary (LOW confidence)
- General marketing blog case compilations on AI ad failures and trend extrapolations; useful directional input, not implementation authority.

---
*Research completed: 2026-03-05*  
*Ready for roadmap: yes*
