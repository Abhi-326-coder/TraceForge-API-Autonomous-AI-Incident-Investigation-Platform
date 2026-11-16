
import pytest
from pydantic import ValidationError

from app.schemas.patch import (
    ModifiedFile,
    PatchGenerationResult,
    GeneratedPatch,
)


def test_modified_file_requires_valid_fields():
    with pytest.raises(ValidationError):
        ModifiedFile(
            file_path="",
            proposed_content="",
            change_summary="",
        )


def test_patch_generation_requires_modified_files():
    with pytest.raises(ValidationError):
        PatchGenerationResult(
            summary="Fix checkout",
            modified_files=[],
        )


def test_generated_patch_requires_diff():
    with pytest.raises(ValidationError):
        GeneratedPatch(
            summary="Fix checkout",
            diff="",
            changed_files=["checkout.py"],
            proposed_files={"checkout.py": "fixed"},
        )


def test_patch_lists_default_to_empty():
    result = PatchGenerationResult(
        summary="Fix checkout",
        modified_files=[
            ModifiedFile(
                file_path="checkout.py",
                proposed_content="print('fixed')",
                change_summary="Fix checkout error",
            )
        ],
    )

    assert result.tests_to_run == []
    assert result.risks == []
    assert result.assumptions == []
