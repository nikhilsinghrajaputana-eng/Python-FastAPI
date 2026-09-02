"""Tests for securities master."""

from ecads.ingestion.securities_master import SecuritiesMaster, Segment, Universe


def test_register_and_lookup():
    master = SecuritiesMaster()
    company = master.register_company("Test Industries Ltd", sector="Manufacturing")
    master.register_security(
        company_id=company.company_id,
        isin="INE123A01012",
        nse_symbol="TESTIND",
        bse_scrip_code="500001",
        segment=Segment.MAINBOARD,
    )
    assert master.security_count == 1
    assert master.get_by_nse("testind") is not None
    assert master.get_by_isin("INE123A01012") is not None


def test_universe_assignment():
    master = SecuritiesMaster()
    company = master.register_company("Small Co Ltd")
    sec = master.register_security(
        company_id=company.company_id,
        isin="INE999Z01099",
        nse_symbol="SMALLCO",
        bse_scrip_code=None,
        segment=Segment.SME,
    )
    memberships = master.assign_universe(
        sec.security_id,
        market_cap=300,
        avg_daily_value=5,
    )
    universes = {m.universe for m in memberships}
    assert Universe.SME in universes
    assert Universe.MICROCAP in universes
    assert Universe.ILLIQUID in universes


def test_load_from_csv_rows():
    master = SecuritiesMaster()
    rows = [
        {
            "company_name": "Alpha Ltd",
            "isin": "INE111A01011",
            "nse_symbol": "ALPHA",
            "segment": "MAINBOARD",
        },
        {
            "company_name": "Beta SME Ltd",
            "isin": "INE222B01022",
            "nse_symbol": "BETASME",
            "segment": "SME",
        },
    ]
    assert master.load_from_csv_rows(rows) == 2
    assert master.company_count == 2
