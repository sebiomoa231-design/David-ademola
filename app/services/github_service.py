"""GitHub integration service for David AI (GitHub App architecture).

Provides server-side authentication, repository creation, content push,
branch management, and repository inspection using a GitHub App.

Secrets (private key, client secret, tokens) live ONLY in backend
environment variables and are never returned by any endpoint, stored in
the database, or placed in frontend code.

Two authentication paths are supported and both stay server-side:
1. Installation access tokens  (GITHUB_APP_ID + GITHUB_APP_PRIVATE_KEY +
   GITHUB_INSTALLATION_ID) - the recommended path. The owner installs the
   GitHub App on their own account and David AI mints short-lived tokens.
2. OAuth user tokens via the GitHub App's OAuth client
   (GITHUB_CLIENT_ID + GITHUB_CLIENT_SECRET) - used by the "Connect GitHub"
   flow in the dashboard. The resulting tokens are encrypted-agnostic memory
   tokens that the frontend never sees directly.
"""

from __future__ import annotations

import base64
import json
import logging
import re
import time
from datetime import datetime, timezone
from typing import Any

import httpx

logger = logging.getLogger(__name__)

API_BASE = "https://api.github.com"
_OAUTH_AUTHORIZE_URL = "https://github.com/login/oauth/authorize"
_OAUTH_TOKEN_URL = "https://github.com/login/oauth/access_token"

_SAFE_NAME_RE = re.compile(r"^[a-z0-9][a-z0-9._-]{0,98}[a-z0-9]$|^[a-z0-9]$")

# Events audited through the GitHub service (never include secrets).
AUDIT_GITHUB_CONNECTED = "github.connected"
AUDIT_GITHUB_DISCONNECTED = "github.disconnected"
AUDIT_REPO_CREATED = "github.repository.created"
AUDIT_REPO_NAME_COLLISION = "github.repository.name_collision"
AUDIT_REPO_INITIALIZED = "github.repository.initialized"
AUDIT_REPO_FILES_PUSHED = "github.repository.files_pushed"
AUDIT_REPO_COMMIT_CREATED = "github.repository.commit_created"
AUDIT_REPO_UPDATED = "github.repository.updated"
AUDIT_DEPLOYMENT_REQUESTED = "github.deployment.requested"
AUDIT_DEPLOYMENT_COMPLETED = "github.deployment.completed"
AUDIT_DEPLOYMENT_FAILED = "github.deployment.failed"


class GitHubError(RuntimeError):
    """Safe, non-secret error raised for GitHub API failures."""

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        error_code: str = "github_error",
        retry_after: int | None = None,
    ) -> None:
        self.status_code = status_code
        self.error_code = error_code
        self.retry_after = retry_after
        super().__init__(message)


class GitHubNotConfigured(GitHubError):
    def __init__(self) -> None:
        super().__init__(
            "GitHub is not connected yet. Install the David AI GitHub App on your "
            "account and connect it in the dashboard.",
            error_code="github_not_configured",
        )


class GitHubRateLimited(GitHubError):
    def __init__(self, retry_after: int | None, message: str = "GitHub rate limit exceeded. Please try again later.") -> None:
        super().__init__(message, status_code=429, error_code="github_rate_limited", retry_after=retry_after)


class GitHubUnauthorized(GitHubError):
    def __init__(self, message: str = "GitHub authorization failed. Reconnect the GitHub App.") -> None:
        super().__init__(message, status_code=401, error_code="github_unauthorized")


def _safe_slug(text: str) -> str:
    """Turn free text into a GitHub-safe lowercase slug segment."""
    slug = text.lower().strip()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    slug = slug.strip("-")
    return slug[:60] or "site"


def _is_safe_repo_name(name: str) -> bool:
    return bool(_SAFE_NAME_RE.match(name))


