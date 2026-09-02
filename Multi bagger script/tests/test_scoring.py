"""Tests for scoring orchestrator."""

from ecads.scoring.orchestrator import (
    EarlinessStage,
    StockClassification,
    SubScores,
    _classify_earliness,
    classify_company,
    compute_opportunity_score,
    score_quadrant,
)


def test_opportunity_score_weighted():
    sub = SubScores(fundamental_acceleration=80, revenue_eps_growth=70)
    score = compute_opportunity_score(sub)
    assert 0 <= score <= 100


def test_earliness_classification():
    assert _classify_earliness(85) == EarlinessStage.EARLY
    assert _classify_earliness(55) == EarlinessStage.MID_STAGE
    assert _classify_earliness(10) == EarlinessStage.ALREADY_DISCOVERED


def test_classify_early_accelerator():
    result = classify_company(opportunity=80, earliness=75, risk=20, confidence=85)
    assert result == StockClassification.EARLY_ACCELERATOR


def test_hard_risk_overrides():
    result = classify_company(
        opportunity=95, earliness=90, risk=10, confidence=95, hard_risk_flags=["qualified_audit"]
    )
    assert result == StockClassification.HIGH_RISK


def test_score_quadrant():
    assert score_quadrant(70, 70) == "PRIORITY_RESEARCH"
    assert score_quadrant(70, 30) == "QUALITY_BUT_POSSIBLY_LATE"
    assert score_quadrant(30, 70) == "WATCHLIST"
    assert score_quadrant(30, 30) == "IGNORE"
