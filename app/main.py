from dotenv import load_dotenv
load_dotenv()

from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from .schemas import ClaimRequest, ClaimResponse, EvaluationResponse
from .workflow import process_claim
from . import storage
from .evaluate import run_evaluation

@asynccontextmanager
async def lifespan(app: FastAPI):
    storage.init_db()
    yield

app=FastAPI(title="Agentic Insurance Claims Assistant", description="Synthetic LangGraph claims triage demo; not for real insurance decisions.", version="1.0.0", lifespan=lifespan)

@app.get("/health")
def health(): return {"status":"ok","service":"agentic-insurance-claims-assistant"}

@app.get("/", response_class=HTMLResponse)
def home(): return HTMLResponse((Path(__file__).parent/"templates"/"index.html").read_text(encoding="utf-8"))

@app.post("/api/claims", response_model=ClaimResponse)
def create_claim(request: ClaimRequest):
    claim=request.model_dump()
    result=process_claim(claim); result["claim"]=claim
    storage.save_case(result["case_id"], result.get("status","unknown"), result)
    return {key:result.get(key, default) for key,default in {"case_id":"CLM-UNKNOWN","status":"unknown","route":"human_review","missing_information":[],"validation_flags":[],"triage_score":0,"triage_level":"low","policy_clauses":[],"reviewer_summary":"","azure_summary_used":False}.items()}

@app.get("/api/claims")
def list_claims(): return storage.list_cases()

@app.get("/api/claims/{case_id}")
def get_claim(case_id: str):
    result=storage.get_case(case_id)
    if result is None: raise HTTPException(status_code=404, detail="Case not found")
    return result

@app.post("/api/evaluate", response_model=EvaluationResponse)
def evaluate(): return run_evaluation()
