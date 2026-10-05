import json

from app.agents.tools.log_tools import (
    SEARCH_LOGS_TOOL,
    execute_search_logs,
)
from app.db.models import Incident
from app.llm.gemini import GeminiClient


class GeminiLogAgent:

    def __init__(self):
        self.gemini = GeminiClient()

    def investigate(self, incident: Incident):

        prompt = f"""
You are a production incident investigation agent.

Investigate the following software incident.

Incident:
ID: {incident.external_id}
Title: {incident.title}
Description: {incident.description}
Service: {incident.service}
Severity: {incident.severity}

Your job is to investigate the incident using available tools.

Rules:
1. Search logs when runtime evidence is needed.
2. Decide yourself what queries are useful.
3. You may call the same tool multiple times with different queries.
4. Do not invent evidence.
5. Base your conclusion only on tool results.
6. Once you have enough evidence, stop investigating.

Return a concise investigation summary containing:
- probable root cause
- supporting evidence
- confidence
- recommended next investigation step

Do not claim certainty if the evidence is insufficient.
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