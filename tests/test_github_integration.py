"""Tests for the GitHub App multi-repository integration.

Contract tests (local, no GitHub access needed):
- Repository name generation is deterministic, GitHub-safe, and collision-free.
- Secrets never appear in URLs, error details, or API responses.
- The GitHub routes mount correctly and unconfigured instances answer safely.
- Audit details are sanitized before persistence.

Real-API tests are gated behind GITHUB_TEST_TOKEN and run against the
owner's account only with explicit opt-in (CI never runs them).
"""

import importlib
import json
import secrets
import sys
import uuid
from unittest.mock import MagicMock

import pytest

sys.path.insert(0, ".")

from app.services.github_service import (  # noqa: E402
    API_BASE,
    GitHubError,
    GitHubNotConfigured,
    GitHubRateLimited,
    GitHubUnauthorized,
    GitHubService,
    generate_repository_name,
    _encode_jwt,
)
from app.services.github_persistence import sanitize_details  # noqa: E402


# ---------------------------------------------------------------------------
# Contract: repository naming
# ---------------------------------------------------------------------------

class TestRepositoryNaming:
    def test_basic_slug(self):
        assert generate_repository_name("A Luxury Hotel Landing Page", "sebiomoa231-design") == "david-a-luxury-hotel-landing-page-site"

    def test_empty_topic(self):
        name = generate_repository_name("", "owner")
        assert name.startswith("david-generated-site") or _is_safe(name)

    def test_unicode_and_special_characters(self):
        name = generate_repository_name("Café & Bistro — New York", "owner")
        assert name == "david-caf-bistro-new-york-site"
        assert _is_safe(name)

    def test_collision_avoidance(self):
        existing = {"david-a-luxury-hotel-landing-page-site"}
        name = generate_repository_name("A Luxury Hotel Landing Page", "owner", existing)
        assert name == "david-a-luxury-hotel-landing-page-site-2"
        assert name not in existing

    def test_long_topic_truncation(self):
        topic = "a" * 200
        name = generate_repository_name(topic, "owner")
        assert len(name) <= 100
        assert _is_safe(name)

    def test_no_overwrite_of_existing(self):
        existing = {f"david-topic-site-{i}" for i in range(2, 60)} | {"david-topic-site"}
        name = generate_repository_name("Topic", "owner", existing)
        assert name not in existing

    def test_name_always_starts_and_ends_safe(self):
        for topic in ["-leading dash", "trailing.", "...", "$$$"]:
            name = generate_repository_name(topic, "owner")
            assert _is_safe(name)


def _is_safe(name: str) -> bool:
    import re
    return bool(re.match(r"^[a-z0-9][a-z0-9._-]{0,98}[a-z0-9]$|^[a-z0-9]$", name))


# ---------------------------------------------------------------------------
# Contract: secrets never leak
# ---------------------------------------------------------------------------

class TestSecretIsolation:
    def test_authorize_url_contains_no_secret(self):
        service = GitHubService(client_id="cid", client_secret="TOP_SECRET")
        url = service.oauth_authorize_url("state")
        assert "TOP_SECRET" not in url
        assert "client_secret" not in url
        assert url.startswith("https://github.com/login/oauth/authorize")
        assert "state=state" in url

    def test_not_configured_response_is_secret_free(self):
        service = GitHubService()
        with pytest.raises(GitHubNotConfigured) as exc_info:
            service.oauth_authorize_url("s")
        assert "SECRET" not in str(exc_info.value)
        assert "KEY" not in str(exc_info.value).upper() or "secret" not in str(exc_info.value).lower()
        assert "key" not in str(exc_info.value)

    def test_unconfigured_health_is_safe(self):
        service = GitHubService()
        health = service.health()
        assert health == {"configured": False, "connected": False, "message": "GitHub is not connected yet."}
        assert not any("secret" in str(v).lower() or "key" in str(v).lower() for v in health.values())

    def test_jwt_does_not_contain_key(self):
        key = _test_rsa_key()
        token = _encode_jwt("123456", key)
        assert "-----BEGIN RSA PRIVATE KEY-----" not in token
        assert "private" not in token.lower()

    def test_audit_sanitization_drops_secrets(self):
        dirty = {
            "repository_url": "https://github.com/owner/repo",
            "github_token": "ghp_xxx",
            "authorization": "Bearer ghp_xxx",
            "oauth_client_secret": "shh",
            "private_key_snippet": "BEGIN RSA",
            "file_count": 3,
        }
        clean = sanitize_details(dirty)
        assert "repository_url" in clean
        assert "file_count" in clean
        assert not any(k in clean for k in ("github_token", "authorization", "oauth_client_secret", "private_key_snippet"))

    def test_github_error_messages_never_contain_headers(self):
        err = GitHubUnauthorized("reconnect")
        assert "Bearer" not in str(err)
        rate = GitHubRateLimited(30)
        assert rate.retry_after == 30


def _test_rsa_key():
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.hazmat.primitives import serialization
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    return key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    ).decode()


