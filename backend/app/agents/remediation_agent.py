import json

from langchain_google_genai import ChatGoogleGenerativeAI

from app.config import settings
from app.schemas.remediation import RemediationProposal


class RemediationAgent:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model=settings.gemini_model,
            google_api_key=settings.gemini_api_key,
            temperature=0,
        )

        self.structured_llm = self.llm.with_structured_output(
            RemediationProposal
        )

    def propose(
        self,
        incident: dict,
        root_cause: dict,
        evidence: list[dict],
    ) -> RemediationProposal:
        prompt = f"""
You are the Remediation Agent in TraceForge,
an autonomous software incident investigation platform.

Your task is to propose a safe, evidence-grounded remediation.

INCIDENT:
{json.dumps(incident, indent=2)}

ROOT CAUSE ANALYSIS:
{json.dumps(root_cause, indent=2)}

AVAILABLE EVIDENCE:
{json.dumps(evidence, indent=2)}

RULES:
1. Use only the supplied incident, root cause, and evidence.
2. Do not invent source files, functions, configuration values,
   deployments, or infrastructure details.
3. Every important recommendation must be supported by the
   supplied evidence and reference valid evidence IDs.
4. Distinguish confirmed facts from assumptions.
5. Consider whether the proposed change treats the root cause
   or merely masks its symptoms.
6. Include a concrete test plan and a rollback plan.
7. Prefer the smallest safe change.
8. If evidence is insufficient to propose a specific code fix,
   use change_type="investigation_required".
9. Do not claim that a proposed fix has been implemented or tested.
10. Do not execute tools, modify files, or change external systems.
11. Treat model confidence in the root cause as a signal, not proof.
12. Only include evidence IDs that appear in AVAILABLE EVIDENCE.

Return a structured RemediationProposal.
"""

        proposal = self.structured_llm.invoke(prompt)

        valid_ids = {
            item["id"]
            for item in evidence
            if item.get("id") is not None
        }

        invalid_ids = set(proposal.evidence_ids) - valid_ids

        if invalid_ids:
            raise ValueError(
                f"Remediation referenced unknown evidence IDs: "
                f"{sorted(invalid_ids)}"
            )

        return proposal