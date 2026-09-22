# Knowledge Engineering Platform

A comprehensive Knowledge Engineering Platform that transforms how organizations manage, search, and utilize their knowledge assets.

## Features

- **Multi-Source Ingestion**: PDF, Web, Database, API, File, YouTube
- **Visual Workflow Builder**: Drag & Drop Canvas for Knowledge Pipelines
- **Metadata Management**: Schema, Taxonomy, Ontology, Validation
- **Hybrid Search**: BM25 + Vector + Metadata + Graph
- **RAG Engine**: Context Engineering + Verification
- **AI Agent**: Tool Calling + MCP Integration
- **Governance**: RBAC, Multi-Tenant, Audit, Approval Workflows
- **Evaluation**: Metrics Dashboard, Test Sets, Quality Monitoring

## Architecture

```
Sources → Ingestion → Processing → Metadata → Knowledge → Index → Retrieval → Context → RAG → Agent → Action
```

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 18+ (for frontend development)

### Backend

```bash
cd knowledge-platform
cp .env.example .env
# Edit .env with your configuration

# Start services
docker-compose up -d

# Run backend
cd backend
pip install -r ../requirements.txt
uvicorn main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Project Structure

```
knowledge-platform/
├── backend/           # FastAPI Backend
├── frontend/          # Next.js Frontend
├── workers/           # Background Workers
├── workflows/         # Workflow Definitions
├── docker/            # Docker Configuration
├── scripts/           # Utility Scripts
└── docs/              # Documentation
```

## API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## License

MIT