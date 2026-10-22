import base64
import httpx

from app.config import settings


class GitHubWriteProvider:
    BASE_URL = "https://api.github.com"

    def __init__(self):
        self.headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {settings.github_token}",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    async def create_commit_and_pr(
        self,
        owner: str,
        repo: str,
        base_branch: str,
        head_branch: str,
        files: dict[str, str],
        commit_message: str,
        pr_title: str,
        pr_body: str,
    ) -> dict:
        if not files:
            raise ValueError("No proposed file contents supplied")

        for path in files:
            parts = path.split("/")
            if (
                not path
                or path.startswith("/")
                or "\\" in path
                or any(part in {"", ".", ".."} for part in parts)
            ):
                raise ValueError(f"Unsafe repository path: {path}")

        async with httpx.AsyncClient(
            timeout=30.0,
            follow_redirects=False,
        ) as client:

            async def request(method: str, endpoint: str, **kwargs):
                response = await client.request(
                    method,
                    f"{self.BASE_URL}{endpoint}",
                    headers=self.headers,
                    **kwargs,
                )
                response.raise_for_status()
                return response.json() if response.content else {}

            prefix = f"/repos/{owner}/{repo}"

            # Confirm the feature branch and get its current commit.
            head_ref = await request(
                "GET",
                f"{prefix}/git/ref/heads/{head_branch}",
            )
            head_sha = head_ref["object"]["sha"]

            # Read the current branch commit/tree.
            head_commit = await request(
                "GET",
                f"{prefix}/git/commits/{head_sha}",
            )
            base_tree_sha = head_commit["tree"]["sha"]

            # Create blobs containing the approved complete file contents.
            tree_entries = []

            for path, content in files.items():
                blob = await request(
                    "POST",
                    f"{prefix}/git/blobs",
                    json={
                        "content": base64.b64encode(
                            content.encode("utf-8")
                        ).decode("ascii"),
                        "encoding": "base64",
                    },
                )

                tree_entries.append({
                    "path": path,
                    "mode": "100644",
                    "type": "blob",
                    "sha": blob["sha"],
                })

            # Build a new tree based on the feature branch's current tree.
            tree = await request(
                "POST",
                f"{prefix}/git/trees",
                json={
                    "base_tree": base_tree_sha,
                    "tree": tree_entries,
                },
            )

            commit = await request(
                "POST",
                f"{prefix}/git/commits",
                json={
                    "message": commit_message,
                    "tree": tree["sha"],
                    "parents": [head_sha],
                },
            )

            # Non-force update: fail rather than overwrite a moved ref.
            await request(
                "PATCH",
                f"{prefix}/git/refs/heads/{head_branch}",
                json={
                    "sha": commit["sha"],
                    "force": False,
                },
            )

            # Open a PR for review. Do not merge it.
            pr = await request(
                "POST",
                f"{prefix}/pulls",
                json={
                    "title": pr_title,
                    "body": pr_body,
                    "head": head_branch,
                    "base": base_branch,
                    "draft": True,
                },
            )

            return {
                "commit_sha": commit["sha"],
                "branch": head_branch,
                "pr_number": pr["number"],
                "pr_url": pr["html_url"],
                "pr_state": pr["state"],
                "draft": pr["draft"],
            }