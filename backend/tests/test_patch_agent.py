from app.agents.patch_agent import PatchAgent
from app.schemas.patch import ModifiedFile, PatchGenerationResult


def test_rejects_path_traversal():
    try:
        PatchAgent._validate_path("../../.env")
    except ValueError:
        pass
    else:
        raise AssertionError("Unsafe path was accepted")


def test_accepts_relative_source_path():
    PatchAgent._validate_path("app/checkout.py")


def test_rejects_absolute_path():
    try:
        PatchAgent._validate_path("/etc/passwd")
    except ValueError:
        pass
    else:
        raise AssertionError("Absolute path was accepted")


def test_agent_preserves_complete_contents_for_multiple_modified_files(monkeypatch):
    agent = PatchAgent.__new__(PatchAgent)
    result = PatchGenerationResult(
        summary="Fix both files",
        modified_files=[
            ModifiedFile(file_path="src/a.py", proposed_content="complete a\n", change_summary="a"),
            ModifiedFile(file_path="src/b.py", proposed_content="complete b\n", change_summary="b"),
        ],
    )
    class Structured:
        def invoke(self, prompt):
            assert "complete a" not in prompt
            return result
    agent.structured_llm = Structured()
    generated = agent.generate({}, {}, [
        {"path": "src/a.py", "content": "old a\n"},
        {"path": "src/b.py", "content": "old b\n"},
    ])
    assert generated.changed_files == ["src/a.py", "src/b.py"]
    assert generated.proposed_files == {
        "src/a.py": "complete a\n", "src/b.py": "complete b\n"
    }


def test_agent_rejects_inconsistent_proposed_path_mapping(monkeypatch):
    from pydantic import ValidationError
    from app.schemas.patch import GeneratedPatch
    try:
        GeneratedPatch(summary="bad", diff="diff", changed_files=["src/a.py"],
                       proposed_files={"src/b.py": "contents"})
    except ValidationError:
        pass
    else:
        raise AssertionError("Inconsistent proposed file mapping was accepted")
