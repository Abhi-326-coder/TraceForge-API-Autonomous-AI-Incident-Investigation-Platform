from app.agents.gemini_log_agent import GeminiLogAgent


def log_investigation_node(state):

    agent = GeminiLogAgent()

    result = agent.investigate(
        incident=state["incident"]
    )

    return {
        "final_finding": {
            "summary": result
        }
    }
