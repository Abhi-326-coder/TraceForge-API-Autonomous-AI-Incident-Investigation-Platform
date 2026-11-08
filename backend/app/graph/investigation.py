
from langgraph.graph import StateGraph, START, END

from app.graph.state import InvestigationState

from app.graph.nodes import (
    supervisor_node,
    log_investigation_node,
    metrics_investigation_node,
    code_investigation_node,
    advance_investigation_node,
    root_cause_node,
)


def route_after_supervisor(state):
    next_agent = state.get("next_agent")

    if next_agent == "logs":
        return "logs"

    if next_agent == "metrics":
        return "metrics"

    if next_agent == "code":
        return "code"

    return "root_cause"


def route_after_agent(state):
    if state.get("next_agent") == "root_cause":
        return "root_cause"

    return state.get("next_agent")


def build_investigation_graph(checkpointer):
    graph = StateGraph(InvestigationState)

    graph.add_node("supervisor", supervisor_node)
    graph.add_node("logs", log_investigation_node)
    graph.add_node("metrics", metrics_investigation_node)
    graph.add_node("code", code_investigation_node)
    graph.add_node("advance", advance_investigation_node)
    graph.add_node("root_cause", root_cause_node)

    graph.add_edge(START, "supervisor")

    graph.add_conditional_edges(
        "supervisor",
        route_after_supervisor,
        {
            "logs": "logs",
            "metrics": "metrics",
            "code": "code",
            "root_cause": "root_cause",
        },
    )

    graph.add_edge("logs", "advance")
    graph.add_edge("metrics", "advance")
    graph.add_edge("code", "advance")

    graph.add_conditional_edges(
        "advance",
        route_after_agent,
        {
            "logs": "logs",
            "metrics": "metrics",
            "code": "code",
            "root_cause": "root_cause",
        },
    )

    graph.add_edge("root_cause", END)

    return graph.compile(checkpointer=checkpointer)
