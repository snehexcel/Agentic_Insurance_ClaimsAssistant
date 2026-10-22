# Synthetic sample policy text only; these are not real insurance policy terms.
POLICIES = {
    "auto": [
        {"id":"AUTO-01", "title":"Incident details", "text":"Record the incident date, event description, and reported damage."},
        {"id":"AUTO-02", "title":"Supporting documents", "text":"A sample auto claim may require an incident report, photographs, and a repair estimate. Request missing items rather than automatically denying a claim."},
        {"id":"AUTO-03", "title":"Human review", "text":"Coverage, liability, and payment decisions require an authorized human claims professional."}],
    "home": [
        {"id":"HOME-01", "title":"Property loss details", "text":"Record the incident date, affected property, and description of the reported loss."},
        {"id":"HOME-02", "title":"Supporting documents", "text":"A sample property claim may require photographs and repair estimates."},
        {"id":"HOME-03", "title":"Human review", "text":"Coverage and settlement decisions require authorized human review."}],
    "health": [
        {"id":"HLTH-01", "title":"Medical claim details", "text":"Record service date, provider details, and itemized bills or receipts where applicable."},
        {"id":"HLTH-02", "title":"Supporting documents", "text":"Identify missing records for follow-up; this demo does not infer medical necessity or coverage."},
        {"id":"HLTH-03", "title":"Human review", "text":"Health coverage and payment decisions require authorized human review."}],
    "travel": [
        {"id":"TRVL-01", "title":"Travel incident details", "text":"Describe the event, relevant dates, and claimed loss."},
        {"id":"TRVL-02", "title":"Supporting documents", "text":"A sample travel claim may require booking confirmations, receipts, or carrier documentation."},
        {"id":"TRVL-03", "title":"Human review", "text":"Coverage and settlement decisions require human review."}],
    "other": [
        {"id":"GEN-01", "title":"Claim details", "text":"Include incident description, date, claimed amount, and relevant supporting documents."},
        {"id":"GEN-02", "title":"Human review", "text":"Coverage and payment decisions require authorized human review."}]
}
REQUIRED_DOCS = {"auto":{"incident_report","repair_estimate"}, "home":{"photos","repair_estimate"}, "health":{"itemized_bill"}, "travel":{"receipts"}, "other":set()}

def search_policy_clauses(claim_type: str, query: str = "") -> list[dict[str, str]]:
    clauses = POLICIES.get(claim_type, POLICIES["other"])
    terms = [w.lower().strip(".,!?;:") for w in query.split() if len(w) > 3]
    scored = [(sum(term in (c["title"] + " " + c["text"]).lower() for term in terms), c) for c in clauses]
    scored.sort(key=lambda pair: pair[0], reverse=True)
    matches = [clause for score, clause in scored if score > 0]
    return matches[:3] if matches else clauses[:3]
