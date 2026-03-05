# Stack Research

**Domain:** AI-powered campaign suggestion platform (SMS/WhatsApp)  
**Researched:** 2026-03-05  
**Confidence:** MEDIUM-HIGH *(official docs + package registries; no Context7 access in this environment)*

## Recommended Stack (2026 baseline)

### Core Technologies

| Technology | Version | Purpose | Why Recommended | Confidence |
|------------|---------|---------|-----------------|------------|
| Python | 3.12 (runtime baseline) | Backend + ML + orchestration language | Best ecosystem fit for LLM apps, tabular ML, and data pipelines in one stack | HIGH |
| FastAPI | 0.135.1 | Inference/API layer for suggestions and scoring | Mature async API framework with strong typing + production adoption | HIGH |
| Pydantic | 2.12.5 | Data contracts for prompts, model I/O, APIs | Strong validation prevents bad payloads from corrupting model and campaign flows | HIGH |
| PostgreSQL | 17.9 | System of record (campaigns, users, approvals, predictions) | ACID + relational integrity + long support window; ideal for operational campaign workflows | HIGH |
| pgvector (extension) | v0.8.2 | Vector similarity over historical messages/templates | Keep semantic retrieval in Postgres for MVP (avoid premature vector DB sprawl) | MEDIUM-HIGH |
| ClickHouse | v26.2.3.2-stable | High-volume event/performance analytics | Excellent OLAP performance for engagement metrics and cohort analysis | MEDIUM-HIGH |
| Redis | 8.6.1 | Queue/cache/rate-limit store | Reliable low-latency infra for async jobs and API throttling | MEDIUM-HIGH |
| Prefect | 3.6.20 | Workflow orchestration (ingestion, retraining, batch scoring) | Python-native orchestration with low friction; faster setup than heavy Airflow-first setups | HIGH |
| dbt-core | 1.11.7 | Warehouse transformations + semantic data models | Standard analytics-engineering layer for clean, testable campaign metrics | HIGH |
| XGBoost | 3.2.0 | Primary performance prediction model | Strong baseline for tabular engagement/conversion prediction | HIGH |
| scikit-learn | 1.8.0 | Segmentation + baselines + evaluation pipelines | Industry-standard ML utilities for clustering, calibration, and experimentation | HIGH |
| MLflow | 3.10.1 | Experiment tracking/model registry | Keeps model lifecycle controlled as you iterate scoring + generation strategies | HIGH |
| OpenAI SDK | 2.24.0 | Primary generative model provider integration | Fastest route to high-quality copy generation + structured outputs | MEDIUM |
| Anthropic SDK | 0.84.0 | Secondary provider/fallback model path | Redundancy + model diversity for reliability and cost/performance routing | MEDIUM |
| LiteLLM | 1.82.0 | Multi-provider abstraction/routing | Avoid provider lock-in and normalize API semantics across LLM vendors | MEDIUM |
| Twilio Python SDK | 9.10.2 | SMS/WhatsApp delivery integration | Single programmable messaging surface for both channels in MVP | HIGH |

### Supporting Libraries

| Library | Version | Purpose | When to Use | Confidence |
|---------|---------|---------|-------------|------------|
| SQLAlchemy | 2.0.48 | ORM + SQL control for Postgres | Use for transactional app backend; keep analytics SQL in dbt/ClickHouse | HIGH |
| Polars | 1.38.1 | Fast dataframe transforms | Use for offline feature engineering and batch prep | HIGH |
| DuckDB | 1.4.4 | Local analytical compute | Use in dev/CI for reproducible analytics tests without full warehouse | HIGH |
| Great Expectations | 1.14.0 | Data quality checks | Use on ingestion boundaries (schema drift, null spikes, metric validity) | HIGH |
| Evidently | 0.7.20 | Drift/performance monitoring | Use for model decay detection and retrain triggers | HIGH |
| Celery | 5.6.2 | Background task execution | Use if Prefect isn’t ideal for low-latency ad-hoc async tasks | HIGH |
| Feast | 0.60.0 | Feature store | Add only after feature reuse/online-offline consistency becomes painful | MEDIUM |

### Development Tools

| Tool | Purpose | Notes |
|------|---------|-------|
| Poetry | Python dependency management | Lock transitive deps for reproducible ML/API builds |
| Ruff + mypy | Lint + static typing | Catch data-contract and pipeline regressions early |
| pytest | Test suite | Add API, transformation, and model-eval regression tests |
| Docker Compose | Local stack orchestration | Run Postgres + ClickHouse + Redis + API + worker locally |

