import re

import httpx

from app.config import settings


class GitHubRESTProvider:
    BASE_URL = "https://api.github.com"

    def __init__(self):
        self.headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {settings.github_token}",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    @staticmethod
    def _validate_repo_name(value: str, field: str) -> None:
        if not re.fullmatch(r"[A-Za-z0-9_.-]+", value):
            raise ValueError(f"Invalid GitHub {field}")

        if value in {".", ".."}:
            raise ValueError(f"Invalid GitHub {field}")

    async def create_branch(
        self,
        owner: str,
        repo: str,
        base_branch: str,
        new_branch: str,
    ) -> dict:
        self._validate_repo_name(owner, "owner")
        self._validate_repo_name(repo, "repository")

        if not base_branch or base_branch.startswith("-"):
            raise ValueError("Invalid base branch")

        if (
            not new_branch
            or new_branch.startswith("-")
            or new_branch.startswith("/")
            or new_branch.endswith("/")
            or ".." in new_branch
            or " " in new_branch
            or any(char in new_branch for char in ["~", "^", ":", "?", "*", "[", "\\"])
            or new_branch.endswith(".lock")
            or "//" in new_branch
        ):
            raise ValueError("Invalid Git branch name")

        if any(part.startswith(".") for part in new_branch.split("/")):
            raise ValueError("Invalid Git branch name")

        async with httpx.AsyncClient(
            timeout=20.0,
            follow_redirects=False,
        ) as client:
            # Resolve the source branch to a specific commit SHA.
            base_response = await client.get(
                f"{self.BASE_URL}/repos/{owner}/{repo}/branches/"
                f"{base_branch}",
                headers=self.headers,
            )
            base_response.raise_for_status()

            base_data = base_response.json()
            sha = base_data["commit"]["sha"]

            # Create the new Git reference.
            create_response = await client.post(
                f"{self.BASE_URL}/repos/{owner}/{repo}/git/refs",
                headers=self.headers,
                json={
                    "ref": f"refs/heads/{new_branch}",
                    "sha": sha,
                },
            )
            create_response.raise_for_status()

            created = create_response.json()

            return {
                "branch_name": created["ref"].removeprefix(
                    "refs/heads/"
                ),
                "sha": created["object"]["sha"],
                "url": created["url"],
            }