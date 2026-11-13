from unittest.mock import MagicMock

import pytest
from langchain_core.messages import AIMessage

from app.agents import supervisor_agent
from app.agents.supervisor_agent import SupervisorAgent


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
