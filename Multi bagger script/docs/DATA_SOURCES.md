# ECADS-v3 Data Source Map

## Tier 1 — Primary Official Sources (Authoritative)

| Source ID | Name | Data Types | URL Pattern | Update Freq | Connector Phase |
|-----------|------|------------|-------------|-------------|-----------------|
| NSE_ANN | NSE Announcements | Results, orders, contracts, Reg 30 events | nseindia.com | Real-time (market hrs) | Phase 2 |
| NSE_CORP | NSE Corporate Filings | Annual reports, presentations | nseindia.com | Event-driven | Phase 2 |
| BSE_ANN | BSE Announcements | Same as NSE | bseindia.com | Real-time | Phase 2 |
| SEBI_XBRL | SEBI XBRL Filings | Structured financials | sebi.gov.in | Event-driven | Phase 2 |
| SEBI_ACTION | SEBI Orders/Actions | Regulatory actions | sebi.gov.in | Event-driven | Phase 12 |
| CO_IR | Company IR Websites | Presentations, transcripts | Per company | Event-driven | Phase 9 |
| EXCHANGE_SH | Exchange Shareholding | Quarterly shareholding | NSE/BSE | Quarterly | Phase 2 |

## Tier 2 — Government / Procurement Sources

| Source ID | Name | Data Types | Connector Phase |
|-----------|------|------------|-----------------|
| CPPP | Central Public Procurement Portal | Central govt tenders | Phase 7 |
| GEM | Government e-Marketplace | GeM tenders/orders | Phase 7 |
| EPROC_STATE | State eProcurement | State tenders | Phase 7 |
| RAILWAY | Railway Procurement | Rail tenders | Phase 7 |
| DEFENCE | Defence Procurement | Defence tenders | Phase 7 |
| PSU_PROC | PSU Portals | PSU-specific tenders | Phase 7 |

## Tier 3 — Secondary Financial (Discovery / Cross-Check Only)

| Source ID | Name | Use Case | Precedence |
|-----------|------|----------|------------|
| SCREENER | Screener.in | Discovery, ratio cross-check | Tier 1 wins |
| TRENDLYNE | Trendlyne | Estimates, ownership | Tier 1 wins |
| TIJORI | Tijori Finance | Historical financials | Tier 1 wins |
| MONEYCONTROL | Moneycontrol | News, estimates | Tier 1 wins |
| TRADINGVIEW | TradingView | Price charts | Tier 1 for prices |
| STOCKEDGE | StockEdge | Technical, ownership | Tier 1 wins |

## Source Registry Schema

Stored in `source_registry` table:

```yaml
source_id: NSE_ANN
name: NSE Announcements
tier: 1
source_type: TIER1_OFFICIAL
base_url: https://www.nseindia.com
terms_url: https://www.nseindia.com/nse-security-policy
rate_limit_rpm: 30
robots_respected: true
auth_required: false
license: Public regulatory disclosure
last_verified: 2026-08-18
```

## Conflict Resolution Matrix

| Scenario | Resolution |
|----------|------------|
| Tier 1 vs Tier 3 value mismatch | Use Tier 1; log SOURCE CONFLICT |
| Tier 1 vs Tier 1 mismatch | Flag UNVERIFIED; retain both |
| Tier 2 tender vs company claim | Tier 2 award doc wins over management claim |
| Missing Tier 1 | Use Tier 3 with confidence=LOW, label UNVERIFIED |
| No data anywhere | DATA NOT AVAILABLE |

## Data Freshness Thresholds

| Status | Age | Action |
|--------|-----|--------|
| CURRENT | ≤ 7 days | Full confidence |
| RECENT | 8–30 days | Normal use |
| STALE | 31–90 days | Reduce confidence; flag in output |
| VERY_STALE | > 90 days | Do not use for high-confidence conclusions |

## Security & Compliance (§94)

- Respect robots.txt and rate limits
- No CAPTCHA bypass
- No paywall bypass
- Use official APIs where available
- Licensed datasets for production price feeds where required
