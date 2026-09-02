"""Tests for forensic accounting engine."""

from datetime import date, datetime

import polars as pl

from ecads.forensic_engine.engine import CFCRWarning, ForensicAccountingEngine, FinancialSchema


def _build_sample() -> pl.DataFrame:
    return pl.DataFrame(
        {
            FinancialSchema.SECURITY_ID: [1001] * 8,
            FinancialSchema.PERIOD_END_DATE: [
                date(2025, 3, 31), date(2025, 6, 30), date(2025, 9, 30), date(2025, 12, 31),
            ] * 2,
            FinancialSchema.FILING_TIMESTAMP: [
                datetime(2025, 5, 15), datetime(2025, 8, 14),
                datetime(2025, 11, 14), datetime(2026, 2, 14),
            ] * 2,
            FinancialSchema.REPORT_TYPE: ["CONSOLIDATED"] * 4 + ["STANDALONE"] * 4,
            FinancialSchema.REVENUE: [100.0, 120.0, 150.0, 200.0] * 2,
            FinancialSchema.EBITDA: [20.0, 26.0, 35.0, 50.0] * 2,
            FinancialSchema.EBIT: [16.0, 21.0, 29.0, 42.0] * 2,
            FinancialSchema.PAT: [10.0, 14.0, 20.0, 30.0] * 2,
            FinancialSchema.TOTAL_ASSETS: [120.0, 130.0, 150.0, 180.0] * 2,
            FinancialSchema.CURRENT_LIABILITIES: [20.0, 22.0, 25.0, 30.0] * 2,
            FinancialSchema.GROSS_DEBT: [30.0, 28.0, 25.0, 20.0] * 2,
            FinancialSchema.RELATED_PARTY_LOANS: [0.0, 0.0, 0.0, 0.0] * 2,
            FinancialSchema.CFO: [18.0, 22.0, 30.0, 45.0, 15.0, 18.0, 25.0, 38.0],
            FinancialSchema.CAPEX: [5.0] * 8,
        }
    )


def test_forensic_engine_produces_cfcr_score():
    engine = ForensicAccountingEngine(iroce_lookback_quarters=3)
    results = engine.compute_metrics(_build_sample())
    last = results.tail(1)
    assert last["cfcr_4q"][0] is not None
    assert 0 <= last["cfcr_score"][0] <= 100
    assert last["cfcr_warning"][0] in [w.value for w in CFCRWarning]


def test_pit_cutoff_reduces_rows():
    engine = ForensicAccountingEngine()
    full = engine.compute_metrics(_build_sample())
    partial = engine.compute_metrics(_build_sample(), point_in_time_cutoff=datetime(2025, 8, 1))
    assert partial.height < full.height


def test_iroce_not_stable_when_no_capital_deployed():
    engine = ForensicAccountingEngine(iroce_lookback_quarters=1)
    df = pl.DataFrame(
        {
            FinancialSchema.SECURITY_ID: [1, 1],
            FinancialSchema.PERIOD_END_DATE: [date(2025, 6, 30), date(2025, 9, 30)],
            FinancialSchema.FILING_TIMESTAMP: [datetime(2025, 8, 14), datetime(2025, 11, 14)],
            FinancialSchema.REPORT_TYPE: ["CONSOLIDATED", "CONSOLIDATED"],
            FinancialSchema.REVENUE: [100.0, 110.0],
            FinancialSchema.EBITDA: [20.0, 22.0],
            FinancialSchema.EBIT: [16.0, 18.0],
            FinancialSchema.PAT: [10.0, 11.0],
            FinancialSchema.TOTAL_ASSETS: [100.0, 95.0],
            FinancialSchema.CURRENT_LIABILITIES: [20.0, 20.0],
            FinancialSchema.GROSS_DEBT: [10.0, 5.0],
            FinancialSchema.CFO: [15.0, 16.0],
        }
    )
    results = engine.compute_metrics(df)
    assert results["iroce_status"][-1] == "NOT_STABLE"
