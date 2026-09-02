-- ECADS-v3 Database Schema — Phase 1 Foundation
-- PostgreSQL 16+

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- =============================================================================
-- ENUMS
-- =============================================================================

CREATE TYPE company_status AS ENUM ('ACTIVE', 'DELISTED', 'MERGED', 'SUSPENDED');
CREATE TYPE exchange_type AS ENUM ('NSE', 'BSE', 'BOTH');
CREATE TYPE segment_type AS ENUM ('MAINBOARD', 'SME');
CREATE TYPE security_status AS ENUM ('ACTIVE', 'DELISTED', 'SUSPENDED');
CREATE TYPE universe_type AS ENUM (
    'MAINBOARD', 'SME', 'MICROCAP', 'SMALLCAP', 'MIDCAP',
    'LARGECAP', 'ILLIQUID', 'HIGH_LIQUIDITY'
);
CREATE TYPE report_type AS ENUM ('CONSOLIDATED', 'STANDALONE');
CREATE TYPE source_tier AS ENUM ('TIER1_OFFICIAL', 'TIER2_GOVT', 'TIER3_SECONDARY', 'MODEL');
CREATE TYPE data_status AS ENUM ('ACTUAL', 'ESTIMATED', 'DERIVED', 'MISSING');
CREATE TYPE confidence_level AS ENUM ('HIGH', 'MEDIUM', 'LOW', 'UNVERIFIED');
CREATE TYPE freshness_status AS ENUM ('CURRENT', 'RECENT', 'STALE', 'VERY_STALE');
CREATE TYPE tender_stage AS ENUM (
    'TENDER_PUBLISHED', 'CORRIGENDUM', 'BID_SUBMITTED', 'TECHNICAL_EVALUATION',
    'TECHNICALLY_QUALIFIED', 'FINANCIAL_BID', 'REVERSE_AUCTION', 'L1_PREFERRED',
    'LETTER_OF_INTENT', 'CONTRACT_AWARDED', 'CONTRACT_SIGNED', 'EXECUTION',
    'REVENUE_RECOGNIZED', 'COMPLETED', 'CANCELLED', 'RE_TENDERED'
);
CREATE TYPE earliness_stage AS ENUM (
    'EARLY', 'MID_STAGE', 'LATE_STAGE', 'EXPECTATIONS_HEAVY', 'ALREADY_DISCOVERED'
);
CREATE TYPE stock_classification AS ENUM (
    'EARLY_ACCELERATOR', 'FUNDAMENTAL_BREAKOUT', 'HIGH_QUALITY_COMPOUNDER',
    'GROWTH_CONFIRMED', 'TURNAROUND', 'CATALYST_DRIVEN', 'ORDER_TENDER_CATALYST',
    'OVERVALUED_GROWTH', 'MOMENTUM_ONLY', 'VALUE_TRAP', 'FUNDAMENTAL_DETERIORATION',
    'HIGH_RISK', 'WATCHLIST'
);

-- =============================================================================
-- MASTER DATA
-- =============================================================================

