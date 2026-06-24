import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from src.mcp_server.policy_tools import (
    get_claim_requirements,
    get_complaint_obligations,
    search_policy_documents,
)


def print_result(title: str, payload: dict) -> None:
    print("=" * 100)
    print(title)
    print("=" * 100)
    print(json.dumps(payload, indent=2, ensure_ascii=False)[:4000])
    print()


def main() -> None:
    policy_result = search_policy_documents(
        query="Is accidental damage covered under car insurance?",
        top_k=3,
    )

    claim_result = get_claim_requirements(
        query="What evidence is required for a car insurance claim?",
        top_k=3,
    )

    complaint_result = get_complaint_obligations(
        query="What are complaint handling obligations under RG 271?",
        top_k=3,
    )

    print_result("Policy Search Tool Result", policy_result)
    print_result("Claim Requirements Tool Result", claim_result)
    print_result("Complaint Obligations Tool Result", complaint_result)


if __name__ == "__main__":
    main()
