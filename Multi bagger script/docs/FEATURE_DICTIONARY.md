# ECADS-v3 Feature Dictionary

All features are computed point-in-time unless noted. Status values: `ACTUAL`, `ESTIMATED`, `DERIVED`, `MISSING`.

---

## A. Fundamental Acceleration Features

| Feature ID | Name | Formula / Logic | Engine | Range |
|------------|------|-----------------|--------|-------|
| F001 | revenue_growth_yoy | (Rev_t - Rev_t-4) / Rev_t-4 | fundamental | % |
| F002 | revenue_growth_qoq | QoQ sequential | fundamental | % |
| F003 | ebitda_growth_yoy | YoY EBITDA growth | fundamental | % |
| F004 | pat_growth_yoy | YoY PAT growth | fundamental | % |
| F005 | eps_growth_yoy | YoY EPS growth | fundamental | % or UNSTABLE |
| F006 | margin_expansion | EBITDA margin Δ vs prior year | fundamental | bps |
| F007 | gai_revenue | Standardized Δ in revenue growth rate | fundamental | z-score |
| F008 | gai_ebitda | Standardized Δ in EBITDA growth | fundamental | z-score |
| F009 | gai_pat | Standardized Δ in PAT growth | fundamental | z-score |
| F010 | growth_velocity | Rate of change of growth | fundamental | derived |
| F011 | growth_persistence | Quarters of consecutive acceleration | fundamental | count |
| F012 | growth_breadth | # of metrics accelerating | fundamental | 0–N |
| F013 | earnings_inflection_state | TURNAROUND/ACCELERATION/STABLE/DECEL | fundamental | enum |

---

## B. Capital Efficiency Features

| Feature ID | Name | Formula / Logic | Engine | Range |
|------------|------|-----------------|--------|-------|
| F020 | roce | EBIT / Capital Employed | capital | % |
| F021 | roic | NOPAT / Invested Capital | capital | % |
| F022 | iroce | ΔEBIT / ΔCapital Employed | capital | % or NOT_STABLE |
| F023 | iroic | ΔNOPAT / ΔInvested Capital | capital | % or NOT_STABLE |
| F024 | asset_turnover | Revenue / Avg Assets | capital | ratio |
| F025 | wc_efficiency | Working capital / Revenue | capital | ratio |
| F026 | capex_intensity | Capex / Revenue | capital | % |
| F027 | fcf_conversion | FCF / PAT | capital | ratio |

---

## C. Cash Flow & Forensic Features

| Feature ID | Name | Formula / Logic | Engine | Range |
|------------|------|-----------------|--------|-------|
| F030 | cfcr_4q | Rolling 4Q CFO / Rolling 4Q EBITDA | forensic | ratio |
| F031 | cfcr_pat_4q | Rolling 4Q CFO / Rolling 4Q PAT | forensic | ratio |
| F032 | cfcr_score | Sector/history benchmarked CFCR | forensic | 0–100 |
| F033 | cfcr_warning | LOW/MEDIUM/HIGH/NONE | forensic | enum |
| F034 | cfo_pat_ratio | CFO / PAT | forensic | ratio |
| F035 | cash_divergence_indicator | (Cons CFO - Stand CFO) / Cons PAT | forensic | ratio |
| F036 | standalone_debt_concentration | Standalone debt / Consolidated debt | forensic | ratio |
| F037 | rp_exposure_ratio | Related party loans / Standalone CE | forensic | ratio |
| F038 | receivables_growth_vs_revenue | Recv growth - Rev growth | forensic | % |
| F039 | inventory_growth_vs_revenue | Inv growth - Rev growth | forensic | % |
| F040 | effective_tax_rate | Tax / PBT | forensic | % |
| F041 | tax_reconciliation_status | NORMAL/EXPLAINED/UNEXPLAINED/HIGH_RISK | forensic | enum |

---

## D. Business Transformation Features

| Feature ID | Name | Source | Engine | Range |
|------------|------|--------|--------|-------|
| F050 | new_product_signal | Document NLP | transformation | bool + confidence |
| F051 | export_expansion_signal | Filings | transformation | bool |
| F052 | capacity_expansion_signal | Filings | capacity | bool |
| F053 | capacity_utilization | Production / Installed capacity | capacity | % |
| F054 | capacity_not_in_revenue | New capacity commissioned, revenue lag | capacity | bool |
| F055 | new_geography_signal | Filings | transformation | bool |
| F056 | acquisition_signal | Exchange announcements | restructuring | bool |

---

## E. Order Book Features