def generate_repository_name(topic: str, owner_login: str, existing_names: set[str] | None = None) -> str:
    """Build a unique, GitHub-safe repository name.

    Pattern: david-<topic-slug>-site, with a deterministic numeric suffix
    when a collision exists (never overwrites an existing repository).
    """
    slug = _safe_slug(topic)
    base = f"david-{slug}-site"
    base = base[:95]
    if not _is_safe_repo_name(base):
        base = "david-generated-site"
    if existing_names is None:
        return base
    if base not in existing_names:
        return base
    for index in range(2, 100):
        candidate = f"{base}-{index}"
        if candidate not in existing_names:
            return candidate
    return f"{base}-x{int(time.time())}"


def _encode_jwt(app_id: str | int, private_key_pem: str) -> str:
    """Create a short-lived JSON Web Token for GitHub App authentication
    (RS256) using only the stdlib + PyJWT-free approach. PyJWT is a David
    dependency already (used for owner JWTs), so we delegate to it."""
    import jwt  # David AI already depends on PyJWT

    now = int(time.time())
    payload = {"iat": now - 60, "exp": now + (10 * 60), "iss": str(app_id)}
    return jwt.encode(payload, private_key_pem, algorithm="RS256")


def _user_agent() -> dict[str, str]:
    return {"Accept": "application/vnd.github+json", "User-Agent": "David-AI-Backend"}


