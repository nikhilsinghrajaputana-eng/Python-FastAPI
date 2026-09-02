"""
Point-in-Time (PIT) Architecture — ECADS-v3 §7, §93

Rule: information_available_at <= historical_decision_timestamp
Never use period_end_date as a proxy for information availability.
"""

from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import Protocol

import polars as pl


class FreshnessStatus(str, Enum):
    CURRENT = "CURRENT"          # <= 7 days
    RECENT = "RECENT"            # 8–30 days
    STALE = "STALE"              # 31–90 days
    VERY_STALE = "VERY_STALE"    # > 90 days


class HasTimestamps(Protocol):
    period_end_date: date
    filing_timestamp: datetime
    information_available_at: datetime


def compute_information_available_at(
    filing_timestamp: datetime | None,
    publication_timestamp: datetime | None = None,
) -> datetime:
    """information_available_at = max(filing_timestamp, publication_timestamp)."""
    candidates = [ts for ts in (filing_timestamp, publication_timestamp) if ts is not None]
    if not candidates:
        raise ValueError("At least filing_timestamp must be provided")
    return max(candidates)


def apply_pit_filter(
    df: pl.DataFrame,
    decision_timestamp: datetime,
    *,
    availability_col: str = "information_available_at",
    filing_col: str = "filing_timestamp",
) -> pl.DataFrame:
    """
    Filter records to those available at or before the decision timestamp.

    If information_available_at is missing, falls back to filing_timestamp.
    """
    if availability_col in df.columns:
        return df.filter(pl.col(availability_col) <= decision_timestamp)
    if filing_col in df.columns:
        return df.filter(pl.col(filing_col) <= decision_timestamp)
    raise ValueError(
        f"PIT filter requires '{availability_col}' or '{filing_col}' column"
    )


def classify_freshness(
    information_available_at: datetime,
    reference_time: datetime | None = None,
) -> tuple[int, FreshnessStatus]:
    """Return (data_age_days, freshness_status)."""
    ref = reference_time or datetime.now(tz=information_available_at.tzinfo)
    age_days = (ref - information_available_at).days

    if age_days <= 7:
        status = FreshnessStatus.CURRENT
    elif age_days <= 30:
        status = FreshnessStatus.RECENT
    elif age_days <= 90:
        status = FreshnessStatus.STALE
    else:
        status = FreshnessStatus.VERY_STALE

    return age_days, status


def latest_available_per_period(
    df: pl.DataFrame,
    decision_timestamp: datetime,
    *,
    group_cols: list[str],
    period_col: str = "period_end_date",
    availability_col: str = "information_available_at",
    filing_col: str = "filing_timestamp",
) -> pl.DataFrame:
    """
    For each group+period, return the latest filing available before decision time.
    Used for backtest feature computation.
    """
    filtered = apply_pit_filter(
        df,
        decision_timestamp,
        availability_col=availability_col,
        filing_col=filing_col,
    )
    avail = availability_col if availability_col in filtered.columns else filing_col
    return (
        filtered.sort(group_cols + [period_col, avail])
        .group_by(group_cols + [period_col])
        .tail(1)
    )