| Feature ID | Name | Formula | Engine | Range |
|------------|------|---------|--------|-------|
| F060 | order_book | Disclosed order book value | order | INR Cr |
| F061 | order_book_growth | YoY order book growth | order | % |
| F062 | order_book_to_revenue | Order book / TTM revenue | order | ratio |
| F063 | book_to_bill | Orders / Revenue | order | ratio |
| F064 | order_execution_rate | Executed / Total orders | order | % |
| F065 | customer_concentration | Top customer % | order | % |

---

## F. Tender / Procurement Features

| Feature ID | Name | Logic | Engine | Range |
|------------|------|-------|--------|-------|
| F070 | tender_relevance_score | NLP + eligibility match | tender | 0–100 |
| F071 | tender_materiality_revenue | Tender value / Revenue | tender | ratio |
| F072 | tender_materiality_mcap | Tender value / Market cap | tender | ratio |
| F073 | tender_stage | State machine position | tender | enum (16) |
| F074 | reverse_auction_margin_risk | Flag if RA/L1 bidding | tender | bool |
| F075 | bg_stress_factor | BG requirement vs debt capacity | tender | ratio or NULL |
| F076 | bid_execution_credibility | Historical bid success rate | tender | 0–100 |

---

## G. Management & Governance Features

| Feature ID | Name | Logic | Engine | Range |
|------------|------|-------|--------|-------|
| F080 | management_credibility_score | Guidance vs actual history | management | 0–100 |
| F081 | guidance_accuracy_revenue | Revenue guidance accuracy | management | % |
| F082 | governance_score | Composite governance | governance | 0–100 |
| F083 | hard_governance_flag | Serious governance issue | governance | bool |
| F084 | promoter_encumbrance_effective | (Pledge + NDU) / Promoter shares | ownership | % |
| F085 | institutional_accumulation_score | FII/DII/MF trend | ownership | 0–100 |

---

## H. Valuation & Expectations Features

| Feature ID | Name | Formula | Engine | Range |
|------------|------|---------|--------|-------|
| F090 | pe_trailing | Price / TTM EPS | valuation | ratio |
| F091 | pe_forward | Price / Forward EPS | valuation | ratio |
| F092 | ev_ebitda | EV / TTM EBITDA | valuation | ratio |
| F093 | valuation_percentile_hist | Historical P/E percentile | valuation | 0–100 |
| F094 | valuation_percentile_sector | Sector-relative percentile | valuation | 0–100 |
| F095 | expectations_gap_score | Business improvement vs embedded expectations | expectations | 0–100 |
| F096 | earnings_surprise_eps | Actual - Estimate EPS | expectations | absolute |
| F097 | rerating_potential_score | Earnings compounding vs multiple expansion | valuation | 0–100 |

---

## I. Market Confirmation Features

| Feature ID | Name | Logic | Engine | Range |
|------------|------|-------|--------|-------|
| F100 | return_1m | 1-month return | market | % |
| F101 | return_3m | 3-month return | market | % |
| F102 | relative_strength_nifty | vs NIFTY 50 | market | ratio |
| F103 | relative_strength_sector | vs sector index | market | ratio |
| F104 | distance_from_52w_high | (High - Price) / High | market | % |
| F105 | dma_structure | Higher-high/higher-low classification | market | enum |
| F106 | liquidity_score | ADV, spread, impact cost | market | 0–100 |
| F107 | volume_vs_avg | Volume / 20d avg volume | market | ratio |

---

## J. Scoring Features (Composite)

| Feature ID | Name | Components | Range |
|------------|------|------------|-------|
| S001 | opportunity_score | Weighted sub-scores §51 | 0–100 |
| S002 | earliness_score | §4 inputs | 0–100 |
| S003 | risk_score | §52 inputs (higher = more risk) | 0–100 |
| S004 | confidence_score | §54 inputs | 0–100 |
| S005 | earliness_stage | EARLY/MID/LATE/EXPECTATIONS_HEAVY/DISCOVERED | enum |
| S006 | classification | §56 labels | enum |
| S007 | score_velocity | Δ score / Δ time | float |
| S008 | score_acceleration | Δ velocity | float |

---

## K. ML Features (Phase 17)

Subset of above used as model inputs. Target variables:

| Target | Definition |
|--------|------------|
| T001 | 12M excess return > 20% |
| T002 | 12M excess return > 50% |
| T003 | 24M excess return > 50% |
| T004 | 24M excess return > 100% |
| T005 | 36M excess return > 100% |

All outputs labeled MODEL ESTIMATE with calibration metrics.

---

## L. Data Quality Features

| Feature ID | Name | Logic |
|------------|------|-------|
| Q001 | data_age_days | now - information_available_at |
| Q002 | data_freshness_status | CURRENT/RECENT/STALE/VERY_STALE |
| Q003 | missing_quarters_count | Gaps in financial history |
| Q004 | source_conflict_flag | Tier disagreement detected |
| Q005 | consolidated_standalone_mismatch | Structural inconsistency |
