from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.agents.patch_agent import PatchAgent
from app.services.patch_context_service import PatchContextService


class PatchGenerationService:
    """Build authorized patch context and request a proposed patch."""

    def __init__(self, context_service=None, patch_agent=None):
        self.context_service = context_service or PatchContextService()
        self.patch_agent = patch_agent or PatchAgent()

    async def generate(self, db: Session, investigation_id: int, user):
        # Authorization and source retrieval remain centralized in the context builder.
        context = await self.context_service.build_context(db, investigation_id, user)
        source_files = context.source_files
        if not source_files:
            raise HTTPException(422, "Cannot generate a patch without source files.")

        incident = dict(context.incident)
        remediation = context.remediation
        if remediation is None:
            remediation = {
                "available": False,
                "status": "unavailable",
                "reason": "No persisted remediation proposal is available.",
            }
        else:
            remediation = dict(remediation)

        try:
            return self.patch_agent.generate(
                incident=incident,
                remediation=remediation,
                source_files=source_files,
            )
        except Exception as exc:
            # Avoid exposing prompts, source, credentials, or provider internals.
            raise HTTPException(502, "Patch generation failed.") from exc
