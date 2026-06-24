import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.llm.ollama_client import OllamaChatClient
from src.orchestrator.tool_call_parser import extract_json_object, validate_tool_call
from src.orchestrator.tool_registry import build_tool_prompt, get_tool_registry


TOOL_SELECTION_SYSTEM_PROMPT = """
You are a tool-selection planner for an insurance claims and policy assistant.

Your job is to select exactly one tool from the available tool registry.

Return JSON only.

Required JSON format:
{
  "tool_name": "name_of_tool",
  "arguments": {
    "query": "search query to send to the tool",
    "top_k": 5
  }
}

Rules:
1. Do not answer the user directly.
2. Do not invent tool names.
3. Use only the tools provided.
4. Choose the most relevant tool for the user question.
5. Keep query concise and specific.
6. top_k must be an integer between 1 and 10.
"""


FINAL_ANSWER_SYSTEM_PROMPT = """
You are an insurance policy and claims assistant.

You must answer only from the tool result provided by the application.

Rules:
1. Do not invent policy wording, claim outcomes, legal obligations, or timeframes.
2. Say "based on the retrieved context" when answering.
3. If the tool result is insufficient, say the retrieved context is insufficient.
4. Include document names and source references where available.
5. Do not present a final legal or claim decision.
6. Keep the answer structured and practical.
"""


class ToolCallingOrchestrator:
    """
    Governed tool-calling orchestrator.

    The LLM proposes a tool call.
    The orchestrator validates it.
    The approved registered tool executes.
    The result is returned to the LLM for final grounded response.
    """

    def __init__(self, trace_dir: Path = Path("./logs")) -> None:
        self.llm_client = OllamaChatClient()
        self.tool_registry = get_tool_registry()
        self.trace_dir = Path(trace_dir)
        self.trace_dir.mkdir(parents=True, exist_ok=True)

    def select_tool(self, user_question: str) -> dict[str, Any]:
        tool_definitions = build_tool_prompt()

        user_prompt = f"""
User question:
{user_question}

Available tools:
{tool_definitions}

Select the single best tool and return JSON only.
""".strip()

        llm_output = self.llm_client.chat(
            system_prompt=TOOL_SELECTION_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            temperature=0.0,
        )

        parsed_tool_call = extract_json_object(llm_output)
        validated_tool_call = validate_tool_call(parsed_tool_call)

        return {
            "raw_llm_output": llm_output,
            "tool_call": validated_tool_call,
        }

    def execute_tool(self, tool_call: dict[str, Any]) -> dict[str, Any]:
        tool_name = tool_call["tool_name"]
        arguments = tool_call["arguments"]

        if tool_name not in self.tool_registry:
            raise ValueError(f"Tool is not registered or not allowed: {tool_name}")

        tool = self.tool_registry[tool_name]

        if tool.risk_level != "low":
            raise PermissionError(
                f"Tool requires approval before execution: {tool_name}"
            )

        result = tool.function(**arguments)

        return {
            "tool_name": tool_name,
            "risk_level": tool.risk_level,
            "arguments": arguments,
            "result": result,
        }

    def generate_final_answer(
        self,
        user_question: str,
        tool_execution: dict[str, Any],
    ) -> str:
        user_prompt = f"""
User question:
{user_question}

Tool execution result:
{json.dumps(tool_execution, ensure_ascii=False, indent=2)}

Now produce the final answer using only the tool result.
""".strip()

        return self.llm_client.chat(
            system_prompt=FINAL_ANSWER_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            temperature=0.1,
        )

    def save_trace(self, trace_payload: dict[str, Any]) -> Path:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        trace_path = self.trace_dir / f"tool_trace_{timestamp}.json"

        with trace_path.open("w", encoding="utf-8") as file:
            json.dump(trace_payload, file, ensure_ascii=False, indent=2)

        return trace_path

    def run(self, user_question: str) -> dict[str, Any]:
        started_at = datetime.now(timezone.utc).isoformat()

        tool_selection = self.select_tool(user_question)
        tool_execution = self.execute_tool(tool_selection["tool_call"])
        final_answer = self.generate_final_answer(user_question, tool_execution)

        completed_at = datetime.now(timezone.utc).isoformat()

        trace_payload = {
            "started_at_utc": started_at,
            "completed_at_utc": completed_at,
            "user_question": user_question,
            "tool_selection": tool_selection,
            "tool_execution": tool_execution,
            "final_answer": final_answer,
        }

        trace_path = self.save_trace(trace_payload)

        return {
            "answer": final_answer,
            "selected_tool": tool_selection["tool_call"]["tool_name"],
            "tool_arguments": tool_selection["tool_call"]["arguments"],
            "tool_result_count": tool_execution["result"].get("result_count"),
            "trace_path": str(trace_path),
            "trace": trace_payload,
        }
