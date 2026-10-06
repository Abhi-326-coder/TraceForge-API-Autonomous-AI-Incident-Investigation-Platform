from langgraph.graph import StateGraph, START, END

from app.graph.state import InvestigationState
from app.graph.nodes import log_investigation_node


def build_investigation_graph():

    graph = StateGraph(InvestigationState)

    graph.add_node(
        "log_investigation",
        log_investigation_node,
    )

    graph.add_edge(
        START,
        "log_investigation",
    )

    graph.add_edge(
        "log_investigation",
        END,
    )

    return graph.compile()