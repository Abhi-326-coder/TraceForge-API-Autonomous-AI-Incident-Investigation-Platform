from langchain_google_genai import ChatGoogleGenerativeAI

from app.config import settings


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
            for item in response.content.split(",")
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