class GitHubService:
    """Server-side GitHub operations for David AI."""

    def __init__(
        self,
        app_id: str | int | None = None,
        private_key: str | None = None,
        client_id: str | None = None,
        client_secret: str | None = None,
        installation_id: str | int | None = None,
        installation_access_token: str | None = None,
        public_base_url: str | None = None,
    ) -> None:
        self.app_id = app_id
        self.private_key = private_key
        self.client_id = client_id
        self.client_secret = client_secret
        self.installation_id = installation_id
        self._cached_token = installation_access_token
        self._token_expires_at = 0.0
        self.public_base_url = public_base_url

    @classmethod
    def from_settings(cls, settings: Any) -> "GitHubService":
        return cls(
            app_id=getattr(settings, "github_app_id", None) or None,
            private_key=getattr(settings, "github_app_private_key", None) or None,
            client_id=getattr(settings, "github_client_id", None) or None,
            client_secret=getattr(settings, "github_client_secret", None) or None,
            installation_id=getattr(settings, "github_installation_id", None) or None,
            installation_access_token=getattr(settings, "github_installation_access_token", None) or None,
            public_base_url=getattr(settings, "public_base_url", None) or None,
        )

    @property
    def is_configured(self) -> bool:
        has_installation_flow = bool(
            self.app_id and self.private_key and self.installation_id
        )
        has_oauth_flow = bool(self.client_id and self.client_secret)
        return bool(has_installation_flow or has_oauth_flow or self._cached_token)

    # ------------------------------------------------------------------
    # HTTP helpers
    # ------------------------------------------------------------------

    def _headers(self, token: str) -> dict[str, str]:
        headers = _user_agent()
        headers["Authorization"] = f"Bearer {token}"
        return headers

    def _request(
        self,
        method: str,
        path: str,
        *,
        token: str,
        params: dict[str, Any] | None = None,
        json_body: Any | None = None,
        expect: tuple[int, ...] = (200, 201, 202, 204),
    ) -> Any:
        url = f"{API_BASE}{path}"
        headers = self._headers(token)
        timeout = 60.0 if method in ("POST", "PUT") else 30.0
        try:
            with httpx.Client(timeout=timeout, follow_redirects=True) as client:
                response = client.request(
                    method,
                    url,
                    params=params,
                    json=json_body,
                    headers=headers,
                )
        except httpx.HTTPError as exc:
            raise GitHubError(f"GitHub request failed: {method} {path}", error_code="github_network_error") from exc

        if response.status_code == 401:
            raise GitHubUnauthorized()
        if response.status_code == 403:
            retry_after = None
            try:
                retry_header = response.headers.get("retry-after")
                if retry_header:
                    retry_after = max(1, int(retry_header))
            except ValueError:
                retry_after = None
            rate_remaining = response.headers.get("x-ratelimit-remaining")
            if rate_remaining is not None and rate_remaining == "0":
                raise GitHubRateLimited(retry_after)
            raise GitHubError(
                f"GitHub rejected the request: {method} {path} (status {response.status_code})",
                status_code=403,
                error_code="github_forbidden",
            )
        if response.status_code == 422:
            detail = path
            try:
                payload = response.json()
                errors = payload.get("errors", [])
                if errors:
                    detail = "; ".join(str(err.get("message", err)) for err in errors[:3])
                elif payload.get("message"):
                    detail = str(payload["message"])
            except ValueError:
                pass
            raise GitHubError(detail[:300], status_code=422, error_code="github_validation_error")
        if response.status_code not in expect:
            message = f"GitHub request failed: {method} {path} (status {response.status_code})"
            try:
                payload = response.json()
                message = str(payload.get("message", message))
            except ValueError:
                pass
            raise GitHubError(message[:300], status_code=response.status_code, error_code="github_api_error")
        if response.status_code == 204 or not response.content:
            return {}
        content_type = response.headers.get("content-type", "")
        if "json" in content_type:
            try:
                return response.json()
            except ValueError:
                return {}
        return {"raw": response.text}

    # ------------------------------------------------------------------
    # Token management (installation access token flow)
    # ------------------------------------------------------------------

    def _installation_token(self) -> str:
        if self._cached_token and time.time() < self._token_expires_at:
            return self._cached_token
        if not (self.app_id and self.private_key and self.installation_id):
            raise GitHubNotConfigured()
        app_jwt = _encode_jwt(self.app_id, self.private_key)
        payload = self._request(
            "POST",
            f"/app/installations/{self.installation_id}/access_tokens",
            token=app_jwt,
            json_body={},
        )
        token = payload.get("token")
        if not isinstance(token, str) or not token:
            raise GitHubError("GitHub did not return an installation access token", error_code="github_token_error")
        expires_at = payload.get("expires_at")
        self._cached_token = token
        self._token_expires_at = 0
        if isinstance(expires_at, str):
            try:
                dt = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
                self._token_expires_at = dt.timestamp() - 60
            except ValueError:
                self._token_expires_at = time.time() + (60 * 60)
        else:
            self._token_expires_at = time.time() + (60 * 60)
        return token

    def authenticate_github(self) -> dict[str, Any]:
        """Verify the GitHub connection works and return minimal identity."""
        user = self.get_authenticated_user()
        return {
            "connected": True,
            "github_login": user["login"],
            "github_id": user["id"],
            "github_url": user["html_url"],
            "authenticated_at": datetime.now(timezone.utc).isoformat(),
        }

    def get_authenticated_user(self) -> dict[str, Any]:
        token = self._installation_token()
        user = self._request("GET", "/user", token=token)
        if not isinstance(user, dict) or "login" not in user:
            raise GitHubError("GitHub did not return a user identity", error_code="github_identity_error")
        return {
            "login": user["login"],
            "id": user["id"],
            "html_url": user.get("html_url", f"https://github.com/{user['login']}"),
            "name": user.get("name"),
            "avatar_url": user.get("avatar_url"),
        }

    # ------------------------------------------------------------------
    # OAuth connect flow (Connect GitHub button)
    # ------------------------------------------------------------------

    def oauth_authorize_url(self, state: str) -> str:
        """URL the dashboard sends the owner to in order to authorize the app."""
        if not (self.client_id and self.client_secret):
            raise GitHubNotConfigured()
        params = {
            "client_id": self.client_id,
            "scope": "repo",
            "state": state,
        }
        query = "&".join(f"{k}={v}" for k, v in params.items())
        return f"{_OAUTH_AUTHORIZE_URL}?{query}"

    def oauth_exchange_code(self, code: str) -> dict[str, Any]:
        """Exchange an OAuth authorization code for a user access token.

        The returned token is stored server-side only. Only a status flag
        and the GitHub identity are returned to callers.
        """
        if not (self.client_id and self.client_secret):
            raise GitHubNotConfigured()
        payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
        }
        headers = _user_agent()
        headers["Accept"] = "application/json"
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.post(_OAUTH_TOKEN_URL, json=payload, headers=headers)
        except httpx.HTTPError as exc:
            raise GitHubError("GitHub OAuth token exchange failed", error_code="github_network_error") from exc
        try:
            data = response.json()
        except ValueError:
            raise GitHubError("GitHub OAuth token exchange returned an invalid response", error_code="github_oauth_error")
        if not isinstance(data, dict) or "access_token" not in data:
            error_desc = data.get("error_description", data.get("error", "unknown")) if isinstance(data, dict) else "unknown"
            raise GitHubError(f"GitHub OAuth error: {error_desc}", error_code="github_oauth_error")
        return {
            "oauth_access_token": data["access_token"],
            "token_type": data.get("token_type", "bearer"),
            "scope": data.get("scope", ""),
        }

    # ------------------------------------------------------------------
    # Repositories
    # ------------------------------------------------------------------

    def _list_existing_names(self, token: str, per_page: int = 100) -> set[str]:
        names: set[str] = set()
        page = 1
        while True:
            page_payload = self._request(
                "GET",
                "/user/repos",
                token=token,
                params={"type": "owner", "per_page": str(min(per_page, 100)), "page": str(page)},
            )
            repos = page_payload if isinstance(page_payload, list) else []
            for repo in repos:
                if isinstance(repo, dict) and repo.get("name"):
                    names.add(str(repo["name"]))
            if len(repos) < per_page or page >= 10:
                break
            page += 1
        return names

    def create_repository(
        self,
        topic: str,
        *,
        description: str = "Generated by David AI",
        private: bool = True,
    ) -> dict[str, Any]:
        """Create a new repository with a unique, GitHub-safe name.

        Never overwrites an existing repository; generates a deterministic
        unique suffix when the preferred name is taken.
        """
        token = self._installation_token()
        owner = self.get_authenticated_user()["login"]
        existing = self._list_existing_names(token)
        name = generate_repository_name(topic, owner, existing)
        collision = name != generate_repository_name(topic, owner)
        if collision:
            logger.info(f"github repository name collision, using '{name}'")

        payload = {
            "name": name,
            "description": description,
            "private": private,
            "auto_init": False,
        }
        created = self._request("POST", "/user/repos", token=token, json_body=payload)
        if not isinstance(created, dict) or "full_name" not in created:
            raise GitHubError("GitHub did not return the created repository", error_code="github_repo_create_error")

        return {
            "repository_id": created.get("id"),
            "repository_name": created["name"],
            "repository_full_name": created["full_name"],
            "repository_owner": owner,
            "repository_url": f"https://github.com/{created['full_name']}",
            "clone_url": created.get("clone_url", ""),
            "default_branch": created.get("default_branch", "main"),
            "visibility": "private" if created.get("private") else "public",
            "created_at": created.get("created_at", ""),
            "is_empty": True,
        }

    def get_repository(self, full_name: str) -> dict[str, Any]:
        token = self._installation_token()
        repo = self._request("GET", f"/repos/{full_name}", token=token)
        if not isinstance(repo, dict) or "full_name" not in repo:
            raise GitHubError(f"Repository not found: {full_name}", status_code=404, error_code="github_repo_not_found")
        return {
            "repository_id": repo.get("id"),
            "repository_name": repo["name"],
            "repository_full_name": repo["full_name"],
            "repository_owner": repo["owner"]["login"],
            "repository_url": repo.get("html_url", f"https://github.com/{repo['full_name']}"),
            "default_branch": repo.get("default_branch", "main"),
            "visibility": "private" if repo.get("private") else "public",
            "created_at": repo.get("created_at", ""),
            "updated_at": repo.get("updated_at", ""),
            "is_empty": repo.get("size", 0) == 0,
        }

    def list_repositories(self, limit: int = 50) -> list[dict[str, Any]]:
        token = self._installation_token()
        repos = self._request(
            "GET",
            "/user/repos",
            token=token,
            params={"type": "owner", "per_page": str(min(limit, 100)), "page": "1"},
        )
        repos = repos if isinstance(repos, list) else []
        out: list[dict[str, Any]] = []
        for repo in repos[:limit]:
            if not isinstance(repo, dict) or "full_name" not in repo:
                continue
            out.append(
                {
                    "repository_id": repo.get("id"),
                    "repository_name": repo["name"],
                    "repository_full_name": repo["full_name"],
                    "repository_owner": repo["owner"]["login"],
                    "repository_url": repo.get("html_url", f"https://github.com/{repo['full_name']}"),
                    "default_branch": repo.get("default_branch", "main"),
                    "visibility": "private" if repo.get("private") else "public",
                    "created_at": repo.get("created_at", ""),
                    "updated_at": repo.get("updated_at", ""),
                    "is_empty": repo.get("size", 0) == 0,
                }
            )
        return out

    # ------------------------------------------------------------------
    # Initialization, commits, branches, file updates
    # ------------------------------------------------------------------

    def initialize_repository(self, full_name: str, default_branch: str = "main") -> dict[str, Any]:
        """Initialize an empty repository with a root commit.

        Uses the Git blobs/trees/commits/refs APIs rather than the Contents
        API so the entire bootstrap happens in a single clean commit.
        """
        token = self._installation_token()
        root_tree = self._request(
            "POST",
            f"/repos/{full_name}/git/trees",
            token=token,
            json_body={"tree": []},
        )
        commit = self._request(
            "POST",
            f"/repos/{full_name}/git/commits",
            token=token,
            json_body={
                "message": "Initialize repository (David AI)",
                "tree": root_tree["sha"],
            },
        )
        self._request(
            "POST",
            f"/repos/{full_name}/git/refs",
            token=token,
            json_body={"ref": f"refs/heads/{default_branch}", "sha": commit["sha"]},
        )
        return {
            "initialized": True,
            "default_branch": default_branch,
            "initial_commit_sha": commit["sha"],
        }

    def push_files(
        self,
        full_name: str,
        files: dict[str, str],
        *,
        branch: str = "main",
        message: str = "Add generated website files (David AI)",
    ) -> dict[str, Any]:
        """Push many files to a branch, creating the branch from the base
        branch if it does not exist. Each file becomes one commit on the
        branch, chained to the previous one, with a final status commit."""
        token = self._installation_token()
        base_sha = self._get_branch_sha(full_name, branch)
        parent_sha = base_sha
        commit_shas: list[str] = []
        for path, content in files.items():
            blob = self._request(
                "POST",
                f"/repos/{full_name}/git/blobs",
                token=token,
                json_body={"content": content, "encoding": "utf-8"},
            )
            tree = self._request(
                "POST",
                f"/repos/{full_name}/git/trees",
                token=token,
                json_body={
                    "base_tree": base_sha,
                    "tree": [{"path": path, "mode": "100644", "type": "blob", "sha": blob["sha"]}],
                },
            )
            commit_payload: dict[str, Any] = {
                "message": f"Add {path} (David AI)",
                "tree": tree["sha"],
                "parents": [parent_sha] if parent_sha else [],
            }
            commit = self._request(
                "POST",
                f"/repos/{full_name}/git/commits",
                token=token,
                json_body=commit_payload,
            )
            parent_sha = commit["sha"]
            commit_shas.append(commit["sha"])

        self._request(
            "POST" if base_sha is None else "PATCH",
            f"/repos/{full_name}/git/refs/heads/{branch}" if base_sha is not None else f"/repos/{full_name}/git/refs",
            token=token,
            json_body={"sha": parent_sha} if base_sha is not None else {"ref": f"refs/heads/{branch}", "sha": parent_sha},
        )
        return {
            "branch": branch,
            "last_commit_sha": commit_shas[-1] if commit_shas else None,
            "commits_created": len(commit_shas),
            "files_pushed": list(files.keys()),
        }

    def create_commit(
        self,
        full_name: str,
        files: dict[str, str],
        *,
        branch: str = "main",
        message: str,
    ) -> dict[str, Any]:
        """Update files on an existing branch with one new commit."""
        token = self._installation_token()
        base_sha = self._get_branch_sha(full_name, branch)
        if base_sha is None:
            raise GitHubError(f"Branch '{branch}' does not exist in {full_name}", error_code="github_branch_missing")
        parent_sha = base_sha
        last_sha: str | None = None
        for path, content in files.items():
            blob = self._request(
                "POST",
                f"/repos/{full_name}/git/blobs",
                token=token,
                json_body={"content": content, "encoding": "utf-8"},
            )
            tree = self._request(
                "POST",
                f"/repos/{full_name}/git/trees",
                token=token,
                json_body={
                    "base_tree": base_sha,
                    "tree": [{"path": path, "mode": "100644", "type": "blob", "sha": blob["sha"]}],
                },
            )
            commit = self._request(
                "POST",
                f"/repos/{full_name}/git/commits",
                token=token,
                json_body={"message": message, "tree": tree["sha"], "parents": [parent_sha]},
            )
            parent_sha = commit["sha"]
            last_sha = commit["sha"]
        self._request(
            "PATCH",
            f"/repos/{full_name}/git/refs/heads/{branch}",
            token=token,
            json_body={"sha": last_sha},
        )
        return {"branch": branch, "commit_sha": last_sha}

    def create_branch(self, full_name: str, branch: str, base_branch: str = "main") -> dict[str, Any]:
        token = self._installation_token()
        base_sha = self._get_branch_sha(full_name, base_branch)
        if base_sha is None:
            raise GitHubError(f"Base branch '{base_branch}' does not exist in {full_name}", error_code="github_branch_missing")
        self._request(
            "POST",
            f"/repos/{full_name}/git/refs",
            token=token,
            json_body={"ref": f"refs/heads/{branch}", "sha": base_sha},
        )
        return {"branch": branch, "base_branch": base_branch, "base_sha": base_sha}

    def get_repository_url(self, full_name: str) -> str:
        return f"https://github.com/{full_name}"

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _get_branch_sha(self, full_name: str, branch: str) -> str | None:
        token = self._installation_token()
        try:
            ref = self._request(
                "GET",
                f"/repos/{full_name}/git/ref/heads/{branch}",
                token=token,
                expect=(200,),
            )
            obj = ref.get("object", {}) if isinstance(ref, dict) else {}
            return obj.get("sha")
        except GitHubError:
            return None

    def repository_exists(self, owner: str, name: str) -> bool:
        token = self._installation_token()
        try:
            repo = self._request("GET", f"/repos/{owner}/{name}", token=token, expect=(200,))
            return isinstance(repo, dict) and repo.get("full_name") == f"{owner}/{name}"
        except GitHubError:
            return False

    def health(self) -> dict[str, Any]:
        """Report connection readiness without touching GitHub if unconfigured."""
        if not self.is_configured:
            return {"configured": False, "connected": False, "message": "GitHub is not connected yet."}
        try:
            user = self.get_authenticated_user()
            return {"configured": True, "connected": True, "github_login": user["login"]}
        except GitHubError as exc:
            return {"configured": True, "connected": False, "error_code": exc.error_code, "message": str(exc)}