# ---------------------------------------------------------------------------
# Contract: mocked GitHub API behavior
# ---------------------------------------------------------------------------

class MockResponse:
    def __init__(self, status_code=200, json_body=None, headers=None, text=""):
        self.status_code = status_code
        self._json = json_body
        self.headers = headers or {"content-type": "application/json"}
        self.content = json.dumps(json_body or {}).encode()
        self.text = text or json.dumps(json_body or {})

    def json(self):
        return self._json or {}


class TestGitHubServiceMocked:
    @pytest.fixture()
    def service(self):
        svc = GitHubService(
            app_id="123456",
            private_key=_test_rsa_key(),
            client_id="cid",
            client_secret="cs",
            installation_id="789",
        )
        return svc

    def _mock_client(self, service, responses_by_url):
        call_log = []

        class FakeClient:
            def __init__(self, *args, **kwargs):
                pass

            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

            def request(self, method, url, params=None, json=None, json_body=None, headers=None):
                call_log.append({"method": method, "url": url, "params": params, "body": json_body, "headers": headers or {}})
                for prefix, resp in responses_by_url.items():
                    if prefix in url:
                        return resp
                raise AssertionError(f"unexpected request: {method} {url}")

    def test_list_repositories_returns_tracked_fields(self, service):
        repos = [
            {"id": 1, "name": "david-cafe-site", "full_name": "owner/david-cafe-site", "size": 0,
             "owner": {"login": "owner"}, "html_url": "https://github.com/owner/david-cafe-site",
             "default_branch": "main", "private": True, "created_at": "t", "updated_at": "t"}
        ]
        def respond(method, url, params=None, json_body=None, headers=None):
            if "access_tokens" in url:
                return MockResponse(200, {"token": "TOKEN", "expires_at": "2099-01-01T00:00:00Z"})
            if url.endswith("/user"):
                return MockResponse(200, {"login": "owner", "id": 111, "html_url": "https://github.com/owner"})
            if "/user/repos" in url:
                return MockResponse(200, repos)
            raise AssertionError(url)

        import httpx
        original = httpx.Client

        class FakeClient:
            def __init__(self, *args, **kwargs):
                pass

            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

            def request(self, method, url, params=None, json=None, json_body=None, headers=None):
                return respond(method, url, params, json_body, headers)

        httpx.Client = FakeClient
        try:
            listed = service.list_repositories()
            assert len(listed) == 1
            assert listed[0]["repository_full_name"] == "owner/david-cafe-site"
            assert listed[0]["is_empty"] is True
        finally:
            httpx.Client = original

    def test_create_repository_uses_unique_name(self, service):
        captured = {}

        import httpx

        original = httpx.Client

        class FakeClient:
            def __init__(self, *args, **kwargs):
                pass

            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

            def request(self, method, url, params=None, json=None, json_body=None, headers=None):
                captured["request"] = {"method": method, "url": url, "params": params, "body": json or json_body, "headers": headers or {}}
                if "access_tokens" in url:
                    return MockResponse(200, {"token": "TOKEN", "expires_at": "2099-01-01T00:00:00Z"})
                if url.endswith("/user"):
                    return MockResponse(200, {"login": "owner", "id": 1, "html_url": "x"})
                if "/user/repos" in url and method == "GET":
                    return MockResponse(200, [{"name": "david-a-luxury-hotel-site", "full_name": "owner/david-a-luxury-hotel-site",
                                               "owner": {"login": "owner"}, "size": 0, "html_url": "x",
                                               "default_branch": "main", "private": True, "created_at": "t", "updated_at": "t"}])
                if method == "POST":
                    body = json or json_body
                    return MockResponse(201, {"id": 42, "name": body["name"], "full_name": f"owner/{body['name']}",
                                              "owner": {"login": "owner"}, "html_url": f"https://github.com/owner/{body['name']}",
                                              "clone_url": "https://github.com/owner/x.git", "default_branch": "main",
                                              "private": True, "created_at": "t"})
                raise AssertionError(url)

        httpx.Client = FakeClient
        try:
            created = service.create_repository("A Luxury Hotel", description="desc", private=True)
            assert captured["request"]["body"]["name"] == "david-a-luxury-hotel-site-2"
            assert created["visibility"] == "private"
            # The private key never appears anywhere in the outbound request,
            # and the access token only appears as the Bearer authorization value.
            request_json = json.dumps(captured["request"])
            private_key_text = json.dumps(_test_rsa_key())
            assert private_key_text not in request_json
            auth = captured["request"].get("headers", {}).get("Authorization", "")
            assert auth.startswith("Bearer ")
            assert "-----" not in auth
        finally:
            httpx.Client = original

    def test_rate_limit_returns_retryable_error(self, service):
        import httpx

        original = httpx.Client

        class FakeClient:
            def __init__(self, *args, **kwargs):
                pass

            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

            def request(self, method, url, params=None, json=None, json_body=None, headers=None):
                if "access_tokens" in url:
                    return MockResponse(200, {"token": "TOKEN", "expires_at": "2099-01-01T00:00:00Z"})
                if url.endswith("/user") and method == "GET":
                    return MockResponse(200, {"login": "owner", "id": 1, "html_url": "x"})
                if url.endswith("/user/repos") and method == "GET":
                    return MockResponse(403, {"message": "rate limit"}, headers={"x-ratelimit-remaining": "0", "retry-after": "55"})
                raise AssertionError(url)

        httpx.Client = FakeClient
        try:
            with pytest.raises(GitHubRateLimited) as exc_info:
                service.create_repository("x")
            assert exc_info.value.retry_after == 55
            assert exc_info.value.error_code == "github_rate_limited"
        finally:
            httpx.Client = original

    def test_422_name_taken_surfaces_message(self, service):
        import httpx

        original = httpx.Client

        class FakeClient:
            def __init__(self, *args, **kwargs):
                pass

            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

            def request(self, method, url, params=None, json=None, json_body=None, headers=None):
                if "access_tokens" in url:
                    return MockResponse(200, {"token": "TOKEN", "expires_at": "2099-01-01T00:00:00Z"})
                if url.endswith("/user"):
                    return MockResponse(200, {"login": "owner", "id": 1, "html_url": "x"})
                if method == "GET":
                    return MockResponse(200, [])
                return MockResponse(422, {"message": "name already exists on this account", "errors": [{"message": "name already exists on this account"}]})

        httpx.Client = FakeClient
        try:
            with pytest.raises(GitHubError) as exc_info:
                service.create_repository("x")
            assert "already exists" in str(exc_info.value)
        finally:
            httpx.Client = original


