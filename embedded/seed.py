"""Seed script for Embedded Analytics default dashboards and charts."""
import asyncio
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from embedded.config import settings
from embedded.database import async_session_factory, init_db
from embedded.models import EmbeddedChart, EmbeddedDashboard


async def seed_dashboards_and_charts(db: AsyncSession):
    # Check if already seeded
    result = await db.execute(select(EmbeddedDashboard).limit(1))
    if result.scalar_one_or_none():
        print("Already seeded, skipping...")
        return

    # Create charts
    charts = [
        EmbeddedChart(
            id=str(uuid4()),
            title="Daily Revenue",
            chart_type="area",
            query="""
                SELECT 
                    transaction_date,
                    SUM(total_amount) as revenue
                FROM mart.sales
                WHERE transaction_date >= CURRENT_DATE - INTERVAL '30 days'
                GROUP BY transaction_date
                ORDER BY transaction_date
            """,
            config={
                "fill": True,
                "tension": 0.4,
                "beginAtZero": True,
            },
        ),
        EmbeddedChart(
            id=str(uuid4()),
            title="Revenue by Product Category",
            chart_type="bar",
            query="""
                SELECT 
                    p.category,
                    SUM(s.total_amount) as revenue
                FROM mart.sales s
                JOIN mart.products p ON s.product_id = p.product_id
                WHERE s.transaction_date >= CURRENT_DATE - INTERVAL '30 days'
                GROUP BY p.category
                ORDER BY revenue DESC
            """,
            config={
                "beginAtZero": True,
            },
        ),
        EmbeddedChart(
            id=str(uuid4()),
            title="Top 10 Customers by Revenue",
            chart_type="bar",
            query="""
                SELECT 
                    c.customer_name,
                    SUM(s.total_amount) as revenue
                FROM mart.sales s
                JOIN mart.customers c ON s.customer_id = c.customer_id
                WHERE s.transaction_date >= CURRENT_DATE - INTERVAL '90 days'
                GROUP BY c.customer_name
                ORDER BY revenue DESC
                LIMIT 10
            """,
            config={
                "beginAtZero": True,
            },
        ),
        EmbeddedChart(
            id=str(uuid4()),
            title="Sales Trend - Last 12 Months",
            chart_type="line",
            query="""
                SELECT 
                    DATE_TRUNC('month', transaction_date) as month,
                    COUNT(*) as transactions,
                    SUM(quantity) as units_sold,
                    SUM(total_amount) as revenue
                FROM mart.sales
                WHERE transaction_date >= CURRENT_DATE - INTERVAL '12 months'
                GROUP BY DATE_TRUNC('month', transaction_date)
                ORDER BY month
            """,
            config={
                "tension": 0.3,
                "beginAtZero": True,
            },
        ),
        EmbeddedChart(
            id=str(uuid4()),
            title="Revenue Distribution by Segment",
            chart_type="pie",
            query="""
                SELECT 
                    c.segment,
                    SUM(s.total_amount) as revenue
                FROM mart.sales s
                JOIN mart.customers c ON s.customer_id = c.customer_id
                WHERE s.transaction_date >= CURRENT_DATE - INTERVAL '30 days'
                GROUP BY c.segment
            """,
            config={},
        ),
    ]

    for chart in charts:
        db.add(chart)

    await db.flush()

    # Create dashboard
    dashboard = EmbeddedDashboard(
        id=str(uuid4()),
        title="Sales Overview",
        description="Real-time sales performance dashboard with key metrics and trends",
        charts=[
            {"chart_id": charts[0].id, "title": "Daily Revenue", "width": 12, "height": 6},
            {"chart_id": charts[1].id, "title": "Revenue by Category", "width": 6, "height": 6},
            {"chart_id": charts[2].id, "title": "Top 10 Customers", "width": 6, "height": 6},
            {"chart_id": charts[3].id, "title": "Monthly Sales Trend", "width": 12, "height": 6},
            {"chart_id": charts[4].id, "title": "Revenue by Segment", "width": 6, "height": 6},
        ],
    )
    db.add(dashboard)

    await db.commit()
    print(f"Seeded {len(charts)} charts and 1 dashboard")


async def main():
    await init_db()
    async with async_session_factory() as db:
        await seed_dashboards_and_charts(db)


if __name__ == "__main__":
    asyncio.run(main())