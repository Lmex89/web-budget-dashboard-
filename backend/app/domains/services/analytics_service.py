"""Analytics query service for dashboard data.

SRP: Single responsibility for aggregating and computing analytics data.
     Queries via IUnitOfWork repository abstractions.
OCP: Open for extension with new analytics methods without modifying existing ones.
"""
from typing import List, Optional

from loguru import logger

from app.domains.repositories.unit_of_work import IUnitOfWork


class AnalyticsService:
    """Provides analytical data for dashboard visualizations."""

    def __init__(self, uow: IUnitOfWork) -> None:
        self.uow = uow

    async def monthly_summary(
        self,
        family_id: str,
        year: int,
        month: int,
        category_id: Optional[str] = None,
    ) -> dict:
        """Total expenses for a given family in a specific month/year."""
        logger.debug(f"Monthly summary: family={family_id}, period={year}-{month:02d}")
        async with self.uow:
            result = await self.uow.expenses.get_family_monthly_summary(
                family_id, year, month, category_id
            )
            logger.info(f"Monthly summary for {year}-{month:02d}: total={result['total_expenses']}")
            return result

    async def category_distribution(
        self,
        family_id: str,
        year: int,
        month: int,
        category_id: Optional[str] = None,
    ) -> List[dict]:
        """Expenses grouped by category for a given month/year."""
        logger.debug(f"Category distribution: family={family_id}, period={year}-{month:02d}")
        async with self.uow:
            result = await self.uow.expenses.get_category_distribution(
                family_id, year, month, category_id
            )
            logger.debug(f"Category distribution has {len(result)} entries")
            return result

    async def monthly_trend(self, family_id: str, year: int) -> List[dict]:
        """Expenses per month for a given year (12 data points for line chart)."""
        logger.debug(f"Monthly trend: family={family_id}, year={year}")
        async with self.uow:
            results = []
            for month in range(1, 13):
                summary = await self.uow.expenses.get_family_monthly_summary(
                    family_id, year, month
                )
                results.append(summary)
            return results


