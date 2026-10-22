from typing import TypedDict, Any
from uuid import uuid4
from datetime import date
from langgraph.graph import StateGraph, END
from .policy import search_policy_clauses, REQUIRED_DOCS
from .azure_client import make_summary

class ClaimState(TypedDict, total=False):
    case_id: str
    claim: dict[str, Any]
    policy_clauses: list[dict[str, str]]
    missing_information: list[str]
    validation_flags: list[str]
    triage_score: int
    triage_level: str
    route: str
    status: str
    reviewer_summary: str
    azure_summary_used: bool

def policy_retrieval_agent(state: ClaimState) -> dict:
    claim = state["claim"]
    return {"policy_clauses": search_policy_clauses(claim["claim_type"], claim["incident_description"])}

def claim_validation_agent(state: ClaimState) -> dict:
    claim = state["claim"]
    provided = {str(doc).lower().strip().replace(" ", "_") for doc in claim.get("documents_provided", [])}
    missing = sorted(REQUIRED_DOCS.get(claim["claim_type"], set()) - provided)
    flags: list[str] = []
    if missing: flags.append("Required demo document(s) not listed: " + ", ".join(missing))
    if claim.get("claimed_amount", 0) > 25000: flags.append("Claim amount exceeds the demo high-value review threshold.")
    try:
        if date.fromisoformat(str(claim.get("incident_date"))) > date.today(): flags.append("Incident date is in the future.")
    except (TypeError, ValueError): flags.append("Incident date could not be parsed.")
    if len(claim.get("incident_description", "").strip()) < 20: flags.append("Incident description may need more detail.")
    return {"missing_information": missing, "validation_flags": flags}

def risk_triage_agent(state: ClaimState) -> dict:
    claim = state["claim"]; flags = state.get("validation_flags", [])
    score = 10 + min(35, len(state.get("missing_information", [])) * 12)
    if claim.get("claimed_amount", 0) > 25000: score += 25
    if any("future" in flag.lower() for flag in flags): score += 20
    if any("detail" in flag.lower() for flag in flags): score += 10
    score = min(100, score)
    return {"triage_score":score, "triage_level":"high" if score >= 60 else "medium" if score >= 30 else "low"}

def route_claim(state: ClaimState) -> str:
    return "needs_information" if state.get("missing_information") else "human_review"

def needs_information_node(state: ClaimState) -> dict:
    return {"route":"needs_information", "status":"needs_information"}

def human_review_node(state: ClaimState) -> dict:
    return {"route":"human_review", "status":"pending_human_review"}

def response_agent(state: ClaimState) -> dict:
    summary, used = make_summary(state["claim"], state.get("policy_clauses", []), state.get("validation_flags", []), state.get("route", "human_review"))
    return {"reviewer_summary":summary, "azure_summary_used":used}

def build_graph():
    graph = StateGraph(ClaimState)
    graph.add_node("policy_retrieval_agent", policy_retrieval_agent)
    graph.add_node("claim_validation_agent", claim_validation_agent)
    graph.add_node("risk_triage_agent", risk_triage_agent)
    graph.add_node("needs_information", needs_information_node)
    graph.add_node("human_review", human_review_node)
    graph.add_node("response_agent", response_agent)
    graph.set_entry_point("policy_retrieval_agent")
    graph.add_edge("policy_retrieval_agent", "claim_validation_agent")
    graph.add_edge("claim_validation_agent", "risk_triage_agent")
    graph.add_conditional_edges("risk_triage_agent", route_claim, {"needs_information":"needs_information", "human_review":"human_review"})
    graph.add_edge("needs_information", "response_agent")
    graph.add_edge("human_review", "response_agent")
    graph.add_edge("response_agent", END)
    return graph.compile()

workflow = build_graph()

def process_claim(claim: dict) -> dict:
    case_id = "CLM-" + uuid4().hex[:10].upper()
    final = workflow.invoke({"case_id":case_id, "claim":claim})
    final.pop("claim", None)
    return final
