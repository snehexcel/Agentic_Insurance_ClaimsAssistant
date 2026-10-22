from datetime import date
from app.workflow import process_claim

def valid_claim(**overrides):
    claim={"claimant_name":"Asha Verma","policy_number":"POL-1001","claim_type":"auto","incident_description":"Rear bumper damage after a low-speed collision in a parking area.","claimed_amount":1800,"incident_date":date.today().isoformat(),"documents_provided":["incident_report","repair_estimate"]}
    claim.update(overrides); return claim

def test_complete_claim_routes_to_human_review():
    result=process_claim(valid_claim())
    assert result["route"]=="human_review" and result["status"]=="pending_human_review"
    assert result["triage_score"] >= 0 and result["policy_clauses"]

def test_missing_documents_routes_to_information():
    result=process_claim(valid_claim(documents_provided=[]))
    assert result["route"]=="needs_information" and "incident_report" in result["missing_information"]

def test_high_value_claim_flagged():
    result=process_claim(valid_claim(claimed_amount=30000))
    assert any("high-value" in flag for flag in result["validation_flags"])
