from langchain_google_genai import ChatGoogleGenerativeAI

from app.config import settings
from app.schemas.root_cause import RootCauseResult


class RootCauseAgent:

    def __init__(self):
        if settings.demo_mode:
            self.llm = None
            self.structured_llm = None
            return

        self.llm = ChatGoogleGenerativeAI(
            model=settings.gemini_model,
            google_api_key=settings.gemini_api_key,
            temperature=0,
            max_retries=0,
        )

        self.structured_llm = (
            self.llm.with_structured_output(
                RootCauseResult
            )
        )

    def analyze(
        self,
        evidence: list[dict],
    ) -> RootCauseResult:

        if settings.demo_mode:
            ids = [item["id"] for item in evidence]
            return RootCauseResult(
                root_cause="Checkout database connection pool exhaustion",
                explanation=("The seeded checkout logs show the connection pool was exhausted immediately "
                             "before transaction failures and HTTP 500 responses. This is the strongest "
                             "direct explanation available in the demo evidence."),
                confidence=0.86 if ids else 0.35,
                evidence_ids=ids,
                alternative_causes=[{"cause": "Database outage", "reason_not_primary": "The sample contains pool exhaustion but no direct evidence of database unavailability."}],
                uncertainty="The demo includes runtime logs only; database health and pool configuration were not independently inspected.",
            )

        evidence_text = "\n\n".join(
            [
                (
                    f"Evidence ID: {item['id']}\n"
                    f"Source: {item['source_type']}\n"
                    f"Provider: {item['provider']}\n"
                    f"Title: {item['title']}\n"
                    f"Content: {item['content']}\n"
                    f"Reference: {item.get('source_reference')}"
                )
                for item in evidence
            ]
        )

        prompt = f"""
You are the Root Cause Agent for TraceForge.

Your responsibility is to determine the most likely
root cause of a software incident using ONLY the
provided evidence.

Evidence:

{evidence_text}

Rules:

1. Do not invent evidence.
2. Every important conclusion must be supported by
   one or more provided evidence IDs.
3. Only use evidence IDs that actually exist above.
4. Distinguish direct evidence from inference.
5. Consider alternative explanations.
6. If evidence is insufficient, say so.
7. Do not claim certainty when the evidence is weak.
8. Return a confidence score between 0 and 1.
9. The confidence score represents model confidence,
   not statistical probability.

Determine:

- the most likely root cause
- why the evidence supports it
- which evidence IDs support the conclusion
- plausible alternative causes
- remaining uncertainty
"""

        return self.structured_llm.invoke(
            prompt
        )
