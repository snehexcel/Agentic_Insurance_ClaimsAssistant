# Agentic Insurance Claims Assistant

Runnable portfolio demo for an Agentic AI Engineer role. Demonstrates LangGraph StateGraph and conditional routing, specialized workflow agents, Pydantic validation, FastAPI, PostgreSQL/SQLite persistence, Docker, MCP tools, and a basic evaluation harness. Azure AI Foundry summarization is optional; the core demo runs without keys.

**Synthetic data only.** This is an educational triage demo, not an insurance decision system. It never approves or denies a claim; every case is routed for human review or to request missing information.

## Run on Windows with Docker (recommended)
1. Install and open Docker Desktop.
2. Extract this ZIP and open PowerShell in `agentic_insurance_claims_assistant`.
3. Run `docker compose up --build`.
4. Open http://localhost:8000 (UI), http://localhost:8000/docs (API docs), or http://localhost:8000/health.
5. Stop with Ctrl+C; use `docker compose down` to stop containers.

## Run locally without Docker
Requires Python 3.11 (recommended). In PowerShell in the project folder:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload
```
If PowerShell blocks activation: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`, then activate again. Local mode uses SQLite by default.

## Test it
Use the prefilled UI form and click **Run agent workflow**. Endpoints: `GET /health`, `POST /api/claims`, `GET /api/claims`, `GET /api/claims/{case_id}`, and `POST /api/evaluate`.

Run tests/evaluation:

```powershell
python -m app.evaluate
pytest -q
```
The evaluation set is a small deterministic regression check, not a validated benchmark.

## MCP server
After installing requirements, run `python -m app.mcp_server` in a second terminal. It uses stdio and exposes `search_policy_clauses_tool` and `triage_claim_tool` for MCP-compatible clients. The tools use synthetic sample policy content only.

## Optional Azure AI Foundry
The project works without Azure credentials. To enable model-generated summaries, configure the OpenAI-compatible endpoint and model/deployment name supplied by your Azure AI Foundry deployment in `.env`:

```env
AZURE_AI_FOUNDRY_ENDPOINT=https://YOUR-OPENAI-COMPATIBLE-ENDPOINT/v1
AZURE_AI_FOUNDRY_API_KEY=your-key
AZURE_AI_FOUNDRY_MODEL=your-deployment-or-model-name
```
Endpoint formats vary; use the exact endpoint and instructions shown in your Azure project. If configuration is absent or a call fails, the app uses a deterministic fallback. Never commit keys to GitHub.

## Deploy
Push to GitHub, create a Docker web service on a Docker-capable host such as Render or Railway, attach managed PostgreSQL, and set `DATABASE_URL` to its SQLAlchemy-compatible connection string (e.g. `postgresql+psycopg://...`). Set any API keys as host secrets, not in source. Check `/health` after deployment. Before real-world data use, add authentication, authorization, rate limiting, audit logging, privacy controls, monitoring, backups, migrations, and security review.

## Architecture
Browser/API -> FastAPI + Pydantic -> LangGraph StateGraph: Policy Retrieval Agent -> Claim Validation Agent -> Rule-Based Risk Triage Agent -> conditional route (`needs_information` or `human_review`) -> Response Agent (optional Azure summary) -> PostgreSQL in Docker or SQLite locally. A separate MCP stdio server exposes policy-search and triage tools.

