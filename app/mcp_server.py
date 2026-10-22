from mcp.server.fastmcp import FastMCP
from .policy import search_policy_clauses
from .workflow import process_claim
mcp = FastMCP("agentic-insurance-claims-demo")

@mcp.tool()
def search_policy_clauses_tool(claim_type: str, query: str = "") -> list[dict[str, str]]:
    """Search synthetic sample policy clauses by claim type and query."""
    return search_policy_clauses(claim_type, query)

@mcp.tool()
def triage_claim_tool(claimant_name: str, policy_number: str, claim_type: str, incident_description: str, claimed_amount: float, incident_date: str, documents_provided: list[str]) -> dict:
    """Run demo LangGraph triage on synthetic data. Human review is always required."""
    return process_claim({"claimant_name":claimant_name,"policy_number":policy_number,"claim_type":claim_type,"incident_description":incident_description,"claimed_amount":claimed_amount,"incident_date":incident_date,"documents_provided":documents_provided})

if __name__ == "__main__": mcp.run(transport="stdio")
