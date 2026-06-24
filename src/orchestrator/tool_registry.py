from dataclasses import dataclass
from typing import Any, Callable

from src.mcp_server.policy_tools import (
    get_claim_requirements,
    get_complaint_obligations,
    search_policy_documents,
)


@dataclass
class ToolDefinition:
    name: str
    description: str
    input_schema: dict[str, Any]
    risk_level: str
    function: Callable[..., dict[str, Any]]


def get_tool_registry() -> dict[str, ToolDefinition]:
    """
    Returns the approved tool registry.

    The LLM can propose tool calls, but only tools in this registry can execute.
    """
    return {
        "search_policy_documents": ToolDefinition(
            name="search_policy_documents",
            description="Search insurance policy and regulatory documents for coverage, exclusions, clauses, and obligations.",
            input_schema={
                "query": "string",
                "top_k": "integer",
            },
            risk_level="low",
            function=search_policy_documents,
        ),
        "get_claim_requirements": ToolDefinition(
            name="get_claim_requirements",
            description="Search for claim evidence, required documents, claim conditions, coverage clauses, and exclusions.",
            input_schema={
                "query": "string",
                "top_k": "integer",
            },
            risk_level="low",
            function=get_claim_requirements,
        ),
        "get_complaint_obligations": ToolDefinition(
            name="get_complaint_obligations",
            description="Search complaint handling, internal dispute resolution, ASIC RG 271, AFCA, and Code of Practice obligations.",
            input_schema={
                "query": "string",
                "top_k": "integer",
            },
            risk_level="low",
            function=get_complaint_obligations,
        ),
    }


def build_tool_prompt() -> str:
    """
    Builds a readable tool definition block for the LLM.
    """
    registry = get_tool_registry()

    lines = []

    for tool in registry.values():
        lines.append(f"Tool name: {tool.name}")
        lines.append(f"Description: {tool.description}")
        lines.append(f"Input schema: {tool.input_schema}")
        lines.append(f"Risk level: {tool.risk_level}")
        lines.append("")

    return "\n".join(lines).strip()
