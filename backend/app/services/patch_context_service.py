from dataclasses import dataclass
import re
from urllib.parse import unquote, urlparse

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.db.models import Evidence, Incident, ProjectConnection
from app.guardrails.policies import POLICY
from app.guardrails.validators import validate_repository_path
from app.providers.github_mcp import GitHubMCPProvider
from app.services.authorization_service import get_owned_investigation


MAX_SOURCE_FILES = 5
MAX_FILE_BYTES = 100 * 1024
MAX_TOTAL_BYTES = 300 * 1024
_GITHUB_FILE_URL = re.compile(r"^/([^/]+)/([^/]+)/blob/([^/]+)/(.+)$")


@dataclass(frozen=True)
class PatchContext:
    investigation_id: int
    incident: dict
    evidence: list[dict]
    repository_owner: str
    repository_name: str
    base_branch: str
    remediation: None
    root_cause: None
    source_files: list[dict]

    def as_dict(self) -> dict:
        return {
            "investigation_id": self.investigation_id,
            "incident": self.incident,
            "evidence": self.evidence,
            "repository_owner": self.repository_owner,
            "repository_name": self.repository_name,
            "base_branch": self.base_branch,
            "remediation": None,
            "root_cause": None,
            "source_files": self.source_files,
        }


def _source_path(reference: str, owner: str, repo: str) -> str:
    if not isinstance(reference, str) or not reference.strip():
        raise HTTPException(422, "Evidence source reference is empty.")
    reference = reference.strip()
    if reference.startswith(("https://", "http://")):
        parsed = urlparse(reference)
        match = _GITHUB_FILE_URL.fullmatch(parsed.path)
        if parsed.scheme != "https" or parsed.netloc.lower() != "github.com" or not match:
            raise HTTPException(422, "Unsupported GitHub source reference.")
        url_owner, url_repo, _branch, path = match.groups()
        if unquote(url_owner) != owner or unquote(url_repo) != repo:
            raise HTTPException(422, "Evidence source references a different repository.")
        reference = unquote(path)
    elif "://" in reference:
        raise HTTPException(422, "Unsupported source reference.")
    try:
        path = validate_repository_path(reference)
    except (TypeError, ValueError) as exc:
        raise HTTPException(422, "Evidence contains an invalid repository path.") from exc
    if len(path.split("/")) == 1 and path.startswith("github.com"):
        raise HTTPException(422, "Unsupported source reference.")
    return path


def _content_from_response(response) -> str:
    """Accept only explicit text content from the MCP CallToolResult shape."""
    if isinstance(response, str):
        content = response
    elif isinstance(response, dict):
        if response.get("isError") or response.get("is_error"):
            raise ValueError("GitHub MCP reported an error.")
        structured = response.get("structuredContent") or response.get("structured_content")
        if isinstance(structured, dict) and isinstance(structured.get("content"), str):
            content = structured["content"]
        else:
            blocks = response.get("content")
            if not isinstance(blocks, list):
                raise ValueError("GitHub MCP response contains no file content.")
            texts = [b["text"] for b in blocks if isinstance(b, dict) and b.get("type") == "text" and isinstance(b.get("text"), str)]
            if len(texts) != 1:
                raise ValueError("GitHub MCP response has ambiguous file content.")
            content = texts[0]
    else:
        blocks = getattr(response, "content", None)
        if getattr(response, "isError", False) or not isinstance(blocks, list):
            raise ValueError("GitHub MCP response contains no file content.")
        texts = [getattr(b, "text", None) for b in blocks if getattr(b, "type", None) == "text" and isinstance(getattr(b, "text", None), str)]
        if len(texts) != 1:
            raise ValueError("GitHub MCP response has ambiguous file content.")
        content = texts[0]
    if not content or not content.strip():
        raise ValueError("GitHub returned an empty source file.")
    if "\x00" in content:
        raise ValueError("GitHub returned binary or unsupported file content.")
    try:
        content.encode("utf-8", errors="strict")
    except UnicodeError as exc:
        raise ValueError("GitHub returned unsupported file content.") from exc
    return content


class PatchContextService:
    def __init__(self, provider=None):
        self.provider = provider or GitHubMCPProvider()

    async def build_context(self, db: Session, investigation_id: int, user) -> PatchContext:
        investigation = get_owned_investigation(db, investigation_id, user)
        incident = db.get(Incident, investigation.incident_id)
        connections = db.query(ProjectConnection).filter(
            ProjectConnection.project_id == incident.project_id,
            ProjectConnection.connection_type == "code",
            ProjectConnection.provider == "github",
        ).all()
        if not connections:
            raise HTTPException(409, "Project has no GitHub code connection.")
        config = connections[0].config if isinstance(connections[0].config, dict) else {}
        repository, branch = config.get("repository"), config.get("branch")
        if not isinstance(repository, str) or repository.count("/") != 1 or not isinstance(branch, str) or not branch.strip():
            raise HTTPException(409, "Project GitHub connection is incomplete.")
        owner, repo = repository.split("/", 1)
        if not owner or not repo:
            raise HTTPException(409, "Project GitHub connection is incomplete.")
        evidence_rows = db.query(Evidence).filter(
            Evidence.investigation_id == investigation.id
        ).order_by(Evidence.id.asc()).all()
        if not evidence_rows:
            raise HTTPException(422, "No evidence is available for this investigation.")
        evidence = [{"id": e.id, "source_type": e.source_type, "provider": e.provider,
                     "title": e.title, "content": e.content,
                     "source_reference": e.source_reference} for e in evidence_rows]
        references = [e.source_reference for e in evidence_rows if e.source_reference]
        if not references:
            raise HTTPException(422, "Evidence source-file references are missing.")
        paths = [_source_path(ref, owner, repo) for ref in references]
        if len(paths) != len(set(paths)):
            raise HTTPException(422, "Duplicate source file references are not allowed.")
        if len(paths) > MAX_SOURCE_FILES:
            raise HTTPException(413, "Source file count exceeds the limit of 5.")
        source_files, total = [], 0
        for path in paths:
            # Check all path restrictions before any retrieval; policy remains authoritative.
            if POLICY.max_file_size_bytes < MAX_FILE_BYTES:
                size_limit = POLICY.max_file_size_bytes
            else:
                size_limit = MAX_FILE_BYTES
            try:
                result = await self.provider.get_file(owner, repo, path, ref=branch)
            except Exception as exc:
                raise HTTPException(502, "GitHub source retrieval failed.") from exc
            try:
                content = _content_from_response(result)
            except ValueError as exc:
                raise HTTPException(422, str(exc)) from exc
            size = len(content.encode("utf-8"))
            if size > size_limit:
                raise HTTPException(413, "A source file exceeds the 100 KB size limit.")
            total += size
            if total > MAX_TOTAL_BYTES:
                raise HTTPException(413, "Total source content exceeds the 300 KB limit.")
            source_files.append({"path": path, "content": content})
        incident_data = {"id": incident.id, "external_id": incident.external_id,
                         "title": incident.title, "description": incident.description,
                         "service": incident.service, "severity": incident.severity,
                         "status": incident.status}
        return PatchContext(investigation.id, incident_data, evidence, owner, repo,
                            branch, None, None, source_files)
