
from pydantic import BaseModel, Field, ConfigDict


class ModifiedFile(BaseModel):
    model_config = ConfigDict(extra="forbid")

    file_path: str = Field(min_length=1)
    proposed_content: str = Field(min_length=1)
    change_summary: str = Field(min_length=1)


class PatchGenerationResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    summary: str = Field(min_length=1)

    modified_files: list[ModifiedFile] = Field(
        min_length=1
    )

    tests_to_run: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)


class GeneratedPatch(BaseModel):
    model_config = ConfigDict(extra="forbid")

    summary: str = Field(min_length=1)
    diff: str = Field(min_length=1)

    changed_files: list[str] = Field(min_length=1)

    tests_to_run: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
