import sys
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from src.orchestrator.tool_orchestrator import ToolCallingOrchestrator


def main() -> None:
    load_dotenv()

    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])
    else:
        question = "Is accidental damage covered under car insurance?"

    print("Starting governed tool-calling orchestrator...", flush=True)
    print(f"Question: {question}", flush=True)

    orchestrator = ToolCallingOrchestrator(
        trace_dir=Path("./logs"),
    )

    result = orchestrator.run(question)

    print("\nSelected tool:")
    print(result["selected_tool"])

    print("\nTool arguments:")
    print(result["tool_arguments"])

    print("\nTool result count:")
    print(result["tool_result_count"])

    print("\nFinal answer:\n")
    print(result["answer"])

    print("\nTrace saved to:")
    print(result["trace_path"])


if __name__ == "__main__":
    main()
