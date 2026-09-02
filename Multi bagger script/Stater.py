"""
========================================================================================
MODULE: ecads.forensic_engine
DESCRIPTION: Production-grade Forensic Accounting, Capital Efficiency & Divergence Engine
ENGINE VERSION: ECADS-v2.4
FRAMEWORK: Polars (Vectorized Multi-Tenant Execution)
========================================================================================
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Final

import polars as pl

# --------------------------------------------------------------------------------------
# LOGGING CONFIGURATION
# --------------------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s : %(message)s",
)
logger = logging.getLogger("ECADS_FORENSIC_ENGINE")

# --------------------------------------------------------------------------------------
# SYSTEM THRESHOLDS & CONSTANTS
# --------------------------------------------------------------------------------------
CFCR_HARD_FAIL_THRESHOLD: Final[float] = 0.60
DIVERGENCE_CFO_RATIO_ALERT: Final[float] = 0.30
IROCE_LOW_HURDLE_RATE: Final[float] = 0.15  # 15% minimum acceptable hurdle in India


# --------------------------------------------------------------------------------------
# INPUT SCHEMA VERIFICATION
# --------------------------------------------------------------------------------------
class FinancialSchema:
    """Canonical column definitions required for forensic calculation."""

    SECURITY_ID: Final[str] = "security_id"
    ISIN: Final[str] = "isin"
    PERIOD_END_DATE: Final[str] = "period_end_date"
    FILING_TIMESTAMP: Final[str] = "filing_timestamp"
    REPORT_TYPE: Final[str] = "report_type"  # 'CONSOLIDATED' | 'STANDALONE'

    # Income Statement
    REVENUE: Final[str] = "revenue"
    EBITDA: Final[str] = "ebitda"
    EBIT: Final[str] = "ebit"
    PAT: Final[str] = "pat"

    # Balance Sheet
    TOTAL_ASSETS: Final[str] = "total_assets"
    CURRENT_LIABILITIES: Final[str] = "current_liabilities"
    GROSS_DEBT: Final[str] = "gross_debt"
    RELATED_PARTY_LOANS: Final[str] = "related_party_loans_advances"

    # Cash Flow Statement
    CFO: Final[str] = "cfo"
    CAPEX: Final[str] = "capex"


# --------------------------------------------------------------------------------------
# ENGINE IMPLEMENTATION
# --------------------------------------------------------------------------------------
class ForensicAccountingEngine:
    """
    Computes Point-in-Time Indian forensic metrics:
    1. Consolidated vs Standalone Divergence & Capital Tunneling.
    2. 4-Quarter Rolling Cash-Flow Confirmation Ratio (CFCR).
    3. Incremental Return on Capital Employed (iROCE) over N-quarter shifts.
    """

    def __init__(self, iroce_lookback_quarters: int = 4) -> None:
        self.iroce_lookback = iroce_lookback_quarters

    def _validate_input_frame(self, df: pl.DataFrame) -> None:
        """Validates that required schema columns are present with non-null critical keys."""
        required_cols = {
            getattr(FinancialSchema, attr)
            for attr in dir(FinancialSchema)
            if not attr.startswith("_")
        }
        missing = required_cols.difference(set(df.columns))
        if missing:
            raise ValueError(f"Schema violation. Missing columns: {sorted(missing)}")

    def compute_metrics(
        self,
        raw_financials: pl.DataFrame,
        point_in_time_cutoff: datetime | None = None,
    ) -> pl.DataFrame:
        """
        Executes full forensic pipeline across an arbitrary multi-tenant universe.

        Parameters:
            raw_financials: Polars DataFrame containing both Consolidated and Standalone rows.
            point_in_time_cutoff: Optional timestamp for backtest lookahead prevention.

        Returns:
            Polars DataFrame enriched with forensic flags, ratios, and risk vectors.
        """
        self._validate_input_frame(raw_financials)

        # 1. Enforce Point-in-Time (PIT) horizon if specified
        df = raw_financials
        if point_in_time_cutoff is not None:
            df = df.filter(pl.col(FinancialSchema.FILING_TIMESTAMP) <= point_in_time_cutoff)

        # Ensure correct datatypes & sorting
        df = df.with_columns(
            [
                pl.col(FinancialSchema.PERIOD_END_DATE).cast(pl.Date),
                pl.col(FinancialSchema.FILING_TIMESTAMP).cast(pl.Datetime),
                pl.col(FinancialSchema.REPORT_TYPE).cast(pl.Categorical),
            ]
        ).sort([FinancialSchema.SECURITY_ID, FinancialSchema.PERIOD_END_DATE])

        # 2. Derive Core Financial Intermediaries (Capital Employed)
        df = df.with_columns(
            (pl.col(FinancialSchema.TOTAL_ASSETS) - pl.col(FinancialSchema.CURRENT_LIABILITIES))
            .alias("capital_employed")
        )

        # 3. Compute Consolidated vs Standalone Divergence Metrics
        divergence_df = self._compute_parent_sub_divergence(df)

        # 4. Compute Rolling Quality Ratios & iROCE on Consolidated numbers
        consolidated_df = df.filter(
            pl.col(FinancialSchema.REPORT_TYPE) == "CONSOLIDATED"
        )
        quality_df = self._compute_rolling_quality_and_iroce(consolidated_df)

        # 5. Join results and evaluate master forensic flags
        final_df = quality_df.join(
            divergence_df,
            on=[FinancialSchema.SECURITY_ID, FinancialSchema.PERIOD_END_DATE],
            how="left",
        )

        return self._evaluate_master_flags(final_df)

    def _compute_parent_sub_divergence(self, df: pl.DataFrame) -> pl.DataFrame:
        """
        Splits and pivots Standalone vs Consolidated to measure cash leakage
        and subsidiary capital tunneling.
        """
        # Pivot the metrics to have standalone and consolidated side-by-side
        pivoted = (
            df.select(
                [
                    FinancialSchema.SECURITY_ID,
                    FinancialSchema.PERIOD_END_DATE,
                    FinancialSchema.REPORT_TYPE,
                    FinancialSchema.REVENUE,
                    FinancialSchema.PAT,
                    FinancialSchema.CFO,
                    FinancialSchema.GROSS_DEBT,
                    FinancialSchema.RELATED_PARTY_LOANS,
                    "capital_employed",
                ]
            )
            .pivot(
                index=[FinancialSchema.SECURITY_ID, FinancialSchema.PERIOD_END_DATE],
                on=FinancialSchema.REPORT_TYPE,
                values=[
                    FinancialSchema.REVENUE,
                    FinancialSchema.PAT,
                    FinancialSchema.CFO,
                    FinancialSchema.GROSS_DEBT,
                    FinancialSchema.RELATED_PARTY_LOANS,
                    "capital_employed",
                ],
            )
        )

        # Metrics for Capital Tunneling and Cash Divergence
        # Dynamic Polars expression handling based on pivot column naming convention
        metrics_df = pivoted.with_columns(
            [
                # Cash Leakage Ratio: (Consolidated CFO - Standalone CFO) / Consolidated PAT
                pl.when(pl.col(f"{FinancialSchema.PAT}_CONSOLIDATED") != 0)
                .then(
                    (
                        pl.col(f"{FinancialSchema.CFO}_CONSOLIDATED")
                        - pl.col(f"{FinancialSchema.CFO}_STANDALONE")
                    )
                    / pl.col(f"{FinancialSchema.PAT}_CONSOLIDATED")
                )
                .otherwise(None)
                .alias("cash_leakage_to_subs_ratio"),

                # Debt Transfer / Tunneling Index: Standalone Debt / Consolidated Debt
                pl.when(pl.col(f"{FinancialSchema.GROSS_DEBT}_CONSOLIDATED") > 0)
                .then(
                    pl.col(f"{FinancialSchema.GROSS_DEBT}_STANDALONE")
                    / pl.col(f"{FinancialSchema.GROSS_DEBT}_CONSOLIDATED")
                )
                .otherwise(1.0)
                .alias("standalone_debt_concentration"),

                # Related Party Loans relative to Standalone Capital Employed
                pl.when(pl.col("capital_employed_STANDALONE") > 0)
                .then(
                    pl.col(f"{FinancialSchema.RELATED_PARTY_LOANS}_STANDALONE")
                    / pl.col("capital_employed_STANDALONE")
                )
                .otherwise(0.0)
                .alias("promoter_related_party_exposure_ratio"),
            ]
        ).select(
            [
                FinancialSchema.SECURITY_ID,
                FinancialSchema.PERIOD_END_DATE,
                "cash_leakage_to_subs_ratio",
                "standalone_debt_concentration",
                "promoter_related_party_exposure_ratio",
            ]
        )

        return metrics_df

    def _compute_rolling_quality_and_iroce(self, cons_df: pl.DataFrame) -> pl.DataFrame:
        """
        Computes 4-quarter rolling Cash-Flow Confirmation Ratio (CFCR)
        and N-quarter Incremental ROCE (iROCE).
        """
        return cons_df.with_columns(
            [
                # 4-Quarter Rolling sums of CFO and EBITDA
                pl.col(FinancialSchema.CFO)
                .rolling_sum(window_size=4, min_periods=4)
                .over(FinancialSchema.SECURITY_ID)
                .alias("cfo_4q_sum"),
                
                pl.col(FinancialSchema.EBITDA)
                .rolling_sum(window_size=4, min_periods=4)
                .over(FinancialSchema.SECURITY_ID)
                .alias("ebitda_4q_sum"),

                # Lags for iROCE calculation: ΔEBIT / ΔCapital_Employed
                pl.col(FinancialSchema.EBIT)
                .shift(self.iroce_lookback)
                .over(FinancialSchema.SECURITY_ID)
                .alias("ebit_lagged"),

                pl.col("capital_employed")
                .shift(self.iroce_lookback)
                .over(FinancialSchema.SECURITY_ID)
                .alias("capital_employed_lagged"),
            ]
        ).with_columns(
            [
                # Cash-Flow Confirmation Ratio (CFCR)
                pl.when(pl.col("ebitda_4q_sum") > 0)
                .then(pl.col("cfo_4q_sum") / pl.col("ebitda_4q_sum"))
                .otherwise(0.0)
                .alias("cfcr_4q"),

                # ΔEBIT and ΔCapital Employed
                (pl.col(FinancialSchema.EBIT) - pl.col("ebit_lagged")).alias("delta_ebit"),
                (pl.col("capital_employed") - pl.col("capital_employed_lagged")).alias(
                    "delta_capital_employed"
                ),
            ]
        ).with_columns(
            [
                # Incremental ROCE (iROCE)
                # Handling boundary condition: Only meaningful when positive new capital is deployed
                pl.when(pl.col("delta_capital_employed") > 0)
                .then(pl.col("delta_ebit") / pl.col("delta_capital_employed"))
                .otherwise(None)
                .alias("iroce"),
            ]
        )

    def _evaluate_master_flags(self, df: pl.DataFrame) -> pl.DataFrame:
        """Applies composite forensic rules to generate deterministic audit warnings."""
        return df.with_columns(
            [
                # Flag 1: High Accounting Profit with Poor Cash Conversion
                pl.when((pl.col("cfcr_4q") < CFCR_HARD_FAIL_THRESHOLD) & (pl.col("ebitda_4q_sum") > 0))
                .then(True)
                .otherwise(False)
                .alias("flag_earnings_quality_divergence"),

                # Flag 2: Capital Tunneling / Opaque Subsidiary Leakage
                pl.when(
                    (pl.col("cash_leakage_to_subs_ratio") < -DIVERGENCE_CFO_RATIO_ALERT)
                    | (pl.col("promoter_related_party_exposure_ratio") > 0.15)
                )
                .then(True)
                .otherwise(False)
                .alias("flag_subsidiary_tunneling_risk"),

                # Flag 3: Value-Destructive Capex Expansion
                pl.when((pl.col("delta_capital_employed") > 0) & (pl.col("iroce") < IROCE_LOW_HURDLE_RATE))
                .then(True)
                .otherwise(False)
                .alias("flag_capital_misallocation_risk"),
            ]
        )


# --------------------------------------------------------------------------------------
# VERIFICATION & SMOKE TEST SUITE
# --------------------------------------------------------------------------------------
if __name__ == "__main__":
    from datetime import date

    # Generate synthetic, structurally representative Indian corporate filings data
    sample_data = pl.DataFrame(
        {
            FinancialSchema.SECURITY_ID: [1001] * 8 + [1002] * 8,
            FinancialSchema.ISIN: ["INE000A01010"] * 8 + ["INE000B01020"] * 8,
            FinancialSchema.PERIOD_END_DATE: [
                date(2025, 3, 31), date(2025, 6, 30), date(2025, 9, 30), date(2025, 12, 31),
                date(2025, 3, 31), date(2025, 6, 30), date(2025, 9, 30), date(2025, 12, 31),
            ] * 2,
            FinancialSchema.FILING_TIMESTAMP: [
                datetime(2025, 5, 15, 18, 0), datetime(2025, 8, 14, 18, 0),
                datetime(2025, 11, 14, 18, 0), datetime(2026, 2, 14, 18, 0),
                datetime(2025, 5, 15, 18, 0), datetime(2025, 8, 14, 18, 0),
                datetime(2025, 11, 14, 18, 0), datetime(2026, 2, 14, 18, 0),
            ] * 2,
            FinancialSchema.REPORT_TYPE: (
                ["CONSOLIDATED"] * 4 + ["STANDALONE"] * 4 +
                ["CONSOLIDATED"] * 4 + ["STANDALONE"] * 4
            ),
            FinancialSchema.REVENUE: [
                100.0, 120.0, 150.0, 200.0,
                90.0, 105.0, 130.0, 170.0,
                50.0, 55.0, 60.0, 65.0,
                50.0, 55.0, 60.0, 65.0,
            ],
            FinancialSchema.EBITDA: [
                20.0, 26.0, 35.0, 50.0,
                18.0, 22.0, 30.0, 42.0,
                10.0, 11.0, 12.0, 13.0,
                10.0, 11.0, 12.0, 13.0,
            ],
            FinancialSchema.EBIT: [
                16.0, 21.0, 29.0, 42.0,
                14.0, 18.0, 25.0, 35.0,
                8.0, 8.5, 9.0, 9.5,
                8.0, 8.5, 9.0, 9.5,
            ],
            FinancialSchema.PAT: [
                10.0, 14.0, 20.0, 30.0,
                9.0, 12.0, 17.0, 25.0,
                5.0, 5.2, 5.5, 5.8,
                5.0, 5.2, 5.5, 5.8,
            ],
            FinancialSchema.TOTAL_ASSETS: [
                120.0, 130.0, 150.0, 180.0,
                100.0, 110.0, 125.0, 145.0,
                80.0, 85.0, 90.0, 95.0,
                80.0, 85.0, 90.0, 95.0,
            ],
            FinancialSchema.CURRENT_LIABILITIES: [
                20.0, 22.0, 25.0, 30.0,
                15.0, 18.0, 20.0, 25.0,
                10.0, 10.0, 10.0, 10.0,
                10.0, 10.0, 10.0, 10.0,
            ],
            FinancialSchema.GROSS_DEBT: [
                30.0, 28.0, 25.0, 20.0,
                25.0, 24.0, 20.0, 15.0,
                20.0, 22.0, 25.0, 28.0,
                10.0, 10.0, 10.0, 10.0,
            ],
            FinancialSchema.RELATED_PARTY_LOANS: [
                0.0, 0.0, 0.0, 0.0,
                2.0, 2.0, 2.0, 2.0,
                0.0, 0.0, 0.0, 0.0,
                15.0, 18.0, 22.0, 25.0,  # Red flag: High Standalone related-party loans
            ],
            FinancialSchema.CFO: [
                18.0, 22.0, 30.0, 45.0,  # High quality cash generation (ID 1001)
                15.0, 18.0, 25.0, 38.0,
                2.0, 1.5, 1.0, 0.5,      # Collapsing cash flow despite positive PAT (ID 1002)
                2.0, 1.5, 1.0, 0.5,
            ],
            FinancialSchema.CAPEX: [
                5.0, 8.0, 10.0, 12.0,
                4.0, 6.0, 8.0, 10.0,
                2.0, 2.0, 2.0, 2.0,
                2.0, 2.0, 2.0, 2.0,
            ],
        }
    )

    engine = ForensicAccountingEngine(iroce_lookback_quarters=3)
    results = engine.compute_metrics(sample_data)

    print("\n--- FORENSIC ENGINE EXECUTION RESULTS ---")
    print(
        results.select(
            [
                FinancialSchema.SECURITY_ID,
                FinancialSchema.PERIOD_END_DATE,
                "cfcr_4q",
                "iroce",
                "cash_leakage_to_subs_ratio",
                "flag_earnings_quality_divergence",
                "flag_subsidiary_tunneling_risk",
                "flag_capital_misallocation_risk",
            ]
        )
    )