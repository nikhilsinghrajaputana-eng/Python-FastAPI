# ECADS-v3 — Early Compounder & Fundamental Acceleration Discovery System

Production-grade Indian equity research engine for identifying fundamental acceleration **before** broad market recognition.

## What This Is

- A **quantitative research and screening system**
- Point-in-time, evidence-traceable, forensic-aware
- Multi-dimensional scoring (Opportunity × Earliness × Risk × Confidence)

## What This Is NOT

- Not investment advice
- Not a price prediction machine
- Not a "guaranteed multibagger" finder

## Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose (for PostgreSQL + Redis)

### Setup

```bash
# Create virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt

# Start infrastructure
docker-compose up -d

# Apply database schema
psql postgresql://ecads:ecads@localhost:5432/ecads -f ecads/db/schema.sql

# Run tests
pytest tests/ -v
```

### Run Forensic Engine (smoke test)

```bash
python -m ecads.forensic_engine.engine
```

### Start API (Phase 1 stub)

```bash
uvicorn ecads.api.main:app --reload --port 8000
```

## Project Structure

```
ecads-v3/
├── docs/                  # Architecture, ER, features, implementation plan
├── config/                # Settings, scoring weights
├── ecads/
│   ├── core/              # PIT engine, provenance, config
│   ├── db/                # SQL schema, models
│   ├── ingestion/         # Data connectors (Phase 2+)
│   ├── fundamental_engine/
│   ├── forensic_engine/   # CFCR, divergence, iROCE
│   ├── scoring/
│   └── api/               # FastAPI
├── tests/
├── docker-compose.yml
└── requirements.txt
```

## Documentation

| Document | Description |
|----------|-------------|
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | Full system architecture (16 deliverables) |
| [IMPLEMENTATION_PLAN.md](docs/IMPLEMENTATION_PLAN.md) | 20-phase build plan |
| [DATABASE_ER.md](docs/DATABASE_ER.md) | Entity-relationship design |
| [DATA_SOURCES.md](docs/DATA_SOURCES.md) | Source map & priority hierarchy |
| [FEATURE_DICTIONARY.md](docs/FEATURE_DICTIONARY.md) | All computed features |

## Current Phase

**Phase 1** — Universe + Securities Master (in progress)

## Disclaimer

> This is a quantitative research and screening system. Historical patterns do not guarantee future returns. Scores are model estimates based on available information and are not investment advice. Tender opportunities, management guidance and business catalysts may not convert into realized revenue or earnings.
