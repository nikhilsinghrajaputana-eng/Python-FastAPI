"""Securities master and universe management — Phase 1."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import Any
from uuid import UUID, uuid4


class Segment(str, Enum):
    MAINBOARD = "MAINBOARD"
    SME = "SME"


class Universe(str, Enum):
    MAINBOARD = "MAINBOARD"
    SME = "SME"
    MICROCAP = "MICROCAP"
    SMALLCAP = "SMALLCAP"
    MIDCAP = "MIDCAP"
    LARGECAP = "LARGECAP"
    ILLIQUID = "ILLIQUID"
    HIGH_LIQUIDITY = "HIGH_LIQUIDITY"


@dataclass
class Company:
    company_id: UUID
    name: str
    cin: str | None = None
    sector: str | None = None
    industry: str | None = None
    status: str = "ACTIVE"


@dataclass
class Security:
    security_id: UUID
    company_id: UUID
    isin: str | None
    nse_symbol: str | None
    bse_scrip_code: str | None
    segment: Segment
    listing_date: date | None = None
    status: str = "ACTIVE"


@dataclass
class UniverseMembership:
    security_id: UUID
    universe: Universe
    effective_from: date
    market_cap: float | None = None
    avg_daily_value: float | None = None


class SecuritiesMaster:
    """In-memory securities registry for Phase 1; backed by PostgreSQL in production."""

    def __init__(self) -> None:
        self._companies: dict[UUID, Company] = {}
        self._securities: dict[UUID, Security] = {}
        self._by_isin: dict[str, UUID] = {}
        self._by_nse: dict[str, UUID] = {}
        self._universe: list[UniverseMembership] = []

    @property
    def company_count(self) -> int:
        return len(self._companies)

    @property
    def security_count(self) -> int:
        return len(self._securities)

    def register_company(self, name: str, **kwargs: Any) -> Company:
        company = Company(company_id=uuid4(), name=name, **kwargs)
        self._companies[company.company_id] = company
        return company

    def register_security(self, company_id: UUID, **kwargs: Any) -> Security:
        security = Security(security_id=uuid4(), company_id=company_id, **kwargs)
        self._securities[security.security_id] = security
        if security.isin:
            self._by_isin[security.isin] = security.security_id
        if security.nse_symbol:
            self._by_nse[security.nse_symbol.upper()] = security.security_id
        return security

    def get_by_nse(self, symbol: str) -> Security | None:
        sid = self._by_nse.get(symbol.upper())
        return self._securities.get(sid) if sid else None

    def get_by_isin(self, isin: str) -> Security | None:
        sid = self._by_isin.get(isin.upper())
        return self._securities.get(sid) if sid else None

    def assign_universe(
        self,
        security_id: UUID,
        market_cap: float,
        avg_daily_value: float,
        *,
        microcap_max: float = 500,
        smallcap_max: float = 5000,
        midcap_max: float = 20000,
        illiquid_threshold: float = 10,
        high_liquidity_threshold: float = 500,
        effective_from: date | None = None,
    ) -> list[UniverseMembership]:
        """Assign cap-band and liquidity universes per config/settings.yaml."""
        security = self._securities.get(security_id)
        if not security:
            raise ValueError(f"Unknown security_id: {security_id}")

        eff = effective_from or date.today()
        memberships: list[UniverseMembership] = []

        segment_universe = Universe.SME if security.segment == Segment.SME else Universe.MAINBOARD
        memberships.append(UniverseMembership(security_id, segment_universe, eff, market_cap, avg_daily_value))

        if market_cap <= microcap_max:
            cap_universe = Universe.MICROCAP
        elif market_cap <= smallcap_max:
            cap_universe = Universe.SMALLCAP
        elif market_cap <= midcap_max:
            cap_universe = Universe.MIDCAP
        else:
            cap_universe = Universe.LARGECAP
        memberships.append(UniverseMembership(security_id, cap_universe, eff, market_cap, avg_daily_value))

        liq_universe = (
            Universe.HIGH_LIQUIDITY
            if avg_daily_value >= high_liquidity_threshold
            else Universe.ILLIQUID
            if avg_daily_value < illiquid_threshold
            else None
        )
        if liq_universe:
            memberships.append(UniverseMembership(security_id, liq_universe, eff, market_cap, avg_daily_value))

        self._universe.extend(memberships)
        return memberships

    def load_from_csv_rows(self, rows: list[dict[str, Any]]) -> int:
        """Load securities from normalized CSV row dicts."""
        count = 0
        for row in rows:
            company = self.register_company(
                name=row["company_name"],
                sector=row.get("sector"),
                industry=row.get("industry"),
            )
            self.register_security(
                company_id=company.company_id,
                isin=row.get("isin"),
                nse_symbol=row.get("nse_symbol"),
                bse_scrip_code=row.get("bse_scrip_code"),
                segment=Segment(row.get("segment", "MAINBOARD")),
                listing_date=row.get("listing_date"),
            )
            count += 1
        return count

    def list_by_universe(self, universe: Universe) -> list[Security]:
        sids = {m.security_id for m in self._universe if m.universe == universe}
        return [self._securities[sid] for sid in sids if sid in self._securities]
