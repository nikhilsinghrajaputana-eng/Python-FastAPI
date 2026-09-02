"""FastAPI application — ECADS-v3."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, Query
from pydantic import BaseModel, Field

from ecads import DISCLAIMER, __version__
from ecads.scoring.orchestrator import score_quadrant

app = FastAPI(
    title="ECADS-v3",
    description="Early Compounder & Fundamental Acceleration Discovery System",
    version=__version__,
)


class HealthResponse(BaseModel):
    status: str
    version: str
    phase: str


class ScoreSummary(BaseModel):
    rank: int
    company: str
    ticker: str
    universe: str
    opportunity_score: int
    earliness_score: int
    risk_score: int
    confidence_score: int
    quadrant: str
    classification: str


class Top20Response(BaseModel):
    as_of_date: date
    decision_timestamp: datetime
    candidates: List[ScoreSummary]
    disclaimer: str = Field(default=DISCLAIMER)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", version=__version__, phase="1-universe-master")


@app.get("/api/v1/top20", response_model=Top20Response)
def top20_candidates(
    as_of: Optional[date] = Query(default=None, description="Decision date (PIT cutoff)"),
) -> Top20Response:
    """
    TOP 20 Early Compounder Candidates — §78.

    Phase 1 stub: returns empty list until scoring pipeline (Phase 13) is wired.
    """
    decision = datetime.combine(as_of or date.today(), datetime.max.time())
    return Top20Response(
        as_of_date=as_of or date.today(),
        decision_timestamp=decision,
        candidates=[],
    )


@app.get("/api/v1/score-quadrant")
def get_score_quadrant(
    opportunity: int = Query(ge=0, le=100),
    earliness: int = Query(ge=0, le=100),
) -> Dict[str, Any]:
    """2D Opportunity Matrix quadrant — §82."""
    return {
        "opportunity_score": opportunity,
        "earliness_score": earliness,
        "quadrant": score_quadrant(opportunity, earliness),
    }


@app.get("/disclaimer")
def get_disclaimer() -> Dict[str, str]:
    return {"disclaimer": DISCLAIMER}
