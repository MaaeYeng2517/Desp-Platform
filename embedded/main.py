"""Embedded Analytics API Service."""
from datetime import datetime
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from embedded.config import settings
from embedded.database import async_session_factory, init_db
from embedded.models import EmbedToken, EmbeddedDashboard, EmbeddedChart


app = FastAPI(
    title="Embedded Analytics API",
    version="1.0.0",
    description="API for embedding analytics dashboards and charts in external applications",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class EmbedTokenRequest(BaseModel):
    dashboard_id: str | None = None
    chart_id: str | None = None
    expires_in: int = Field(default=3600, ge=300, le=86400)
    domain: str | None = None


class EmbedTokenResponse(BaseModel):
    token: str
    expires_at: datetime
    embed_url: str


class DashboardResponse(BaseModel):
    id: str
    title: str
    description: str | None
    charts: list[dict[str, Any]]
    created_at: datetime
    updated_at: datetime


class ChartResponse(BaseModel):
    id: str
    title: str
    chart_type: str
    query: str
    config: dict[str, Any]
    created_at: datetime
    updated_at: datetime


class ChartDataResponse(BaseModel):
    chart_id: str
    data: list[dict[str, Any]]
    columns: list[str]
    updated_at: datetime


async def get_db() -> AsyncSession:
    async with async_session_factory() as session:
        yield session


async def verify_embed_token(
    request: Request,
    token: str = Query(..., alias="embed_token"),
    db: AsyncSession = Depends(get_db),
) -> EmbedToken:
    result = await db.execute(select(EmbedToken).where(EmbedToken.token == token))
    embed_token = result.scalar_one_or_none()

    if not embed_token:
        raise HTTPException(status_code=401, detail="Invalid embed token")

    if embed_token.expires_at < datetime.utcnow():
        raise HTTPException(status_code=401, detail="Embed token expired")

    if embed_token.domain and request.headers.get("origin"):
        origin = request.headers.get("origin", "")
        if embed_token.domain not in origin:
            raise HTTPException(status_code=403, detail="Domain not authorized for this token")

    return embed_token


@app.on_event("startup")
async def startup_event():
    await init_db()


@app.get("/")
async def root():
    return {
        "name": "Embedded Analytics API",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/health")
async def health():
    try:
        async with async_session_factory() as db:
            await db.execute(select(1))
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Database unavailable") from exc
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.post("/api/v1/embed/tokens", response_model=EmbedTokenResponse)
async def create_embed_token(
    request: EmbedTokenRequest,
    db: AsyncSession = Depends(get_db),
):
    if not request.dashboard_id and not request.chart_id:
        raise HTTPException(status_code=400, detail="Either dashboard_id or chart_id is required")

    embed_token = EmbedToken.create_token(
        dashboard_id=request.dashboard_id,
        chart_id=request.chart_id,
        expires_in=request.expires_in,
        domain=request.domain,
    )

    db.add(embed_token)
    await db.commit()

    base_url = settings.EMBED_BASE_URL
    if request.dashboard_id:
        embed_url = f"{base_url}/embed/dashboard/{request.dashboard_id}?token={embed_token.token}"
    else:
        embed_url = f"{base_url}/embed/chart/{request.chart_id}?token={embed_token.token}"

    return EmbedTokenResponse(
        token=embed_token.token,
        expires_at=embed_token.expires_at,
        embed_url=embed_url,
    )


@app.get("/api/v1/embed/dashboards", response_model=list[DashboardResponse])
async def list_dashboards(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(EmbeddedDashboard).where(EmbeddedDashboard.is_active.is_(True)))
    dashboards = result.scalars().all()
    return [
        DashboardResponse(
            id=d.id,
            title=d.title,
            description=d.description,
            charts=d.charts,
            created_at=d.created_at,
            updated_at=d.updated_at,
        )
        for d in dashboards
    ]


@app.get("/api/v1/embed/dashboards/{dashboard_id}", response_model=DashboardResponse)
async def get_dashboard(dashboard_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(EmbeddedDashboard).where(EmbeddedDashboard.id == dashboard_id))
    dashboard = result.scalar_one_or_none()

    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")

    return DashboardResponse(
        id=dashboard.id,
        title=dashboard.title,
        description=dashboard.description,
        charts=dashboard.charts,
        created_at=dashboard.created_at,
        updated_at=dashboard.updated_at,
    )


@app.get("/api/v1/embed/charts", response_model=list[ChartResponse])
async def list_charts(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(EmbeddedChart).where(EmbeddedChart.is_active.is_(True)))
    charts = result.scalars().all()
    return [
        ChartResponse(
            id=c.id,
            title=c.title,
            chart_type=c.chart_type,
            query=c.query,
            config=c.config,
            created_at=c.created_at,
            updated_at=c.updated_at,
        )
        for c in charts
    ]


@app.get("/api/v1/embed/charts/{chart_id}", response_model=ChartResponse)
async def get_chart(chart_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(EmbeddedChart).where(EmbeddedChart.id == chart_id))
    chart = result.scalar_one_or_none()

    if not chart:
        raise HTTPException(status_code=404, detail="Chart not found")

    return ChartResponse(
        id=chart.id,
        title=chart.title,
        chart_type=chart.chart_type,
        query=chart.query,
        config=chart.config,
        created_at=chart.created_at,
        updated_at=chart.updated_at,
    )


@app.get("/api/v1/embed/charts/{chart_id}/data", response_model=ChartDataResponse)
async def get_chart_data(
    chart_id: str,
    token: EmbedToken = Depends(verify_embed_token),
    db: AsyncSession = Depends(get_db),
):
    if token.chart_id and token.chart_id != chart_id:
        raise HTTPException(status_code=403, detail="Token not authorized for this chart")

    result = await db.execute(select(EmbeddedChart).where(EmbeddedChart.id == chart_id))
    chart = result.scalar_one_or_none()

    if not chart:
        raise HTTPException(status_code=404, detail="Chart not found")

    async with async_session_factory() as data_db:
        data_result = await data_db.execute(text(chart.query))
        rows = data_result.fetchall()
        columns = list(data_result.keys()) if rows else []

    return ChartDataResponse(
        chart_id=chart_id,
        data=[dict(zip(columns, row, strict=False)) for row in rows],
        columns=columns,
        updated_at=datetime.utcnow(),
    )


@app.get("/embed/dashboard/{dashboard_id}", response_class=HTMLResponse)
async def embed_dashboard(
    dashboard_id: str,
    request: Request,
    token: str = Query(..., alias="token"),
    db: AsyncSession = Depends(get_db),
):
    embed_token = await verify_embed_token(request, token, db)

    if embed_token.dashboard_id and embed_token.dashboard_id != dashboard_id:
        raise HTTPException(status_code=403, detail="Token not authorized for this dashboard")

    result = await db.execute(select(EmbeddedDashboard).where(EmbeddedDashboard.id == dashboard_id))
    dashboard = result.scalar_one_or_none()

    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")

    chart_ids = [c.get("chart_id") for c in dashboard.charts if c.get("chart_id")]

    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{dashboard.title}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f8f9fa; }}
        .dashboard {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
        .dashboard-header {{ margin-bottom: 24px; }}
        .dashboard-title {{ font-size: 24px; font-weight: 600; color: #1a1a2e; }}
        .dashboard-description {{ color: #6b7280; margin-top: 8px; }}
        .charts-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 20px; }}
        .chart-card {{ background: white; border-radius: 12px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
        .chart-title {{ font-size: 16px; font-weight: 600; margin-bottom: 16px; color: #1a1a2e; }}
        .chart-container {{ position: relative; height: 300px; }}
        .loading {{ display: flex; align-items: center; justify-content: center; height: 300px; color: #6b7280; }}
        .error {{ display: flex; align-items: center; justify-content: center; height: 300px; color: #ef4444; }}
    </style>
</head>
<body>
    <div class="dashboard">
        <div class="dashboard-header">
            <h1 class="dashboard-title">{dashboard.title}</h1>
            {f'<p class="dashboard-description">{dashboard.description}</p>' if dashboard.description else ''}
        </div>
        <div class="charts-grid" id="charts-grid">
            {''.join(f'''
            <div class="chart-card">
                <div class="chart-title" id="title-{cid}">Loading...</div>
                <div class="chart-container">
                    <canvas id="chart-{cid}"></canvas>
                    <div class="loading" id="loading-{cid}">Loading chart...</div>
                    <div class="error" id="error-{cid}" style="display:none;"></div>
                </div>
            </div>
            ''' for cid in chart_ids)}
        </div>
    </div>
    <script>
        const API_BASE = '{settings.API_BASE_URL}';
        const TOKEN = '{token}';
        const CHART_IDS = {chart_ids};

        async function fetchChartData(chartId) {{
            const response = await fetch(`${{API_BASE}}/api/v1/embed/charts/${{chartId}}/data?embed_token=${{TOKEN}}`);
            if (!response.ok) throw new Error(`HTTP ${{response.status}}`);
            return response.json();
        }}

        async function fetchChartConfig(chartId) {{
            const response = await fetch(`${{API_BASE}}/api/v1/embed/charts/${{chartId}}`);
            if (!response.ok) throw new Error(`HTTP ${{response.status}}`);
            return response.json();
        }}

        function getChartConfig(chartType, data, columns, config) {{
            const labels = data.map(row => row[columns[0]]);
            const datasets = columns.slice(1).map((col, i) => ({{
                label: col,
                data: data.map(row => row[col]),
                borderColor: `hsl(${{(i * 137) % 360}}, 70%, 50%)`,
                backgroundColor: `hsla(${{(i * 137) % 360}}, 70%, 50%, 0.1)`,
                fill: config.fill || false,
                tension: config.tension || 0.3,
            }}));

            const baseConfig = {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{ display: true, position: 'top' }},
                    tooltip: {{ mode: 'index', intersect: false }},
                }},
                scales: {{
                    x: {{ grid: {{ display: false }} }},
                    y: {{ beginAtZero: config.beginAtZero !== false, grid: {{ color: '#f3f4f6' }} }},
                }},
            }};

            if (chartType === 'bar') {{
                return {{ ...baseConfig, type: 'bar', data: {{ labels, datasets: datasets.map(d => ({...d, borderWidth: 0, borderRadius: 4}})) }}};
            }}
            if (chartType === 'line') {{
                return {{ ...baseConfig, type: 'line', data: {{ labels, datasets }} }};
            }}
            if (chartType === 'area') {{
                return {{ ...baseConfig, type: 'line', data: {{ labels, datasets: datasets.map(d => ({...d, fill: true})) }} }};
            }}
            if (chartType === 'pie') {{
                return {{ type: 'pie', data: {{ labels, datasets: [{ data: data.map(row => row[columns[1]]), backgroundColor: datasets.map(d => d.backgroundColor) }] }}, options: {{ responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ position: 'right' }} }} }} }};
            }}
            return {{ ...baseConfig, type: 'bar', data: {{ labels, datasets }} }};
        }}

        async function loadChart(chartId) {{
            const titleEl = document.getElementById(`title-${{chartId}}`);
            const canvas = document.getElementById(`chart-${{chartId}}`);
            const loading = document.getElementById(`loading-${{chartId}}`);
            const error = document.getElementById(`error-${{chartId}}`);

            try {{
                const [dataRes, configRes] = await Promise.all([
                    fetchChartData(chartId),
                    fetchChartConfig(chartId),
                ]);

                titleEl.textContent = configRes.title;
                loading.style.display = 'none';
                canvas.style.display = 'block';

                const chartConfig = getChartConfig(configRes.chart_type, dataRes.data, dataRes.columns, configRes.config);
                new Chart(canvas, chartConfig);
            }} catch (err) {{
                loading.style.display = 'none';
                error.style.display = 'flex';
                error.textContent = `Failed to load chart: ${{err.message}}`;
            }}
        }}

        CHART_IDS.forEach(loadChart);
    </script>
</body>
</html>
    """


@app.get("/embed/chart/{chart_id}", response_class=HTMLResponse)
async def embed_chart(
    chart_id: str,
    request: Request,
    token: str = Query(..., alias="token"),
    db: AsyncSession = Depends(get_db),
):
    embed_token = await verify_embed_token(request, token, db)

    if embed_token.chart_id and embed_token.chart_id != chart_id:
        raise HTTPException(status_code=403, detail="Token not authorized for this chart")

    result = await db.execute(select(EmbeddedChart).where(EmbeddedChart.id == chart_id))
    chart = result.scalar_one_or_none()

    if not chart:
        raise HTTPException(status_code=404, detail="Chart not found")

    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{chart.title}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: white; min-height: 100vh; display: flex; flex-direction: column; }}
        .chart-wrapper {{ flex: 1; display: flex; flex-direction: column; padding: 16px; }}
        .chart-title {{ font-size: 18px; font-weight: 600; color: #1a1a2e; margin-bottom: 16px; text-align: center; }}
        .chart-container {{ position: relative; flex: 1; }}
        .loading {{ display: flex; align-items: center; justify-content: center; height: 100%; color: #6b7280; }}
        .error {{ display: flex; align-items: center; justify-content: center; height: 100%; color: #ef4444; }}
    </style>
</head>
<body>
    <div class="chart-wrapper">
        <h1 class="chart-title" id="chart-title">{chart.title}</h1>
        <div class="chart-container">
            <canvas id="chart"></canvas>
            <div class="loading" id="loading">Loading chart...</div>
            <div class="error" id="error" style="display:none;"></div>
        </div>
    </div>
    <script>
        const API_BASE = '{settings.API_BASE_URL}';
        const TOKEN = '{token}';
        const CHART_ID = '{chart_id}';

        async function fetchChartData() {{
            const response = await fetch(`${{API_BASE}}/api/v1/embed/charts/${{CHART_ID}}/data?embed_token=${{TOKEN}}`);
            if (!response.ok) throw new Error(`HTTP ${{response.status}}`);
            return response.json();
        }}

        async function fetchChartConfig() {{
            const response = await fetch(`${{API_BASE}}/api/v1/embed/charts/${{CHART_ID}}`);
            if (!response.ok) throw new Error(`HTTP ${{response.status}}`);
            return response.json();
        }}

        function getChartConfig(chartType, data, columns, config) {{
            const labels = data.map(row => row[columns[0]]);
            const datasets = columns.slice(1).map((col, i) => ({{
                label: col,
                data: data.map(row => row[col]),
                borderColor: `hsl(${{(i * 137) % 360}}, 70%, 50%)`,
                backgroundColor: `hsla(${{(i * 137) % 360}}, 70%, 50%, 0.1)`,
                fill: config.fill || false,
                tension: config.tension || 0.3,
            }}));

            const baseConfig = {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{ display: true, position: 'top' }},
                    tooltip: {{ mode: 'index', intersect: false }},
                }},
                scales: {{
                    x: {{ grid: {{ display: false }} }},
                    y: {{ beginAtZero: config.beginAtZero !== false, grid: {{ color: '#f3f4f6' }} }},
                }},
            }};

            if (chartType === 'bar') {{
                return {{ ...baseConfig, type: 'bar', data: {{ labels, datasets: datasets.map(d => ({...d, borderWidth: 0, borderRadius: 4}})) }}};
            }}
            if (chartType === 'line') {{
                return {{ ...baseConfig, type: 'line', data: {{ labels, datasets }} }};
            }}
            if (chartType === 'area') {{
                return {{ ...baseConfig, type: 'line', data: {{ labels, datasets: datasets.map(d => ({...d, fill: true})) }} }};
            }}
            if (chartType === 'pie') {{
                return {{ type: 'pie', data: {{ labels, datasets: [{ data: data.map(row => row[columns[1]]), backgroundColor: datasets.map(d => d.backgroundColor) }] }}, options: {{ responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ position: 'right' }} }} }} }};
            }}
            return {{ ...baseConfig, type: 'bar', data: {{ labels, datasets }} }};
        }}

        async function loadChart() {{
            const canvas = document.getElementById('chart');
            const loading = document.getElementById('loading');
            const error = document.getElementById('error');
            const titleEl = document.getElementById('chart-title');

            try {{
                const [dataRes, configRes] = await Promise.all([
                    fetchChartData(),
                    fetchChartConfig(),
                ]);

                titleEl.textContent = configRes.title;
                loading.style.display = 'none';
                canvas.style.display = 'block';

                const chartConfig = getChartConfig(configRes.chart_type, dataRes.data, dataRes.columns, configRes.config);
                new Chart(canvas, chartConfig);
            }} catch (err) {{
                loading.style.display = 'none';
                error.style.display = 'flex';
                error.textContent = `Failed to load chart: ${{err.message}}`;
            }}
        }}

        loadChart();
    </script>
</body>
</html>
    """


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)