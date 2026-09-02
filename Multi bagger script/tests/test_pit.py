"""Tests for point-in-time architecture."""

from datetime import date, datetime

import polars as pl
import pytest

from ecads.core.pit import (
    FreshnessStatus,
    apply_pit_filter,
    classify_freshness,
    compute_information_available_at,
    latest_available_per_period,
)


def test_compute_information_available_at():
    filing = datetime(2026, 2, 14, 18, 32)
    pub = datetime(2026, 2, 15, 9, 0)
    assert compute_information_available_at(filing) == filing
    assert compute_information_available_at(filing, pub) == pub


def test_pit_filter_excludes_future_filings():
    df = pl.DataFrame(
        {
            "period_end_date": [date(2025, 12, 31), date(2025, 12, 31)],
            "filing_timestamp": [
                datetime(2026, 2, 14, 18, 32),
                datetime(2026, 3, 1, 10, 0),
            ],
            "information_available_at": [
                datetime(2026, 2, 14, 18, 32),
                datetime(2026, 3, 1, 10, 0),
            ],
            "pat": [100.0, 110.0],
        }
    )
    decision = datetime(2026, 2, 15, 0, 0)
    filtered = apply_pit_filter(df, decision)
    assert filtered.height == 1
    assert filtered["pat"][0] == 100.0


def test_dec_2025_result_not_available_on_dec_2025():
    """§7 example: period 31-Dec-2025 filed 14-Feb-2026 excluded before filing."""
    df = pl.DataFrame(
        {
            "period_end_date": [date(2025, 12, 31)],
            "filing_timestamp": [datetime(2026, 2, 14, 18, 32)],
            "information_available_at": [datetime(2026, 2, 14, 18, 32)],
            "revenue": [1000.0],
        }
    )
    assert apply_pit_filter(df, datetime(2025, 12, 31)).height == 0
    assert apply_pit_filter(df, datetime(2026, 2, 15)).height == 1


def test_classify_freshness():
    info_at = datetime(2026, 8, 1)
    ref = datetime(2026, 8, 5)
    age, status = classify_freshness(info_at, ref)
    assert age == 4
    assert status == FreshnessStatus.CURRENT


def test_latest_available_per_period():
    df = pl.DataFrame(
        {
            "security_id": [1, 1, 1],
            "period_end_date": [date(2025, 3, 31)] * 3,
            "filing_timestamp": [
                datetime(2025, 5, 15),
                datetime(2025, 5, 20),
                datetime(2025, 6, 1),
            ],
            "information_available_at": [
                datetime(2025, 5, 15),
                datetime(2025, 5, 20),
                datetime(2025, 6, 1),
            ],
            "pat": [10.0, 10.5, 11.0],
        }
    )
    result = latest_available_per_period(
        df,
        datetime(2025, 5, 25),
        group_cols=["security_id"],
    )
    assert result.height == 1
    assert result["pat"][0] == 10.5