## Installation (Python-first)

```bash
# Core API + orchestration + ML
pip install fastapi==0.135.1 pydantic==2.12.5 sqlalchemy==2.0.48 prefect==3.6.20 \
  xgboost==3.2.0 scikit-learn==1.8.0 mlflow==3.10.1 redis==7.2.1 celery==5.6.2 \
  openai==2.24.0 anthropic==0.84.0 litellm==1.82.0 twilio==9.10.2 dbt-core==1.11.7

# Data + quality + monitoring
pip install polars==1.38.1 duckdb==1.4.4 great-expectations==1.14.0 evidently==0.7.20

# Optional (scale stage)
pip install feast==0.60.0
```

## Alternatives Considered

| Category | Recommended | Alternative | Why Not (for this project now) |
|----------|-------------|-------------|----------------------------------|
| Workflow orchestration | Prefect 3 | Apache Airflow | Airflow is strong but heavier to operate for greenfield teams needing speed to first value |
| Analytics store | ClickHouse | BigQuery/Snowflake | Great managed options, but higher recurring cost and weaker control for self-hosted/event-heavy workloads |
| Vector retrieval | pgvector in Postgres | Dedicated vector DB (Pinecone/Weaviate) | Extra infra not justified until retrieval scale or latency demands exceed Postgres |
| LLM integration | Multi-provider via LiteLLM | Single-provider direct SDK only | Increases outage and pricing risk; harder future migration |

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| “Fine-tune first” strategy as MVP | Slow, expensive, and risky before you validate prompt+retrieval baseline | Start with prompt + retrieval + scoring model, then selectively fine-tune |
| MongoDB as primary source-of-truth | Campaign + attribution workflows are highly relational and audit-heavy | PostgreSQL for operational integrity |
| Pure LLM ranking for campaign selection | LLMs are weak on calibrated probability vs tabular models | XGBoost/scikit models for scoring, LLM only for generation |
| Building custom message gateway early | Reinvents compliance, deliverability, sender management | Twilio APIs first; optimize infra later |

## Stack Patterns by Variant

**If you need fastest launch (4–8 weeks):**
- Keep Postgres + pgvector only (skip ClickHouse initially)
- Use Prefect + dbt-core + XGBoost + OpenAI SDK
- Add ClickHouse when event volume or dashboard latency becomes a bottleneck

**If you expect high event volume from day one:**
- Use dual-store: Postgres (OLTP) + ClickHouse (OLAP)
- Enforce dbt models for metrics contracts
- Add Evidently monitoring + scheduled retraining from week 1

## Version Compatibility (critical)

| Package | Compatible With | Notes |
|---------|-----------------|-------|
| FastAPI 0.135.1 | Pydantic 2.12.5 | FastAPI is now firmly Pydantic v2-based |
| SQLAlchemy 2.0.48 | Python 3.12+ | Use 2.0 API style only; avoid legacy 1.x patterns |
| Prefect 3.6.20 | Python 3.10–3.14 | Prefer 3.12 for broad package stability |
| XGBoost 3.2.0 | scikit-learn 1.8.0 | Works well for tabular pipelines and calibrated predictors |
| Redis-py 7.2.1 | Redis server 8.x | Keep server/client majors close to reduce protocol surprises |

## Sources

- PostgreSQL version policy + current supported minors: https://www.postgresql.org/support/versioning/ *(HIGH)*
- Prefect v3 docs: https://docs.prefect.io/v3/get-started/index *(HIGH)*
- dbt introduction + version track context: https://docs.getdbt.com/docs/introduction *(HIGH)*
- Twilio Programmable Messaging (SMS + WhatsApp in one API family): https://www.twilio.com/docs/messaging *(HIGH)*
- ClickHouse docs (OLAP positioning): https://clickhouse.com/docs/en/intro *(MEDIUM-HIGH)*
- Anthropic docs overview: https://docs.anthropic.com/en/docs/overview *(HIGH)*
- PyPI JSON metadata for pinned package versions (queried 2026-03-05): https://pypi.org/ *(HIGH)*
- GitHub latest releases/tags for infra components (queried 2026-03-05):
  - ClickHouse: https://github.com/ClickHouse/ClickHouse/releases
  - Redis: https://github.com/redis/redis/releases
  - pgvector: https://github.com/pgvector/pgvector/tags

---
*Stack research for: AI campaign suggestion system*
*Researched: 2026-03-05*