CREATE TABLE companies (
    company_id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name                VARCHAR(500) NOT NULL,
    cin                 VARCHAR(25),
    sector              VARCHAR(100),
    industry            VARCHAR(200),
    incorporation_date  DATE,
    status              company_status NOT NULL DEFAULT 'ACTIVE',
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE securities (
    security_id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id          UUID NOT NULL REFERENCES companies(company_id),
    isin                VARCHAR(12) UNIQUE,
    nse_symbol          VARCHAR(30),
    bse_scrip_code      VARCHAR(20),
    exchange            exchange_type,
    segment             segment_type NOT NULL DEFAULT 'MAINBOARD',
    listing_date        DATE,
    face_value          DECIMAL(12, 4),
    status              security_status NOT NULL DEFAULT 'ACTIVE',
    source              VARCHAR(100),
    source_url          TEXT,
    retrieved_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_securities_company ON securities(company_id);
CREATE INDEX idx_securities_nse ON securities(nse_symbol) WHERE nse_symbol IS NOT NULL;
CREATE INDEX idx_securities_bse ON securities(bse_scrip_code) WHERE bse_scrip_code IS NOT NULL;

CREATE TABLE universe_membership (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    security_id         UUID NOT NULL REFERENCES securities(security_id),
    universe            universe_type NOT NULL,
    effective_from      DATE NOT NULL,
    effective_to        DATE,
    market_cap          DECIMAL(18, 2),
    avg_daily_value     DECIMAL(18, 2),
    source              VARCHAR(100),
    retrieved_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_universe_security ON universe_membership(security_id, effective_from);

CREATE TABLE source_registry (
    source_id           VARCHAR(50) PRIMARY KEY,
    name                VARCHAR(200) NOT NULL,
    tier                SMALLINT NOT NULL CHECK (tier BETWEEN 1 AND 3),
    source_type         source_tier NOT NULL,
    base_url            TEXT,
    terms_url           TEXT,
    rate_limit_rpm      INTEGER,
    robots_respected    BOOLEAN DEFAULT TRUE,
    auth_required       BOOLEAN DEFAULT FALSE,
    license_notes       TEXT,
    last_verified       DATE,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE regulatory_versions (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    regulation_name     VARCHAR(200) NOT NULL,
    version             VARCHAR(50) NOT NULL,
    effective_date      DATE NOT NULL,
    superseded_date     DATE,
    source              VARCHAR(100),
    source_url          TEXT,
    applicable_rule     JSONB NOT NULL DEFAULT '{}',
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_regulatory_active ON regulatory_versions(regulation_name, effective_date)
    WHERE superseded_date IS NULL;

-- =============================================================================
-- MARKET DATA
-- =============================================================================

CREATE TABLE prices (
    id                  BIGSERIAL PRIMARY KEY,
    security_id         UUID NOT NULL REFERENCES securities(security_id),
    trade_date          DATE NOT NULL,
    open                DECIMAL(14, 4),
    high                DECIMAL(14, 4),
    low                 DECIMAL(14, 4),
    close               DECIMAL(14, 4),
    volume              BIGINT,
    value_traded        DECIMAL(18, 2),
    source              VARCHAR(100) NOT NULL,
    source_type         source_tier NOT NULL,
    retrieved_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    information_available_at TIMESTAMPTZ NOT NULL,
    UNIQUE (security_id, trade_date, source)
);

CREATE INDEX idx_prices_security_date ON prices(security_id, trade_date);

CREATE TABLE corporate_actions (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    security_id         UUID NOT NULL REFERENCES securities(security_id),
    action_type         VARCHAR(50) NOT NULL,
    ex_date             DATE,
    record_date         DATE,
    ratio               VARCHAR(50),
    details             JSONB DEFAULT '{}',
    source              VARCHAR(100) NOT NULL,
    filing_timestamp    TIMESTAMPTZ,
    information_available_at TIMESTAMPTZ NOT NULL,
    retrieved_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- =============================================================================
-- FINANCIAL DATA
-- =============================================================================

CREATE TABLE financial_results (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id          UUID NOT NULL REFERENCES companies(company_id),
    security_id         UUID REFERENCES securities(security_id),
    report_type         report_type NOT NULL,
    period              VARCHAR(20) NOT NULL,
    period_end          DATE NOT NULL,
    filing_timestamp    TIMESTAMPTZ NOT NULL,
    information_available_at TIMESTAMPTZ NOT NULL,
    source              VARCHAR(100) NOT NULL,
    source_type         source_tier NOT NULL,
    source_url          TEXT,
    document_id         UUID,
    confidence          confidence_level NOT NULL DEFAULT 'HIGH',
    data_status         data_status NOT NULL DEFAULT 'ACTUAL',
    retrieved_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (company_id, report_type, period_end, filing_timestamp)
);

CREATE INDEX idx_financials_pit ON financial_results(company_id, information_available_at);
CREATE INDEX idx_financials_period ON financial_results(company_id, period_end, report_type);

CREATE TABLE income_statement (
    financial_result_id UUID PRIMARY KEY REFERENCES financial_results(id),
    revenue             DECIMAL(18, 2),
    gross_profit        DECIMAL(18, 2),
    ebitda              DECIMAL(18, 2),
    ebit                DECIMAL(18, 2),
    pat                 DECIMAL(18, 2),
    eps                 DECIMAL(12, 4),
    depreciation        DECIMAL(18, 2),
    interest            DECIMAL(18, 2),
    tax                 DECIMAL(18, 2),
    other_income        DECIMAL(18, 2),
    exceptional_items   DECIMAL(18, 2),
    unit                VARCHAR(20) DEFAULT 'INR_CR'
);

CREATE TABLE balance_sheet (
    financial_result_id UUID PRIMARY KEY REFERENCES financial_results(id),
    cash                DECIMAL(18, 2),
    investments         DECIMAL(18, 2),
    receivables         DECIMAL(18, 2),
    inventory           DECIMAL(18, 2),
    payables            DECIMAL(18, 2),
    gross_debt          DECIMAL(18, 2),
    net_debt            DECIMAL(18, 2),
    working_capital     DECIMAL(18, 2),
    total_assets        DECIMAL(18, 2),
    current_liabilities DECIMAL(18, 2),
    net_worth           DECIMAL(18, 2),
    capital_employed    DECIMAL(18, 2),
    related_party_loans DECIMAL(18, 2),
    unit                VARCHAR(20) DEFAULT 'INR_CR'
);

CREATE TABLE cash_flow (
    financial_result_id UUID PRIMARY KEY REFERENCES financial_results(id),
    cfo                 DECIMAL(18, 2),
    cfi                 DECIMAL(18, 2),
    cff                 DECIMAL(18, 2),
    fcf                 DECIMAL(18, 2),
    capex               DECIMAL(18, 2),
    unit                VARCHAR(20) DEFAULT 'INR_CR'
);

CREATE TABLE ratios (
    financial_result_id UUID PRIMARY KEY REFERENCES financial_results(id),
    roe                 DECIMAL(8, 4),
    roce                DECIMAL(8, 4),
    roic                DECIMAL(8, 4),
    incremental_roce    DECIMAL(8, 4),
    cfcr_4q             DECIMAL(8, 4),
    cfcr_score          SMALLINT,
    cfcr_warning        VARCHAR(20),
    effective_tax_rate  DECIMAL(8, 4),
    tax_reconciliation_status VARCHAR(30),
    debt_to_equity      DECIMAL(8, 4),
    cfo_pat_ratio       DECIMAL(8, 4),
    computed_at         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    model_version       VARCHAR(20)
);

-- =============================================================================
-- OWNERSHIP
-- =============================================================================

CREATE TABLE shareholding (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id          UUID NOT NULL REFERENCES companies(company_id),
    period_end          DATE NOT NULL,
    promoter_pct        DECIMAL(8, 4),
    fii_pct             DECIMAL(8, 4),
    dii_pct             DECIMAL(8, 4),
    public_pct          DECIMAL(8, 4),
    filing_timestamp    TIMESTAMPTZ NOT NULL,
    information_available_at TIMESTAMPTZ NOT NULL,
    source              VARCHAR(100) NOT NULL,
    retrieved_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE promoter_encumbrance (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id          UUID NOT NULL REFERENCES companies(company_id),
    period_end          DATE NOT NULL,
    pledged_pct         DECIMAL(8, 4),
    ndu_pct             DECIMAL(8, 4),
    effective_encumbrance_pct DECIMAL(8, 4),
    filing_timestamp    TIMESTAMPTZ NOT NULL,
    information_available_at TIMESTAMPTZ NOT NULL,
    source              VARCHAR(100) NOT NULL,
    retrieved_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- =============================================================================
-- DOCUMENTS
-- =============================================================================

CREATE TABLE documents (
    document_id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id          UUID REFERENCES companies(company_id),
    document_type       VARCHAR(50) NOT NULL,
    title               VARCHAR(500),
    source              VARCHAR(100) NOT NULL,
    source_url          TEXT,
    filing_timestamp    TIMESTAMPTZ,
    information_available_at TIMESTAMPTZ NOT NULL,
    content_hash        VARCHAR(64),
    retrieved_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE document_extractions (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id         UUID NOT NULL REFERENCES documents(document_id),
    extraction_type     VARCHAR(50) NOT NULL,
    extracted_data      JSONB NOT NULL DEFAULT '{}',
    confidence          confidence_level NOT NULL DEFAULT 'MEDIUM',
    model_version       VARCHAR(20),
    extracted_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE management_guidance (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id          UUID NOT NULL REFERENCES companies(company_id),
    guidance_type       VARCHAR(50) NOT NULL,
    metric              VARCHAR(50),
    guidance_value      DECIMAL(18, 4),
    guidance_text       TEXT,
    period              VARCHAR(20),
    document_id         UUID REFERENCES documents(document_id),
    guidance_date       DATE,
    information_available_at TIMESTAMPTZ NOT NULL,
    source              VARCHAR(100) NOT NULL,
    confidence          confidence_level NOT NULL DEFAULT 'MEDIUM'
);

-- =============================================================================
-- ORDERS & TENDERS
-- =============================================================================

CREATE TABLE orders (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id          UUID NOT NULL REFERENCES companies(company_id),
    order_value         DECIMAL(18, 2),
    order_description   TEXT,
    customer            VARCHAR(200),
    order_date          DATE,
    execution_status    VARCHAR(50),
    source              VARCHAR(100) NOT NULL,
    filing_timestamp    TIMESTAMPTZ,
    information_available_at TIMESTAMPTZ NOT NULL,
    confidence          confidence_level NOT NULL DEFAULT 'HIGH'
);

CREATE TABLE tenders (
    tender_id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    external_tender_id  VARCHAR(100),
    issuer              VARCHAR(300) NOT NULL,
    description         TEXT,
    tender_value        DECIMAL(18, 2),
    currency            VARCHAR(10) DEFAULT 'INR',
    stage               tender_stage NOT NULL DEFAULT 'TENDER_PUBLISHED',
    closing_date        DATE,
    award_status        VARCHAR(50),
    source              VARCHAR(100) NOT NULL,
    source_url          TEXT,
    information_available_at TIMESTAMPTZ NOT NULL,
    confidence          confidence_level NOT NULL DEFAULT 'MEDIUM',
    retrieved_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE tender_company_matches (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tender_id           UUID NOT NULL REFERENCES tenders(tender_id),
    company_id          UUID NOT NULL REFERENCES companies(company_id),
    relevance_score     SMALLINT CHECK (relevance_score BETWEEN 0 AND 100),
    match_reason        JSONB DEFAULT '{}',
    materiality_revenue_pct DECIMAL(8, 4),
    materiality_mcap_pct DECIMAL(8, 4),
    bid_risk            VARCHAR(30),
    bg_stress_factor    DECIMAL(8, 4),
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE tender_awards (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tender_id           UUID NOT NULL REFERENCES tenders(tender_id),
    company_id          UUID REFERENCES companies(company_id),
    award_value         DECIMAL(18, 2),
    award_date          DATE,
    source              VARCHAR(100) NOT NULL,
    source_url          TEXT,
    information_available_at TIMESTAMPTZ NOT NULL,
    confidence          confidence_level NOT NULL DEFAULT 'HIGH'
);

-- =============================================================================
-- EVENTS & CATALYSTS
-- =============================================================================

CREATE TABLE catalysts (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id          UUID NOT NULL REFERENCES companies(company_id),
    event_date          DATE,
    expected_date       DATE,
    catalyst_type       VARCHAR(50) NOT NULL,
    description         TEXT,
    expected_impact     VARCHAR(20),
    probability         DECIMAL(5, 4),
    materiality         VARCHAR(20),
    status              VARCHAR(30) DEFAULT 'UPCOMING',
    source              VARCHAR(100) NOT NULL,
    information_available_at TIMESTAMPTZ NOT NULL,
    confidence          confidence_level NOT NULL DEFAULT 'MEDIUM'
);

CREATE TABLE governance_events (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id          UUID NOT NULL REFERENCES companies(company_id),
    event_type          VARCHAR(50) NOT NULL,
    severity            VARCHAR(20) NOT NULL,
    description         TEXT,
    event_date          DATE,
    source              VARCHAR(100) NOT NULL,
    filing_timestamp    TIMESTAMPTZ,
    information_available_at TIMESTAMPTZ NOT NULL,
    hard_risk_flag      BOOLEAN DEFAULT FALSE
);

-- =============================================================================
-- SCORING
-- =============================================================================

CREATE TABLE scores (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id          UUID NOT NULL REFERENCES companies(company_id),
    as_of_date          DATE NOT NULL,
    opportunity_score   SMALLINT CHECK (opportunity_score BETWEEN 0 AND 100),
    earliness_score     SMALLINT CHECK (earliness_score BETWEEN 0 AND 100),
    risk_score          SMALLINT CHECK (risk_score BETWEEN 0 AND 100),
    confidence_score    SMALLINT CHECK (confidence_score BETWEEN 0 AND 100),
    classification      stock_classification,
    earliness_stage     earliness_stage,
    fundamental_score   SMALLINT,
    growth_score        SMALLINT,
    catalyst_score      SMALLINT,
    market_score        SMALLINT,
    valuation_score     SMALLINT,
    primary_catalyst    TEXT,
    primary_risk        TEXT,
    thesis_invalidation JSONB DEFAULT '[]',
    evidence_quality    confidence_level,
    model_version       VARCHAR(20) NOT NULL DEFAULT '3.0.0',
    historical_decision_timestamp TIMESTAMPTZ NOT NULL,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (company_id, as_of_date, model_version)
);

CREATE INDEX idx_scores_ranking ON scores(as_of_date, opportunity_score DESC, earliness_score DESC);

CREATE TABLE score_history (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id          UUID NOT NULL REFERENCES companies(company_id),
    recorded_at         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    opportunity_score   SMALLINT,
    earliness_score     SMALLINT,
    risk_score          SMALLINT,
    confidence_score    SMALLINT,
    classification      stock_classification,
    score_velocity      DECIMAL(8, 4),
    model_version       VARCHAR(20)
);

CREATE TABLE risk_flags (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id          UUID NOT NULL REFERENCES companies(company_id),
    flag_type           VARCHAR(50) NOT NULL,
    severity            VARCHAR(20) NOT NULL,
    description         TEXT,
    is_hard_gate        BOOLEAN DEFAULT FALSE,
    detected_at         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    information_available_at TIMESTAMPTZ NOT NULL,
    source              VARCHAR(100),
    resolved_at         TIMESTAMPTZ
);

-- =============================================================================
-- ML & BACKTESTING
-- =============================================================================

CREATE TABLE model_versions (
    model_id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    model_name          VARCHAR(100) NOT NULL,
    model_type          VARCHAR(50) NOT NULL,
    target_variable     VARCHAR(50) NOT NULL,
    hyperparameters     JSONB DEFAULT '{}',
    feature_set         JSONB DEFAULT '[]',
    trained_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    train_period_start  DATE,
    train_period_end    DATE,
    metrics             JSONB DEFAULT '{}'
);

CREATE TABLE model_predictions (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id          UUID NOT NULL REFERENCES companies(company_id),
    model_id            UUID NOT NULL REFERENCES model_versions(model_id),
    as_of_date          DATE NOT NULL,
    target              VARCHAR(50) NOT NULL,
    probability         DECIMAL(6, 5),
    top_positive_factors JSONB DEFAULT '[]',
    top_negative_factors JSONB DEFAULT '[]',
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE backtests (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    backtest_name       VARCHAR(200) NOT NULL,
    model_version       VARCHAR(20),
    start_date          DATE NOT NULL,
    end_date            DATE NOT NULL,
    config              JSONB NOT NULL DEFAULT '{}',
    results             JSONB NOT NULL DEFAULT '{}',
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE data_quality (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_type         VARCHAR(50) NOT NULL,
    entity_id           UUID NOT NULL,
    issue_type          VARCHAR(50) NOT NULL,
    severity            VARCHAR(20) NOT NULL,
    description         TEXT,
    detected_at         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    resolved            BOOLEAN DEFAULT FALSE
);

-- =============================================================================
-- SEED: Source Registry
-- =============================================================================

INSERT INTO source_registry (source_id, name, tier, source_type, base_url) VALUES
    ('NSE_ANN', 'NSE Announcements', 1, 'TIER1_OFFICIAL', 'https://www.nseindia.com'),
    ('BSE_ANN', 'BSE Announcements', 1, 'TIER1_OFFICIAL', 'https://www.bseindia.com'),
    ('SEBI_XBRL', 'SEBI XBRL Filings', 1, 'TIER1_OFFICIAL', 'https://www.sebi.gov.in'),
    ('CPPP', 'Central Public Procurement Portal', 2, 'TIER2_GOVT', 'https://eprocure.gov.in'),
    ('GEM', 'Government e-Marketplace', 2, 'TIER2_GOVT', 'https://gem.gov.in'),
    ('SCREENER', 'Screener.in', 3, 'TIER3_SECONDARY', 'https://www.screener.in')
ON CONFLICT (source_id) DO NOTHING;
