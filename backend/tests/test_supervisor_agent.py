from unittest.mock import MagicMock

import pytest
from langchain_core.messages import AIMessage

from app.agents import supervisor_agent
from app.agents.supervisor_agent import SupervisorAgent


def test_supervisor_configures_bounded_gemini_requests(monkeypatch):
    llm_class = MagicMock()
    monkeypatch.setattr(
        supervisor_agent,
        "ChatGoogleGenerativeAI",
        llm_class,
    )

    SupervisorAgent()

    assert llm_class.call_args.kwargs["request_timeout"] == 30
    assert llm_class.call_args.kwargs["retries"] == 1


def test_supervisor_propagates_gemini_timeout(monkeypatch):
    llm = MagicMock()
    llm.invoke.side_effect = TimeoutError("Gemini request timed out")
    monkeypatch.setattr(
        supervisor_agent,
        "ChatGoogleGenerativeAI",
        MagicMock(return_value=llm),
    )
    agent = SupervisorAgent()

    with pytest.raises(TimeoutError, match="Gemini request timed out"):
        agent.create_plan(
            {
                "external_id": "test-1",
                "title": "Test incident",
                "description": "A test incident",
                "service": "test-service",
                "severity": "LOW",
            }
        )


@pytest.mark.parametrize(
    "content",
    [
        "logs, metrics",
        [{"type": "text", "text": "logs, metrics"}],
    ],
)
def test_supervisor_parses_text_and_text_block_responses(
    content,
    monkeypatch,
):
    llm = MagicMock()
    llm.invoke.return_value = AIMessage(content=content)
    monkeypatch.setattr(
        supervisor_agent,
        "ChatGoogleGenerativeAI",
        MagicMock(return_value=llm),
    )
    agent = SupervisorAgent()

    result = agent.create_plan(
        {
            "external_id": "test-1",
            "title": "Test incident",
            "description": "A test incident",
            "service": "test-service",
            "severity": "LOW",
        }
    )

    assert result == ["logs", "metrics"]
