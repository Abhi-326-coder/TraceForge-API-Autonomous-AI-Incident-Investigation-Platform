import json
from app.config import settings

from app.agents.tools.log_tools import (
    SEARCH_LOGS_TOOL,
    execute_search_logs,
)
from app.db.models import Incident
from app.llm.gemini import GeminiClient


class GeminiLogAgent:

    def __init__(self):
        self.gemini = None if settings.demo_mode else GeminiClient()

    def investigate(self, incident: dict):

        if settings.demo_mode:
            return (
                "DEMO evidence: checkout-api logs show database connection pool exhaustion "
                "followed by failed checkout transactions and HTTP 500 responses. "
                "This supports connection pool saturation as the immediate failure mode."
            )

        prompt = f"""
You are a production incident investigation agent.

Investigate this incident.

Incident ID:
{incident["external_id"]}

Title:
{incident["title"]}

Description:
{incident["description"]}

Service:
{incident["service"]}

Severity:
{incident["severity"]}

Use the available tools to investigate the incident.

Do not invent evidence.

Return a concise investigation summary.
"""

        interaction = self.gemini.client.interactions.create(
            model=self.gemini.model,
            input=prompt,
            tools=[SEARCH_LOGS_TOOL],
        )

        while True:

            function_calls = [
                step
                for step in interaction.steps
                if step.type == "function_call"
            ]

            if not function_calls:
                break

            for call in function_calls:

                print(
                    f"[Gemini] Tool call: "
                    f"{call.name}({call.arguments})"
                )

                if call.name == "search_logs":

                    arguments = call.arguments

                    result = execute_search_logs(
                        service=arguments["service"],
                        query=arguments.get("query"),
                    )

                else:
                    result = {
                        "error": f"Unknown tool: {call.name}"
                    }

                interaction = self.gemini.client.interactions.create(
                    model=self.gemini.model,
                    previous_interaction_id=interaction.id,
                    tools=[SEARCH_LOGS_TOOL],
                    input=[
                        {
                            "type": "function_result",
                            "name": call.name,
                            "call_id": call.id,
                            "result": [
                                {
                                    "type": "text",
                                    "text": json.dumps(result),
                                }
                            ],
                        }
                    ],
                )

        return interaction.output_text
