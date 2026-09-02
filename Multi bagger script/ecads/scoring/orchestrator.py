"""Multi-dimensional scoring orchestrator — ECADS-v3 §50–56."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from ecads.core.config import get_scoring_weights


class EarlinessStage(str, Enum):
    EARLY = "EARLY"
    MID_STAGE = "MID_STAGE"
    LATE_STAGE = "LATE_STAGE"
    EXPECTATIONS_HEAVY = "EXPECTATIONS_HEAVY"
    ALREADY_DISCOVERED = "ALREADY_DISCOVERED"


class StockClassification(str, Enum):
    EARLY_ACCELERATOR = "EARLY_ACCELERATOR"
    FUNDAMENTAL_BREAKOUT = "FUNDAMENTAL_BREAKOUT"
    HIGH_QUALITY_COMPOUNDER = "HIGH_QUALITY_COMPOUNDER"
    WATCHLIST = "WATCHLIST"
    VALUE_TRAP = "VALUE_TRAP"
    HIGH_RISK = "HIGH_RISK"


@dataclass
class SubScores:
    fundamental_acceleration: float = 0.0
    revenue_eps_growth: float = 0.0
    earnings_quality: float = 0.0
    margins_roce_roic: float = 0.0
    cashflow_balance_sheet: float = 0.0
    business_transformation: float = 0.0
    order_book_inflow: float = 0.0
    tender_procurement_catalyst: float = 0.0
    management_credibility: float = 0.0
    market_confirmation: float = 0.0
    ownership_confirmation: float = 0.0
    valuation_expectations_gap: float = 0.0
    rerating_potential: float = 0.0
    sector_opportunity: float = 0.0


@dataclass
class CompanyScore:
    company_id: str
    opportunity_score: int
    earliness_score: int
    risk_score: int
    confidence_score: int
    classification: StockClassification
    earliness_stage: EarlinessStage
    sub_scores: SubScores = field(default_factory=SubScores)
    primary_catalyst: str | None = None
    primary_risk: str | None = None
    thesis_invalidation: list[str] = field(default_factory=list)
    hard_risk_flags: list[str] = field(default_factory=list)


def _classify_earliness(score: int) -> EarlinessStage:
    if score >= 70:
        return EarlinessStage.EARLY
    if score >= 50:
        return EarlinessStage.MID_STAGE
    if score >= 30:
        return EarlinessStage.LATE_STAGE
    if score >= 15:
        return EarlinessStage.EXPECTATIONS_HEAVY
    return EarlinessStage.ALREADY_DISCOVERED


def compute_opportunity_score(sub: SubScores, weights: dict[str, float] | None = None) -> int:
    w = weights or get_scoring_weights()
    total_weight = sum(w.values()) or 100.0
    weighted = (
        sub.fundamental_acceleration * w.get("fundamental_acceleration", 15)
        + sub.revenue_eps_growth * w.get("revenue_eps_growth", 10)
        + sub.earnings_quality * w.get("earnings_quality", 8)
        + sub.margins_roce_roic * w.get("margins_roce_roic", 8)
        + sub.cashflow_balance_sheet * w.get("cashflow_balance_sheet", 8)
        + sub.business_transformation * w.get("business_transformation", 8)
        + sub.order_book_inflow * w.get("order_book_inflow", 6)
        + sub.tender_procurement_catalyst * w.get("tender_procurement_catalyst", 5)
        + sub.management_credibility * w.get("management_credibility", 5)
        + sub.market_confirmation * w.get("market_confirmation", 5)
        + sub.ownership_confirmation * w.get("ownership_confirmation", 3)
        + sub.valuation_expectations_gap * w.get("valuation_expectations_gap", 10)
        + sub.rerating_potential * w.get("rerating_potential", 5)
        + sub.sector_opportunity * w.get("sector_opportunity", 4)
    )
    return int(min(100, max(0, weighted / total_weight)))


def classify_company(
    opportunity: int,
    earliness: int,
    risk: int,
    confidence: int,
    hard_risk_flags: list[str] | None = None,
) -> StockClassification:
    if hard_risk_flags:
        return StockClassification.HIGH_RISK
    if opportunity >= 75 and earliness >= 65 and risk <= 35:
        return StockClassification.EARLY_ACCELERATOR
    if opportunity >= 70 and earliness >= 45:
        return StockClassification.FUNDAMENTAL_BREAKOUT
    if opportunity >= 65 and risk <= 25:
        return StockClassification.HIGH_QUALITY_COMPOUNDER
    if opportunity >= 50 and earliness >= 60:
        return StockClassification.WATCHLIST
    if opportunity >= 60 and earliness < 25 and risk >= 50:
        return StockClassification.VALUE_TRAP
    return StockClassification.WATCHLIST


def score_quadrant(opportunity: int, earliness: int) -> str:
    high_opp = opportunity >= 60
    high_early = earliness >= 60
    if high_opp and high_early:
        return "PRIORITY_RESEARCH"
    if high_opp and not high_early:
        return "QUALITY_BUT_POSSIBLY_LATE"
    if not high_opp and high_early:
        return "WATCHLIST"
    return "IGNORE"
