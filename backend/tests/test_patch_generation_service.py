import asyncio

import pytest
from fastapi import HTTPException

from app.schemas.patch import GeneratedPatch
from app.services.patch_generation_service import PatchGenerationService


class ContextBuilder:
    def __init__(self, context=None, error=None):
        self.context, self.error, self.calls = context, error, []

    async def build_context(self, db, investigation_id, user):
        self.calls.append((db, investigation_id, user))
        if self.error:
            raise self.error
        return self.context


class Agent:
    def __init__(self, result=None, error=None):
        self.result, self.error, self.calls = result, error, []

    def generate(self, **kwargs):
        self.calls.append(kwargs)
        if self.error:
            raise self.error
        return self.result


class Context:
    investigation_id = 44
    incident = {"id": 8, "title": "API error", "description": "Failure"}
    remediation = None
    source_files = [{"path": "src/api.py", "content": "raise RuntimeError()\n"}]


def test_context_and_exact_agent_inputs_and_result_are_preserved():
    context_builder, patch = ContextBuilder(Context()), Agent(GeneratedPatch(
        summary="Fix API error", diff="diff", changed_files=["src/api.py"],
        proposed_files={"src/api.py": "updated content"}))
    service = PatchGenerationService(context_builder, patch)
    db, user = object(), object()
    result = asyncio.run(service.generate(db, 44, user))
    assert context_builder.calls == [(db, 44, user)]
    assert result is patch.result
    assert patch.calls == [{
        "incident": Context.incident,
        "remediation": {"available": False, "status": "unavailable",
                        "reason": "No persisted remediation proposal is available."},
        "source_files": Context.source_files,
    }]


def test_missing_source_files_rejected_without_agent_call():
    context = Context(); context.source_files = []
    agent = Agent()
    with pytest.raises(HTTPException) as exc:
        asyncio.run(PatchGenerationService(ContextBuilder(context), agent).generate(object(), 44, object()))
    assert exc.value.status_code == 422 and not agent.calls


def test_agent_failure_is_sanitized():
    context_builder = ContextBuilder(Context())
    agent = Agent(error=RuntimeError("prompt and secret content"))
    with pytest.raises(HTTPException) as exc:
        asyncio.run(PatchGenerationService(context_builder, agent).generate(object(), 44, object()))
    assert exc.value.status_code == 502
    assert "prompt and secret" not in str(exc.value.detail)


def test_unauthorized_context_error_propagates_unchanged():
    denied = HTTPException(404, "Investigation not found.")
    agent = Agent()
    with pytest.raises(HTTPException) as exc:
        asyncio.run(PatchGenerationService(ContextBuilder(error=denied), agent).generate(object(), 44, object()))
    assert exc.value is denied and not agent.calls


def test_no_live_providers_are_constructed_when_dependencies_are_mocked():
    context_builder, agent = ContextBuilder(Context()), Agent(GeneratedPatch(
        summary="Safe", diff="diff", changed_files=["src/api.py"],
        proposed_files={"src/api.py": "updated content"}))
    asyncio.run(PatchGenerationService(context_builder, agent).generate(object(), 44, object()))
    assert len(context_builder.calls) == 1 and len(agent.calls) == 1
