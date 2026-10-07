from langgraph.graph import StateGraph, START, END

from app.graph.state import InvestigationState
from app.graph.nodes import (
    supervisor_node,
    advance_investigation_node,
    log_investigation_node,
    metrics_investigation_node,
    code_investigation_node,
    route_after_supervisor
)

def route_after_agent(state):

    if state.get(
        "investigation_complete"
    ):
        return "end"

    next_agent = state.get(
        "next_agent"
    )

    if next_agent == "logs":
        return "log_investigation"

    if next_agent == "metrics":
        return "metrics_investigation"

    if next_agent == "code":
        return "code_investigation"

    return "end"


def build_investigation_graph():
    
    graph = StateGraph(
        InvestigationState
    )
    
    graph.add_node(
        "supervisor",
        supervisor_node,
    )

    graph.add_node(
        "log_investigation",
        log_investigation_node,
    )

    graph.add_node(
        "metrics_investigation",
        metrics_investigation_node,
    )

    graph.add_node(
        "code_investigation",
        code_investigation_node,
    )

    graph.add_node(
        "advance_investigation",
        advance_investigation_node,
    )
    
    graph.add_edge(
        START,
        "supervisor"
    )
    
    graph.add_conditional_edges(
        "supervisor",
        route_after_supervisor,
        {
            "log_investigation":
                "log_investigation",

            "metrics_investigation":
                "metrics_investigation",

            "code_investigation":
                "code_investigation",

            "end":
                END,
        },
    )
    
    graph.add_edge(
        "log_investigation",
        "advance_investigation",
    )
    
    graph.add_edge(
        "metrics_investigation",
        "advance_investigation",
    )

    graph.add_edge(
        "code_investigation",
        "advance_investigation",
    )
    
    graph.add_conditional_edges(
        "advance_investigation",
        route_after_agent,
        {
            "log_investigation":
                "log_investigation",

            "metrics_investigation":
                "metrics_investigation",

            "code_investigation":
                "code_investigation",

            "end":
                END,
        },
    )

    
    