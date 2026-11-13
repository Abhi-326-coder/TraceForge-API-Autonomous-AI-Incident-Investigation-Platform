from langchain_google_genai import ChatGoogleGenerativeAI

from app.config import settings


def _extract_text_content(content: object) -> str:
    if isinstance(content, str):
        return content

    if not isinstance(content, list):
        raise TypeError("Supervisor response content must be text.")

    text_parts = []
    for part in content:
        if isinstance(part, str):
            text_parts.append(part)
        elif isinstance(part, dict):
            text = part.get("text")
            if not isinstance(text, str):
                raise ValueError(
                    "Supervisor response contains a non-text content block."
                )
            text_parts.append(text)
        else:
            raise TypeError(
                "Supervisor response contains an unsupported content block."
            )

    response_text = "".join(text_parts)
    if not response_text.strip():
        raise ValueError("Supervisor response contains no text.")

    return response_text


class SupervisorAgent:

    def __init__(self):

        self.llm = ChatGoogleGenerativeAI(
            model=settings.gemini_model,
            google_api_key=settings.gemini_api_key,
            temperature=0,
        )

    def create_plan(
        self,
        incident: dict,
    ):

        prompt = f"""
You are the Supervisor Agent for TraceForge,
an autonomous software incident investigation platform.

Your responsibility is to decide which specialized
investigation capabilities are required.

Incident:

ID:
{incident["external_id"]}

Title:
{incident["title"]}

Description:
{incident["description"]}

Service:
{incident["service"]}

Severity:
{incident["severity"]}

Available investigation agents:

- logs
  Investigates application and runtime logs.

- metrics
  Investigates service metrics such as error rate,
  latency, request rate and resource utilization.

- code
  Investigates source code, recent commits and
  repository changes.

Return the investigation agents that should be used.

Rules:

1. Use logs when runtime failures need investigation.
2. Use metrics when system health or resource saturation
   may be relevant.
3. Use code when source changes or implementation details
   may explain the incident.
4. Prefer evidence collection before making conclusions.
5. Do not invent evidence.

Return only a comma-separated list containing:
logs
metrics
code
"""

        response = self.llm.invoke(prompt)

        agents = [
            item.strip().lower()
            for item in _extract_text_content(
                response.content
            ).split(",")
        ]

        allowed = {
            "logs",
            "metrics",
            "code",
        }

        return [
            agent
            for agent in agents
            if agent in allowed
        ]