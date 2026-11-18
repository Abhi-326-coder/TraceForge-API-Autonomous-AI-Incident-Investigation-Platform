from fastapi import HTTPException
from sqlalchemy.orm import Session
import difflib

from app.agents.patch_agent import PatchAgent
from app.services.patch_context_service import PatchContextService
from app.config import settings
from app.schemas.patch import GeneratedPatch, ModifiedFile, PatchGenerationResult


def _generated_from_demo(result: PatchGenerationResult, original: str) -> GeneratedPatch:
    modified = result.modified_files[0]
    diff = "".join(difflib.unified_diff(
        original.splitlines(keepends=True),
        modified.proposed_content.splitlines(keepends=True),
        fromfile=f"a/{modified.file_path}", tofile=f"b/{modified.file_path}",
    ))
    return GeneratedPatch(
        summary=result.summary, diff=diff,
        changed_files=[modified.file_path],
        proposed_files={modified.file_path: modified.proposed_content},
        tests_to_run=result.tests_to_run, risks=result.risks,
        assumptions=result.assumptions,
    )


class PatchGenerationService:
    """Build authorized patch context and request a proposed patch."""

    def __init__(self, context_service=None, patch_agent=None):
        self.context_service = context_service
        self.patch_agent = patch_agent

    async def generate(self, db: Session, investigation_id: int, user):
        if settings.demo_mode and self.patch_agent is None:
            from app.services.authorization_service import get_owned_investigation
            from app.db.models import Incident, Evidence
            investigation = get_owned_investigation(db, investigation_id, user)
            db.get(Incident, investigation.incident_id)
            evidence = db.query(Evidence).filter(Evidence.investigation_id == investigation_id).all()
            if not evidence:
                raise HTTPException(422, "No evidence is available for this investigation.")
            path = "src/checkout/connection_pool.py"
            original = "MAX_CONNECTIONS = 10\nACQUIRE_TIMEOUT_SECONDS = 1\n"
            proposed = "MAX_CONNECTIONS = 30\nACQUIRE_TIMEOUT_SECONDS = 5\n"
            demo_result = PatchGenerationResult(
                summary="Increase checkout database pool capacity and acquisition timeout",
                modified_files=[ModifiedFile(file_path=path, proposed_content=proposed, change_summary="Increase pool capacity and wait longer for a connection.")],
                tests_to_run=["Run checkout API integration tests", "Load test concurrent checkout requests"],
                risks=["Higher pool limits can increase database connection usage."],
                assumptions=["Demo source file is illustrative seeded content, not fetched from a repository."],
            )
            return _generated_from_demo(demo_result, original)
        patch_agent = self.patch_agent or PatchAgent()
        # Authorization and source retrieval remain centralized in the context builder.
        context = await (self.context_service or PatchContextService()).build_context(db, investigation_id, user)
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
            return patch_agent.generate(
                incident=incident,
                remediation=remediation,
                source_files=source_files,
            )
        except Exception as exc:
            # Avoid exposing prompts, source, credentials, or provider internals.
            raise HTTPException(502, "Patch generation failed.") from exc
