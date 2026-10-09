import json
from pathlib import PurePosixPath

from langchain_google_genai import ChatGoogleGenerativeAI

from app.config import settings
from app.schemas.patch import (
    GeneratedPatch,
    PatchGenerationResult,
)


class PatchAgent:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model=settings.gemini_model,
            google_api_key=settings.gemini_api_key,
            temperature=0,
        )

        self.structured_llm = self.llm.with_structured_output(
            PatchGenerationResult
        )

    def generate(
        self,
        incident: dict,
        remediation: dict,
        source_files: list[dict],
    ) -> GeneratedPatch:
        if not source_files:
            raise ValueError(
                "Cannot generate a patch without source files."
            )

        original_files = {}

        for file in source_files:
            path = file["path"]
            content = file["content"]

            self._validate_path(path)

            if path in original_files:
                raise ValueError(f"Duplicate source path: {path}")

            original_files[path] = content

        prompt = f"""
You are TraceForge's Automated Patch Generation Agent.

Generate a minimal, reviewable code change based on the supplied
incident, remediation proposal, and actual source files.

INCIDENT:
{json.dumps(incident, indent=2)}

APPROVED REMEDIATION INPUT:
{json.dumps(remediation, indent=2)}

AVAILABLE SOURCE FILES:
{json.dumps(source_files, indent=2)}

STRICT RULES:
1. Modify only files included in AVAILABLE SOURCE FILES.
2. Return the complete proposed content of each modified file.
3. Do not invent existing code, APIs, environment variables,
   dependencies, or configuration.
4. Make the smallest reasonable change that addresses the proposal.
5. Preserve unrelated functionality and existing conventions.
6. Do not claim the patch has been tested.
7. Include tests that should be run and remaining risks.
8. If the supplied evidence is insufficient for a safe change,
   state that limitation in assumptions and risks.
9. Do not add secrets, credentials, or hardcoded API keys.
10. Do not execute code, edit the repository, or call external tools.
11. Do not modify unrelated files.
12. Use exact relative file paths from the supplied source files.

Return a structured PatchGenerationResult.
"""

        result = self.structured_llm.invoke(prompt)

        proposed_by_path = {}

        for modified_file in result.modified_files:
            path = modified_file.file_path

            self._validate_path(path)

            if path not in original_files:
                raise ValueError(
                    f"Model proposed a file that was not supplied: {path}"
                )

            if path in proposed_by_path:
                raise ValueError(
                    f"Model returned a duplicate file: {path}"
                )

            proposed_by_path[path] = modified_file

        if not proposed_by_path:
            raise ValueError("The model returned no modified files.")

        # Generate diffs deterministically from original and proposed
        # contents. The model never gets to invent diff coordinates.
        import difflib

        diff_lines = []

        for path, modified_file in proposed_by_path.items():
            original = original_files[path]
            proposed = modified_file.proposed_content

            diff = difflib.unified_diff(
                original.splitlines(keepends=True),
                proposed.splitlines(keepends=True),
                fromfile=f"a/{path}",
                tofile=f"b/{path}",
            )

            diff_lines.extend(diff)

        return GeneratedPatch(
            summary=result.summary,
            diff="".join(diff_lines),
            changed_files=list(proposed_by_path.keys()),
            tests_to_run=result.tests_to_run,
            risks=result.risks,
            assumptions=result.assumptions,
        )

    @staticmethod
    def _validate_path(path: str) -> None:
        candidate = PurePosixPath(path)

        if (
            not path
            or candidate.is_absolute()
            or ".." in candidate.parts
            or "\\" in path
            or path.startswith("/")
        ):
            raise ValueError(f"Unsafe file path: {path}")