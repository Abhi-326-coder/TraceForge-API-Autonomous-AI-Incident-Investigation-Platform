from app.agents.patch_agent import PatchAgent


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