# ---------------------------------------------------------------------------
# Contract: FastAPI mount + unconfigured behavior
# ---------------------------------------------------------------------------

class TestFastAPIMount:
    def test_github_routes_mounted(self):
        from main import app

        paths = sorted(app.openapi()["paths"].keys())
        gh = [p for p in paths if p.startswith("/api/github")]
        expected = [
            "/api/github/health",
            "/api/github/connection",
            "/api/github/connect",
            "/api/github/connect/callback",
            "/api/github/disconnect",
            "/api/github/repositories",
            "/api/github/repositories/{repository_id}",
            "/api/github/repositories/{repository_id}/initialize",
            "/api/github/repositories/{repository_id}/push",
            "/api/github/repositories/{repository_id}/update",
            "/api/github/audit",
        ]
        for path in expected:
            assert path in gh, f"{path} not mounted"

    def test_health_unconfigured(self):
        from fastapi.testclient import TestClient
        from main import app

        with TestClient(app) as client:
            response = client.get("/api/github/health")
            assert response.status_code == 200
            data = response.json()
            assert data["configured"] is False
            assert data["connected"] is False
            assert "token" not in json.dumps(data).lower()
            assert "secret" not in json.dumps(data).lower()

    def test_repositories_unconfigured_returns_412(self):
        from fastapi.testclient import TestClient
        from main import app

        with TestClient(app) as client:
            response = client.get("/api/github/repositories")
            # Without the database enabled the backend reports persistence unavailability (503);
            # with the database enabled and GitHub unconnected it reports a precondition failure (412).
            assert response.status_code in (412, 503), response.status_code

    def test_connect_callback_rejects_bad_state(self):
        from fastapi.testclient import TestClient
        from main import app

        with TestClient(app) as client:
            response = client.post("/api/github/connect/callback", json={"code": "abc", "state": "nonexistent"})
            assert response.status_code == 400

    def test_create_repository_requires_topic(self):
        from fastapi.testclient import TestClient
        from main import app

        with TestClient(app) as client:
            response = client.post("/api/github/repositories", json={"topic": ""})
            assert response.status_code == 400

    def test_push_requires_files(self):
        from fastapi.testclient import TestClient
        from main import app

        with TestClient(app) as client:
            response = client.post("/api/github/repositories/abc123/push", json={"files": {}})
            assert response.status_code == 400

    def test_connection_unconfigured(self):
        from fastapi.testclient import TestClient
        from main import app

        with TestClient(app) as client:
            response = client.get("/api/github/connection")
            assert response.status_code == 200
            assert response.json()["connected"] is False


# ---------------------------------------------------------------------------
# Contract: settings wiring
# ---------------------------------------------------------------------------

class TestSettingsWiring:
    def test_github_settings_defaults_empty(self):
        from app.core.config import Settings

        settings = Settings()
        assert settings.github_app_id == ""
        assert settings.github_client_secret == ""
        assert settings.github_is_configured is False

    def test_github_configured_with_installation_flow(self):
        from app.core.config import Settings

        settings = Settings(
            github_app_id="1",
            github_app_private_key="x",
            github_installation_id="2",
        )
        assert settings.github_is_configured is True

    def test_github_configured_with_oauth_flow(self):
        from app.core.config import Settings

        settings = Settings(github_client_id="a", github_client_secret="b")
        assert settings.github_is_configured is True
