# LeaseLensAI — AI Lease Financial Workflow Automation SaaS

Operational AI for property managers: upload leases, extract key terms, generate payment schedules, reconcile rent rolls, forecast revenue, export to Excel, and audit everything.

## Architecture
- **API:** FastAPI (multi-tenant) + background workers
- **DB:** PostgreSQL + pgvector
- **Cache/Queue:** Redis
- **Docs:** S3-compatible storage (MinIO local, S3 in prod)
- **AI:** LLM extraction + embeddings (provider-agnostic interface)

High-level flow:
Client (Next.js) → FastAPI → Postgres/pgvector → Workers → S3

## Local Development
1. Start infra:
   - `docker compose -f infra/docker-compose.yml up -d`
2. Run API:
   - `cd apps/api && poetry install`
   - `poetry run uvicorn app.main:app --reload --port 8000`
3. Run Client:
   - `cd apps/client && npm install`
   - `npm run dev`
4. Check:
   - API: `GET http://localhost:8000/healthz`
   - API Docs: `http://localhost:8000/docs`
   - Client: `http://localhost:3000`

## Environment Variables
Copy `.env.example` → `.env` and update values.

## Services
- API: http://localhost:8000
- Client: http://localhost:3000
- Postgres: localhost:5432
- Redis: localhost:6379
- MinIO: http://localhost:9000
- MinIO Console: http://localhost:9001

## Roadmap
- [x] Auth + tenant isolation
- Lease upload + storage
- AI extraction (terms)
- Dashboard + filters
- Payment schedule engine
- Reconciliation (rent roll vs expected)
- Forecasting
- Excel exports
- Audit logging + permissions