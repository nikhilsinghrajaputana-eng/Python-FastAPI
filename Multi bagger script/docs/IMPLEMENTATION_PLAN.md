# ECADS-v3 Phase-by-Phase Implementation Plan

Per specification §95 — build incrementally, validate each phase before proceeding.

---

## Phase Overview

| Phase | Name | Deliverables | Status |
|-------|------|--------------|--------|
| 1 | Universe + Securities Master | DB schema, companies/securities tables, universe tagging | **IN PROGRESS** |
| 2 | Official Data Ingestion | NSE/BSE connectors, announcement parser | Planned |
| 3 | Database + PIT Architecture | PIT engine, provenance mixin, ingestion timestamps | **Partial (core built)** |
| 4 | Fundamental Engine | GAI, growth velocity, EPS inflection | Planned |
| 5 | Cash Flow + Forensic Engine | CFCR (sector-benchmarked), divergence, tax forensics | **Partial (v2 ported)** |
| 6 | Order Book Engine | Order inflow, book-to-bill, execution rate | Planned |
| 7 | Tender/Procurement Engine | Tender radar, state machine, company matching | Planned |
| 8 | Corporate Action/Restructuring | Splits, demergers, pro-forma views | Planned |
| 9 | Management/Document AI | Guidance extraction, credibility scoring | Planned |
| 10 | Valuation + Expectations Gap | Percentile valuation, expectations gap | Planned |
| 11 | Market Confirmation | Relative strength, liquidity, DMA structure | Planned |
| 12 | Risk/Governance | Hard risk gates, governance score | Planned |
| 13 | Scoring | 4-dimension scoring orchestrator | Planned |
| 14 | Historical Winner/Failure Research | Labeled outcome databases | Planned |
| 15 | Backtesting | Walk-forward, transaction costs | Planned |
| 16 | Walk-Forward Validation | Rolling train/validate/test | Planned |
| 17 | ML | Rule-based → XGBoost/LightGBM | Planned |
| 18 | Dashboard | React/Next.js modules | Planned |
| 19 | Alerts | Thesis invalidation, score movers | Planned |
| 20 | Production Deployment | Docker prod, monitoring, CI/CD | Planned |

---

## Phase 1 — Universe + Securities Master (Current)

### WHAT
Canonical registry of all Indian listed companies and securities with universe classification.

### WHY
Every downstream engine requires stable `company_id` / `security_id` mapping across NSE, BSE, ISIN.

### HOW
- PostgreSQL tables: `companies`, `securities`, `universe_membership`
- Seed from NSE/BSE symbol master (CSV/API when available)
- Tag: MAINBOARD, SME, MICROCAP, SMALLCAP, MIDCAP, LARGECAP

### DATA SOURCE
- NSE symbol list (Equity + SME)
- BSE listed companies
- Manual override CSV for corrections

### VALIDATION
- No duplicate ISIN per active security
- Every security maps to exactly one company
- Universe tags mutually consistent with market cap bands

### FAILURE MODE
- Delisted securities → `status = DELISTED`, retained for survivorship
- Ticker changes → `corporate_actions` + alias table

---

## Phase 2 — Official Data Ingestion

### WHAT
Automated ingestion of exchange filings, results, shareholding.

### WHY
Tier 1 sources are authoritative; all facts must trace here.

### HOW
- Celery tasks per source
- Raw document storage → parse → normalize
- Provenance on every field

### DATA SOURCE
NSE/BSE APIs, company IR, SEBI XBRL

### VALIDATION
- Filing timestamp preserved from exchange metadata
- Duplicate filing detection via content hash

### FAILURE MODE
- Rate limits → exponential backoff
- Parse failure → quarantine in `data_quality`

---

## Phase 3 — Database + PIT Architecture

### WHAT
Enforce `information_available_at <= decision_timestamp` everywhere.

### WHY
Reproducibility and backtest integrity (§93).

### HOW
- `ecads/core/pit.py` — filter functions
- DB constraints + indexes on timestamp columns
- All engine entry points accept `as_of: datetime`

### VALIDATION
- Unit tests: Dec-2025 result excluded before Feb-2026 filing date
- Backtest replay produces identical scores

---

## Phase 4 — Fundamental Engine

### WHAT
GAI, growth acceleration, margin expansion, ROCE improvement.

### ALGORITHM
- Rolling YoY/QoQ growth → velocity → acceleration (standardized z-score)
- Handle negative earnings, denominator instability

### VALIDATION
- Cupid-like case study replay (historical, PIT-correct)
- Compare winner vs failure precursor distributions

---

## Phase 5 — Cash Flow + Forensic Engine

### WHAT
CFCR (sector-benchmarked), parent-subs divergence, tax reconciliation.

### ALGORITHM
- No universal 0.60 CFCR threshold
- CFCR_SCORE vs sector/history/business model
- Cash Flow Divergence Indicator (not "leakage proof")

### VALIDATION
- Known accounting failure cases flag correctly
- False positive rate on clean compounders

---

## Phase 6 — Order Book Engine

### WHAT
Order book growth, book-to-bill, execution rate, concentration.

### DATA SOURCE
Reg 30 disclosures, investor presentations, exchange announcements

---

## Phase 7 — Tender/Procurement Engine

### WHAT
Tender Radar with 16-state machine, NLP company matching, materiality.

### SAFETY
Never "will win" — only "potentially relevant"

### DATA SOURCE
CPPP, GeM, state eProcurement, exchange contract announcements

---

## Phase 8–12 — Supporting Engines

Each engine follows template:
1. Define input schema
2. PIT-filter inputs
3. Compute features with provenance
4. Write to feature tables
5. Unit tests + integration tests

---

## Phase 13 — Scoring

### WHAT
Opportunity, Earliness, Risk, Confidence orchestrator.

### HOW
- Configurable weights (`config/scoring_weights.yaml`)
- Sector overrides
- Hard risk gates before final rank

### OUTPUT
Daily TOP-20, classifications, 2D matrix coordinates

---

## Phase 14 — Winner/Failure Databases

### WHAT
Labeled historical outcomes for ML and pattern research.

### LABELS
Winners: 2x/3x/5x/10x/20x+ | Failures: value trap, fraud, failed turnaround, etc.

### SURVIVORSHIP
Include delisted, suspended, merged entities

---

## Phase 15–16 — Backtesting + Walk-Forward

### WHAT
Validate score buckets predict forward returns.

### METRICS
CAGR, Sharpe, Sortino, FP/FN, calibration by bucket (90-100, 80-89, ...)

### TRANSACTION COSTS
Mandatory for SME/microcap

---

## Phase 17 — ML

### ORDER
Rules → Logistic Regression → RF → XGBoost/LightGBM

### TARGETS
P(excess return > threshold) at 12M/24M/36M

### EXPLAINABILITY
SHAP + top factors per prediction

---

## Phase 18 — Dashboard

React/Next.js with modules per §81. Plotly charts. Role-based access.

---

## Phase 19 — Alerts

Thesis invalidation triggers, score movers, new tender matches, governance events.

---

## Phase 20 — Production

Docker prod stack, CI/CD, monitoring, structured logging, backup strategy.

---

## Immediate Next Steps (Post Phase 1)

1. Run `docker-compose up` to start PostgreSQL + Redis
2. Apply schema: `psql -f ecads/db/schema.sql`
3. Seed securities master from NSE CSV
4. Begin Phase 2 ingestion connector for NSE announcements
5. Wire fundamental engine to PIT-filtered financials
