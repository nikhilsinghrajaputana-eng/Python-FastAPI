"""Source provenance tracking — ECADS-v3 §6, §92."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from typing import Any


class SourceTier(str, Enum):
    TIER1_OFFICIAL = "TIER1_OFFICIAL"
    TIER2_GOVT = "TIER2_GOVT"
    TIER3_SECONDARY = "TIER3_SECONDARY"
    MODEL = "MODEL"


class DataStatus(str, Enum):
    ACTUAL = "ACTUAL"
    ESTIMATED = "ESTIMATED"
    DERIVED = "DERIVED"
    MISSING = "MISSING"


class Confidence(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    UNVERIFIED = "UNVERIFIED"


@dataclass
class Provenance:
    """Mandatory provenance metadata for every material fact."""

    source: str
    source_type: SourceTier
    source_url: str | None = None
    document_name: str | None = None
    document_date: date | None = None
    published_at: datetime | None = None
    filing_timestamp: datetime | None = None
    retrieved_at: datetime = field(default_factory=datetime.utcnow)
    page_section: str | None = None
    reporting_period: str | None = None
    period_end_date: date | None = None
    company_id: str | None = None
    security_id: str | None = None
    confidence: Confidence = Confidence.HIGH
    data_status: DataStatus = DataStatus.ACTUAL

    @property
    def information_available_at(self) -> datetime | None:
        candidates = [ts for ts in (self.filing_timestamp, self.published_at) if ts]
        return max(candidates) if candidates else None

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "source_type": self.source_type.value,
            "source_url": self.source_url,
            "document_name": self.document_name,
            "document_date": self.document_date.isoformat() if self.document_date else None,
            "published_at": self.published_at.isoformat() if self.published_at else None,
            "filing_timestamp": self.filing_timestamp.isoformat() if self.filing_timestamp else None,
            "retrieved_at": self.retrieved_at.isoformat(),
            "page_section": self.page_section,
            "reporting_period": self.reporting_period,
            "period_end_date": self.period_end_date.isoformat() if self.period_end_date else None,
            "company_id": self.company_id,
            "security_id": self.security_id,
            "confidence": self.confidence.value,
            "data_status": self.data_status.value,
            "information_available_at": (
                self.information_available_at.isoformat()
                if self.information_available_at
                else None
            ),
        }


@dataclass
class EvidenceClaim:
    """Research evidence graph node — §76."""

    claim: str
    evidence: str
    provenance: Provenance

    def to_dict(self) -> dict[str, Any]:
        return {
            "claim": self.claim,
            "evidence": self.evidence,
            **self.provenance.to_dict(),
        }
