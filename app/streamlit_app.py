import json
import sys
from pathlib import Path
from typing import Any

import streamlit as st
from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from src.orchestrator.tool_orchestrator import ToolCallingOrchestrator


load_dotenv()


st.set_page_config(
    page_title="Insurance Claims MCP RAG Agent",
    page_icon=None,
    layout="wide",
)


def initialise_session_state() -> None:
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "latest_trace" not in st.session_state:
        st.session_state.latest_trace = None

    if "latest_result" not in st.session_state:
        st.session_state.latest_result = None


def extract_retrieved_sources(trace: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not trace:
        return []

    tool_execution = trace.get("tool_execution", {})
    tool_result = tool_execution.get("result", {})
    results = tool_result.get("results", [])

    if not isinstance(results, list):
        return []

    return results


def render_sidebar() -> None:
    st.sidebar.title("Project Control Plane")

    st.sidebar.markdown(
        """
        This local app demonstrates a governed tool-calling pipeline.

        The LLM proposes a tool call.  
        The orchestrator validates it.  
        The registered tool executes retrieval.  
        The final answer is generated from tool output.
        """
    )

    st.sidebar.divider()

    st.sidebar.subheader("Local Runtime")

    st.sidebar.code(
        """
LLM: Ollama
Embeddings: Ollama nomic-embed-text
Vector Store: Local NumPy
Tool Layer: MCP-style policy tools
Orchestrator: Python validation layer
        """.strip()
    )

    st.sidebar.divider()

    st.sidebar.subheader("Example Questions")

    example_questions = [
        "Is accidental damage covered under car insurance?",
        "What evidence is required for a car insurance claim?",
        "What are complaint handling obligations under ASIC RG 271?",
        "What does CPS 230 say about operational risk management?",
        "What does the General Insurance Code of Practice say about claims handling?",
    ]

    for question in example_questions:
        if st.sidebar.button(question, use_container_width=True):
            st.session_state.pending_question = question

    st.sidebar.divider()

    if st.sidebar.button("Clear chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.latest_trace = None
        st.session_state.latest_result = None
        st.rerun()


def render_header() -> None:
    st.title("MCP-Based Insurance Claims RAG Agent")

    st.markdown(
        """
        Local-first enterprise AI agent for insurance policy intelligence, retrieval,
        governed tool-calling, and traceable answers.
        """
    )

    st.info(
        "This app does not make final claim, legal, or regulatory decisions. "
        "It answers only from retrieved policy and regulatory context."
    )


def render_trace_panel(result: dict[str, Any] | None) -> None:
    st.subheader("Tool Call Trace")

    if not result:
        st.caption("No trace yet. Ask a question first.")
        return

    selected_tool = result.get("selected_tool", "unknown")
    tool_arguments = result.get("tool_arguments", {})
    tool_result_count = result.get("tool_result_count", 0)
    trace_path = result.get("trace_path", "not available")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Selected Tool", selected_tool)

    with col2:
        st.metric("Tool Results", tool_result_count if tool_result_count is not None else 0)

    with col3:
        st.metric("Trace Saved", "Yes" if trace_path else "No")

    st.markdown("**Tool Arguments**")
    st.json(tool_arguments)

    st.markdown("**Trace Path**")
    st.code(trace_path)


def render_sources_panel(trace: dict[str, Any] | None) -> None:
    st.subheader("Retrieved Sources")

    sources = extract_retrieved_sources(trace)

    if not sources:
        st.caption("No retrieved sources yet.")
        return

    for source in sources:
        title = f"{source.get('rank', '-')}. {source.get('document_name', 'Unknown document')}"

        with st.expander(title, expanded=False):
            col1, col2 = st.columns(2)

            with col1:
                st.write("**Document type:**", source.get("document_type"))
                st.write("**Provider / Regulator:**", source.get("provider_or_regulator"))
                st.write("**Chunk type:**", source.get("chunk_type"))

            with col2:
                st.write("**Section:**", source.get("section_title"))
                st.write("**Pages:**", f"{source.get('start_page')} - {source.get('end_page')}")
                st.write("**Sources:**", source.get("source_references"))

            st.markdown("**Preview**")
            st.text(source.get("text_preview", "")[:1500])


def render_raw_trace(trace: dict[str, Any] | None) -> None:
    st.subheader("Raw Trace JSON")

    if not trace:
        st.caption("No raw trace available yet.")
        return

    with st.expander("Open raw trace", expanded=False):
        st.json(trace)


def run_agent(question: str) -> dict[str, Any]:
    orchestrator = ToolCallingOrchestrator(
        trace_dir=Path("./logs"),
    )

    return orchestrator.run(question)


def render_chat() -> None:
    st.subheader("Chat")

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    pending_question = st.session_state.pop("pending_question", None)

    user_input = st.chat_input("Ask an insurance policy, claims, complaint, or risk question")

    question = pending_question or user_input

    if not question:
        return

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question,
        }
    )

    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.status("Running governed tool-calling pipeline...", expanded=True):
            st.write("Selecting tool with local LLM...")
            st.write("Validating tool name and arguments...")
            st.write("Executing approved policy tool...")
            st.write("Generating final grounded answer...")

            try:
                result = run_agent(question)
                answer = result["answer"]

                st.session_state.latest_result = result
                st.session_state.latest_trace = result.get("trace")

                st.markdown(answer)

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer,
                    }
                )

            except Exception as error:
                error_message = f"Pipeline failed: {error}"
                st.error(error_message)

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": error_message,
                    }
                )


def main() -> None:
    initialise_session_state()
    render_sidebar()
    render_header()

    left_col, right_col = st.columns([1.2, 0.8])

    with left_col:
        render_chat()

    with right_col:
        render_trace_panel(st.session_state.latest_result)
        st.divider()
        render_sources_panel(st.session_state.latest_trace)
        st.divider()
        render_raw_trace(st.session_state.latest_trace)


if __name__ == "__main__":
    main()
