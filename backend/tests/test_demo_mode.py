from app.agents import gemini_log_agent, root_cause_agent, supervisor_agent


def test_demo_agents_return_deterministic_results_without_gemini(monkeypatch):
    monkeypatch.setattr(gemini_log_agent.settings, "demo_mode", True)
    monkeypatch.setattr(root_cause_agent.settings, "demo_mode", True)
    monkeypatch.setattr(supervisor_agent.settings, "demo_mode", True)

    class ForbiddenGemini:
        def __init__(self, *args, **kwargs):
            raise AssertionError("Demo investigation must not initialize Gemini")

    monkeypatch.setattr(gemini_log_agent, "GeminiClient", ForbiddenGemini)
    monkeypatch.setattr(root_cause_agent, "ChatGoogleGenerativeAI", ForbiddenGemini)
    monkeypatch.setattr(supervisor_agent, "ChatGoogleGenerativeAI", ForbiddenGemini)

    incident = {"external_id": "DEMO-CHECKOUT-001", "title": "Checkout errors"}
    evidence = [{"id": 12}]
    assert "pool exhaustion" in gemini_log_agent.GeminiLogAgent().investigate(incident)
    assert supervisor_agent.SupervisorAgent().create_plan(incident) == ["logs", "metrics"]
    result = root_cause_agent.RootCauseAgent().analyze(evidence)
    assert result.root_cause == "Checkout database connection pool exhaustion"
    assert result.evidence_ids == [12]
