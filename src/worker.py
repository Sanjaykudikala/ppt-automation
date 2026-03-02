"""Slide worker — LangGraph parallel content generator for each slide."""

from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph import StateGraph, START, END
from langgraph.types import Send

from src.config import get_llm, invoke_with_retry
from src.models import GraphState, WorkerState
from src.prompts import WORKER_SYSTEM_PROMPT


def slide_worker(state: WorkerState):
    """Generate content for a single slide using the LLM."""
    llm = get_llm()

    slot_lines = "\n".join(
        f"- {s['slot_key']} ({s['type']})"
        for s in state["slots"]
    )

    response = invoke_with_retry(llm, [
        SystemMessage(content=WORKER_SYSTEM_PROMPT),
        HumanMessage(content=f"""
Slide premise:
{state['premise']}

You MUST generate content for EACH of these slots:
{slot_lines}

Generate content SLOT BY SLOT. Return ALL slots in a SINGLE JSON object.
"""),
    ])

    return {
        "completed_slides": [
            {
                "slide_id": state["slide_id"],
                "content": response.content.strip(),
            }
        ]
    }


def assign_workers(state: GraphState):
    """Fan out to parallel slide workers."""
    return [
        Send(
            "slide_worker",
            {
                "slide_id": slide["slide_id"],
                "premise": slide["premise"],
                "slots": slide["slots"],
            },
        )
        for slide in state["slides_with_slots"]
    ]


def build_graph():
    """Build and compile the LangGraph for parallel slide generation."""
    graph = StateGraph(GraphState)
    graph.add_node("slide_worker", slide_worker)
    graph.add_conditional_edges(START, assign_workers, ["slide_worker"])
    graph.add_edge("slide_worker", END)
    return graph.compile()
