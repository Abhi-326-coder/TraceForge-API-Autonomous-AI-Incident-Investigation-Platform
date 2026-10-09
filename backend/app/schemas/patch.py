from pydantic import BaseModel, Field


class ModifiedFile(BaseModel):
    file_path: str
    proposed_content: str
    change_summary: str


class PatchGenerationResult(BaseModel):
    summary: str
    modified_files: list[ModifiedFile] = Field(
        min_length=1
    )
    tests_to_run: list[str]
    risks: list[str]
    assumptions: list[str] = Field(default_factory=list)


class GeneratedPatch(BaseModel):
    summary: str
    diff: str
    changed_files: list[str]
    tests_to_run: list[str]
    risks: list[str]
    assumptions: list[str]