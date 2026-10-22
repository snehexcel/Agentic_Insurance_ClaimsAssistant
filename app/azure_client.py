import os
from openai import OpenAI

def make_summary(claim: dict, clauses: list[dict], flags: list[str], route: str) -> tuple[str, bool]:
    fallback = (f"Demo assessment: route={route}; claim type={claim['claim_type']}; amount={claim['claimed_amount']:.2f}. "
                f"Validation flags: {', '.join(flags) if flags else 'none detected by demo rules'}. "
                "This is preliminary triage only. An authorized human reviewer must determine coverage and next steps.")
    endpoint = os.getenv("AZURE_AI_FOUNDRY_ENDPOINT", "").strip()
    api_key = os.getenv("AZURE_AI_FOUNDRY_API_KEY", "").strip()
    model = os.getenv("AZURE_AI_FOUNDRY_MODEL", "").strip()
    if not (endpoint and api_key and model):
        return fallback, False
    try:
        # Use the OpenAI-compatible endpoint and deployment/model name provided in your Azure AI Foundry project.
        client = OpenAI(base_url=endpoint.rstrip("/") + "/", api_key=api_key)
        response = client.chat.completions.create(model=model, temperature=0.1, messages=[
            {"role":"system", "content":"Summarize the supplied synthetic insurance claim and policy excerpts for a human reviewer. Use only provided facts. Never approve or deny a claim, infer coverage, or invent policy terms. State that human review is required."},
            {"role":"user", "content":f"Claim: {claim}\nPolicy excerpts: {clauses}\nValidation flags: {flags}\nRoute: {route}\nWrite a concise reviewer summary."}
        ])
        content = response.choices[0].message.content
        return (content or fallback), bool(content)
    except Exception:
        return fallback + " (Azure call failed; deterministic fallback used.)", False
