import json
import re
from typing import Any


def extract_json_object(text: str) -> dict[str, Any]:
    """
    Extracts the first JSON object from an LLM response.

    The model should return JSON only, but this gives us a safe fallback
    if it wraps the JSON in text or markdown.
    """
    text = text.strip()

    if text.startswith("```"):
        text = re.sub(r"^```json", "", text, flags=re.IGNORECASE).strip()
        text = re.sub(r"^```", "", text).strip()
        text = re.sub(r"```$", "", text).strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{.*\}", text, flags=re.DOTALL)

    if not match:
        raise ValueError(f"No JSON object found in LLM output: {text}")

    return json.loads(match.group(0))


def validate_tool_call(tool_call: dict[str, Any]) -> dict[str, Any]:
    """
    Validates the basic tool-call envelope.

    Expected:
    {
      "tool_name": "search_policy_documents",
      "arguments": {
        "query": "...",
        "top_k": 5
      }
    }
    """
    if "tool_name" not in tool_call:
        raise ValueError("Tool call missing required field: tool_name")

    if "arguments" not in tool_call:
        raise ValueError("Tool call missing required field: arguments")

    if not isinstance(tool_call["tool_name"], str):
        raise TypeError("tool_name must be a string")

    if not isinstance(tool_call["arguments"], dict):
        raise TypeError("arguments must be an object/dictionary")

    arguments = tool_call["arguments"]

    if "query" not in arguments:
        raise ValueError("arguments missing required field: query")

    if not isinstance(arguments["query"], str):
        raise TypeError("arguments.query must be a string")

    if "top_k" not in arguments:
        arguments["top_k"] = 5

    if not isinstance(arguments["top_k"], int):
        raise TypeError("arguments.top_k must be an integer")

    if arguments["top_k"] < 1 or arguments["top_k"] > 10:
        raise ValueError("arguments.top_k must be between 1 and 10")

    return {
        "tool_name": tool_call["tool_name"],
        "arguments": arguments,
    }
