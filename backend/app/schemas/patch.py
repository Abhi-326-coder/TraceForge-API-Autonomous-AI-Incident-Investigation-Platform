
from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator

from app.guardrails.validators import validate_repository_path


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
    proposed_files: dict[str, str]

    tests_to_run: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)

    @field_validator("changed_files")
    @classmethod
    def validate_changed_files(cls, paths):
        normalized = [validate_repository_path(path) for path in paths]
        if len(normalized) != len(set(normalized)):
            raise ValueError("Changed file paths must be unique.")
        return normalized

    @field_validator("proposed_files")
    @classmethod
    def validate_proposed_files(cls, files):
        normalized = {}
        for path, content in files.items():
            safe_path = validate_repository_path(path)
            if safe_path in normalized:
                raise ValueError("Proposed file paths must be unique.")
            if not isinstance(content, str) or not content:
                raise ValueError("Proposed file contents must be non-empty strings.")
            normalized[safe_path] = content
        return normalized

    @model_validator(mode="after")
    def validate_path_mapping(self):
        if set(self.changed_files) != set(self.proposed_files):
            raise ValueError("Proposed file paths must exactly match changed_files.")
        return self
