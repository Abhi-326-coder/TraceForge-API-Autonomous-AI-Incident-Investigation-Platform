from app.agents.gemini_log_agent import GeminiLogAgent
from app.agents.supervisor_agent import SupervisorAgent
from app.agents.root_cause_agent import (
    RootCauseAgent,
)

def log_investigation_node(state):
    
    agent = GeminiLogAgent()

    result = agent.investigate(
        incident=state["incident"]
    )

    return {
        "findings": [
            {
                "agent": "logs",
                "summary": result,
            }
        ]
    }
    
def supervisor_node(state):

    supervisor = SupervisorAgent()

    plan = supervisor.create_plan(
        incident=state["incident"]
    )

    return {
        "investigation_plan": plan,
        "next_agent": plan[0] if plan else None,
        "investigation_complete": not bool(plan),
    }

def route_after_supervisor(state):

    next_agent = state.get("next_agent")

    if next_agent == "logs":
        return "log_investigation"

    if next_agent == "metrics":
        return "metrics_investigation"

    if next_agent == "code":
        return "code_investigation"

    return "end"

def metrics_investigation_node(state):

    return {
        "findings": [
            {
                "agent": "metrics",
                "status": "pending",
                "message": (
                    "Metrics Agent will be implemented next."
                ),
            }
        ]
    }


def code_investigation_node(state):

    return {
        "findings": [
            {
                "agent": "code",
                "status": "pending",
                "message": (
                    "Code Agent will be implemented later."
                ),
            }
        ]
    }
    
def advance_investigation_node(state):

    plan = state.get(
        "investigation_plan",
        [],
    )

    current = state.get(
        "next_agent"
    )

    if current in plan:

        current_index = plan.index(
            current
        )

        next_index = current_index + 1

        if next_index < len(plan):

            return {
                "next_agent": plan[next_index],
            }

    return {
        "next_agent": None,
        "investigation_complete": True,
    }
    
def root_cause_node(state):

    agent = RootCauseAgent()

    result = agent.analyze(
        evidence=state.get(
            "evidence",
            [],
        )
    )

    return {
        "final_finding": result.model_dump()
    }