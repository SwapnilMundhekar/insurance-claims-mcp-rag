import sys
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from mcp.server.fastmcp import FastMCP

from src.mcp_server.policy_tools import (
    get_claim_requirements,
    get_complaint_obligations,
    search_policy_documents,
)


mcp = FastMCP("insurance-policy-knowledge-server")


@mcp.tool()
def search_policy_documents_tool(query: str, top_k: int = 5) -> dict[str, Any]:
    """
    Search insurance policy and regulatory documents.

    Use this tool when the user asks about insurance coverage, exclusions,
    policy wording, claim conditions, regulatory obligations, or industry code guidance.
    """
    return search_policy_documents(query=query, top_k=top_k)


@mcp.tool()
def get_complaint_obligations_tool(query: str, top_k: int = 5) -> dict[str, Any]:
    """
    Search complaint handling and dispute resolution obligations.

    Use this tool for questions about internal dispute resolution,
    complaint timeframes, AFCA, ASIC RG 271, or customer complaint obligations.
    """
    return get_complaint_obligations(query=query, top_k=top_k)


@mcp.tool()
def get_claim_requirements_tool(query: str, top_k: int = 5) -> dict[str, Any]:
    """
    Search claim requirements, evidence needs, coverage conditions, and exclusions.

    Use this tool when the user asks what evidence, documents, conditions,
    or policy clauses matter for an insurance claim.
    """
    return get_claim_requirements(query=query, top_k=top_k)


if __name__ == "__main__":
    mcp.run()
