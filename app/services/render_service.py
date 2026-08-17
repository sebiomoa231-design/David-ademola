from __future__ import annotations

from typing import Any

import httpx

from app.core.config import Settings, get_settings


class RenderApiError(RuntimeError):
    def __init__(self, message: str, *, code: str = "render_api_error", status_code: int = 502, retryable: bool = False):
        super().__init__(message)
        self.code = code
        self.status_code = status_code
        self.retryable = retryable


class RenderNotConfigured(RenderApiError):
    def __init__(self):
        super().__init__("Render API is not configured", code="render_not_configured", status_code=503)


class RenderService:
    def __init__(self, settings: Settings | None = None):
        self.settings = settings or get_settings()

    @property
    def configured(self) -> bool:
        return bool(self.settings.render_api_key and self.settings.render_owner_id)

    def _headers(self) -> dict[str, str]:
        if not self.configured:
            raise RenderNotConfigured()
        return {"Authorization": f"Bearer {self.settings.render_api_key}", "Accept": "application/json", "Content-Type": "application/json"}

    async def request(self, method: str, path: str, **kwargs: Any) -> dict[str, Any] | list[Any]:
        headers = {**self._headers(), **kwargs.pop("headers", {})}
        url = f"{self.settings.render_api_base_url.rstrip('/')}/{path.lstrip('/')}"
        try:
            async with httpx.AsyncClient(timeout=self.settings.request_timeout_seconds, follow_redirects=True) as client:
                response = await client.request(method, url, headers=headers, **kwargs)
        except httpx.TimeoutException as exc:
            raise RenderApiError("Render API request timed out", code="render_timeout", status_code=504, retryable=True) from exc
        except httpx.HTTPError as exc:
            raise RenderApiError("Render API request failed", code="render_network_error", status_code=502, retryable=True) from exc
        if response.status_code in {401, 403}:
            raise RenderApiError("Render API authentication was rejected", code="render_unauthorized", status_code=502)
        if response.status_code == 429:
            raise RenderApiError("Render API rate limit reached", code="render_rate_limited", status_code=429, retryable=True)
        if response.status_code >= 400:
            raise RenderApiError("Render API rejected the request", code="render_request_rejected", status_code=502)
        if not response.content:
            return {}
        try:
            data = response.json()
        except ValueError as exc:
            raise RenderApiError("Render API returned invalid JSON", code="render_invalid_response", status_code=502) from exc
        return data

    async def health(self) -> dict[str, Any]:
        if not self.configured:
            return {"configured": False, "connected": False, "message": "Render API is not configured."}
        try:
            data = await self.request("GET", "/services?limit=1")
            return {"configured": True, "connected": True, "service_count_sample": len(data) if isinstance(data, list) else None}
        except RenderApiError as exc:
            return {"configured": True, "connected": False, "code": exc.code, "message": str(exc)}

    async def list_services(self, *, limit: int = 20) -> dict[str, Any] | list[Any]:
        return await self.request("GET", f"/services?limit={max(1, min(limit, 100))}")

    async def create_service(self, payload: dict[str, Any]) -> dict[str, Any] | list[Any]:
        body = dict(payload)
        body.setdefault("ownerId", self.settings.render_owner_id)
        body.setdefault("autoDeploy", "yes")
        return await self.request("POST", "/services", json=body)

    async def trigger_deploy(self, service_id: str, *, clear_cache: bool = False) -> dict[str, Any] | list[Any]:
        suffix = "?clearCache=clear" if clear_cache else ""
        return await self.request("POST", f"/services/{service_id}/deploys{suffix}", json={})

    async def get_deploy(self, service_id: str, deploy_id: str) -> dict[str, Any] | list[Any]:
        return await self.request("GET", f"/services/{service_id}/deploys/{deploy_id}")

    async def list_deploys(self, service_id: str, *, limit: int = 20) -> dict[str, Any] | list[Any]:
        return await self.request("GET", f"/services/{service_id}/deploys?limit={max(1, min(limit, 100))}")
