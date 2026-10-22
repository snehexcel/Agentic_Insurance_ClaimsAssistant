from typing import Literal
from pydantic import BaseModel, Field, ConfigDict

ClaimType = Literal["auto", "home", "health", "travel", "other"]

class ClaimRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    claimant_name: str = Field(min_length=2, max_length=100)
    policy_number: str = Field(min_length=4, max_length=40, pattern=r"^[A-Za-z0-9-]+$")
    claim_type: ClaimType
    incident_description: str = Field(min_length=10, max_length=3000)
    claimed_amount: float = Field(gt=0, le=10_000_000)
    incident_date: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")
    documents_provided: list[str] = Field(default_factory=list, max_length=30)

class ClaimResponse(BaseModel):
    case_id: str
    status: str
    route: str
    missing_information: list[str]
    validation_flags: list[str]
    triage_score: int
    triage_level: str
    policy_clauses: list[dict[str, str]]
    reviewer_summary: str
    azure_summary_used: bool = False

class EvaluationResponse(BaseModel):
    total_cases: int
    route_accuracy: float
    expected_flag_recall: float
    results: list[dict]
