"""Provider catalog and capability routing for David AI.

This module deliberately keeps credentials server-side and reports only
non-sensitive readiness metadata. Provider adapters are small HTTP boundaries;
unsupported operations return explicit errors instead of fabricated success.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

import httpx

from app.core.config import Settings, get_settings


class ProviderIntegrationError(RuntimeError):
    """Safe provider error that can be surfaced to the API client."""

    def __init__(self, message: str, *, code: str = "provider_error", status_code: int = 502, retryable: bool = False):
        super().__init__(message)
        self.code = code
        self.status_code = status_code
        self.retryable = retryable


class ProviderNotConfigured(ProviderIntegrationError):
    def __init__(self, provider: str):
        super().__init__(f"{provider} is not configured", code="provider_not_configured", status_code=503)


class CapabilityNotSupported(ProviderIntegrationError):
    def __init__(self, capability: str, provider: str):
        super().__init__(f"{provider} does not expose a verified adapter for {capability}", code="capability_not_supported", status_code=501)


@dataclass(frozen=True)
class ProviderSpec:
    id: str
    label: str
    category: str
    capabilities: tuple[str, ...]
    credential_attr: str | None = None
    base_url_attr: str | None = None
    default_base_url: str = ""
    model_attr: str | None = None
    docs_url: str = ""
    status: str = "supported"
    notes: str = ""

    def configured(self, settings: Settings) -> bool:
        if not self.credential_attr:
            return True
        return bool(str(getattr(settings, self.credential_attr, "") or "").strip())

    def base_url(self, settings: Settings) -> str:
        value = str(getattr(settings, self.base_url_attr, "") or "") if self.base_url_attr else ""
        return (value or self.default_base_url).rstrip("/")

    def model(self, settings: Settings) -> str | None:
        return str(getattr(settings, self.model_attr, "") or "") if self.model_attr else None


PROVIDERS: tuple[ProviderSpec, ...] = (
    ProviderSpec("openai", "OpenAI", "reasoning", ("reasoning", "image", "tts", "stt"), "openai_api_key", "openai_api_base_url", "https://api.openai.com/v1", "openai_model", "https://developers.openai.com/api/reference/overview/"),
    ProviderSpec("anthropic", "Anthropic Claude", "reasoning", ("reasoning",), "anthropic_api_key", "anthropic_api_base_url", "https://api.anthropic.com/v1", "anthropic_model", "https://platform.claude.com/docs/en/api/overview"),
    ProviderSpec("gemini", "Google Gemini", "reasoning", ("reasoning", "image", "video"), "gemini_api_key", "gemini_api_base_url", "https://generativelanguage.googleapis.com/v1beta", "gemini_model", "https://ai.google.dev/gemini-api/docs"),
    ProviderSpec("groq", "Groq", "reasoning", ("reasoning", "stt"), "groq_api_key", "groq_api_base_url", "https://api.groq.com/openai/v1", "groq_model", "https://console.groq.com/docs"),
    ProviderSpec("openrouter", "OpenRouter", "reasoning", ("reasoning",), "openrouter_api_key", "openrouter_api_base_url", "https://openrouter.ai/api/v1", "openrouter_model", "https://openrouter.ai/docs/api-reference"),
    ProviderSpec("voyage", "Voyage AI", "embeddings", ("embeddings",), "voyage_api_key", "voyage_api_base_url", "https://api.voyageai.com/v1", "voyage_model", "https://docs.voyageai.com/"),
    ProviderSpec("elevenlabs", "ElevenLabs", "voice", ("tts", "stt"), "elevenlabs_api_key", "elevenlabs_api_base_url", "https://api.elevenlabs.io/v1", "elevenlabs_model", "https://elevenlabs.io/docs/overview/capabilities/text-to-speech"),
    ProviderSpec("runway", "Runway", "video", ("video",), "runway_api_key", "runway_api_base_url", "https://api.dev.runwayml.com/v1", "runway_model", "https://dev.runwayml.com/", status="adapter_pending", notes="Endpoint schema is intentionally gated until the configured API version is verified."),
    ProviderSpec("luma", "Luma", "video", ("video",), "luma_api_key", "luma_api_base_url", "https://api.lumalabs.ai/dream-machine/v1", "luma_model", "https://docs.lumalabs.ai/docs/video-generation", status="adapter_pending", notes="Endpoint schema is intentionally gated until the configured API version is verified."),
    ProviderSpec("v0", "Vercel v0", "website", ("website",), "v0_api_key", "v0_api_base_url", "https://api.v0.dev", "v0_model", "https://v0.dev/docs", status="adapter_pending", notes="The adapter accepts an explicit endpoint only after the current API contract is configured."),
    ProviderSpec("google-maps", "Google Maps", "maps", ("maps",), "google_maps_api_key", None, "", None, "https://developers.google.com/maps/documentation/javascript/get-api-key", status="frontend_key_only", notes="Maps Demo Key is a browser-facing map-rendering credential; geocoding and server APIs require separate enablement."),
    ProviderSpec("render", "Render", "deployment", ("deployment",), "render_api_key", "render_api_base_url", "https://api.render.com/v1", None, "https://api-docs.render.com/reference/introduction"),
    ProviderSpec("github", "GitHub App", "source-control", ("repository", "deployment"), None, None, "", None, "https://docs.github.com/en/apps", status="existing_integration"),
)


class ProviderRegistry:
    def __init__(self, settings: Settings | None = None):
        self.settings = settings or get_settings()
        self._by_id = {item.id: item for item in PROVIDERS}

    def get(self, provider_id: str) -> ProviderSpec | None:
        return self._by_id.get(provider_id.strip().lower())

    def list(self) -> list[dict[str, Any]]:
        return [self._public_status(item) for item in PROVIDERS]

    def _public_status(self, spec: ProviderSpec) -> dict[str, Any]:
        configured = spec.configured(self.settings)
        return {
            "id": spec.id,
            "label": spec.label,
            "category": spec.category,
            "capabilities": list(spec.capabilities),
            "configured": configured,
            "status": spec.status if configured else "not_configured",
            "model": spec.model(self.settings) if configured else None,
            "docs_url": spec.docs_url,
            "notes": spec.notes,
        }

    def capability_candidates(self, capability: str, preferred: Iterable[str] | None = None) -> list[ProviderSpec]:
        requested = [str(item).strip().lower() for item in (preferred or []) if str(item).strip()]
        for item in self.settings.provider_priority_list:
            if item not in requested:
                requested.append(item)
        requested.extend(item.id for item in PROVIDERS if item.id not in requested)
        return [self._by_id[item] for item in requested if item in self._by_id and capability in self._by_id[item].capabilities]

    def select(self, capability: str, preferred: Iterable[str] | None = None) -> ProviderSpec:
        candidates = self.capability_candidates(capability, preferred)
        pending: list[ProviderSpec] = []
        for spec in candidates:
            if not spec.configured(self.settings):
                continue
            if spec.status in {"adapter_pending", "frontend_key_only"}:
                pending.append(spec)
                continue
            return spec
        if pending:
            return pending[0]
        if candidates:
            raise ProviderNotConfigured(candidates[0].id)
        raise ProviderIntegrationError(f"No provider is registered for {capability}", code="capability_unregistered", status_code=501)


class CapabilityRouter:
    """Route capability requests through verified provider HTTP contracts."""

    def __init__(self, settings: Settings | None = None):
        self.settings = settings or get_settings()
        self.registry = ProviderRegistry(self.settings)

    async def execute(self, capability: str, payload: dict[str, Any], preferred: Iterable[str] | None = None) -> dict[str, Any]:
        provider = self.registry.select(capability, preferred)
        if capability == "reasoning":
            return await self._reasoning(provider, payload)
        if capability == "embeddings":
            return await self._embeddings(provider, payload)
        if capability == "tts":
            return await self._tts(provider, payload)
        if capability == "stt":
            return await self._stt(provider, payload)
        if capability == "image":
            return await self._image(provider, payload)
        if capability == "video":
            raise CapabilityNotSupported(capability, provider.id)
        if capability in {"website", "maps", "deployment"}:
            raise CapabilityNotSupported(capability, provider.id)
        raise ProviderIntegrationError(f"Unknown capability: {capability}", code="capability_unknown", status_code=400)

    def _key(self, provider: ProviderSpec) -> str:
        return str(getattr(self.settings, provider.credential_attr or "", "") or "")

    async def _request(self, method: str, url: str, *, headers: dict[str, str], **kwargs: Any) -> httpx.Response:
        timeout = httpx.Timeout(self.settings.request_timeout_seconds)
        try:
            async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
                response = await client.request(method, url, headers=headers, **kwargs)
        except httpx.TimeoutException as exc:
            raise ProviderIntegrationError("Provider request timed out", code="provider_timeout", status_code=504, retryable=True) from exc
        except httpx.HTTPError as exc:
            raise ProviderIntegrationError("Provider request failed", code="provider_network_error", status_code=502, retryable=True) from exc
        if response.status_code in {401, 403}:
            raise ProviderIntegrationError("Provider authentication was rejected", code="provider_unauthorized", status_code=502)
        if response.status_code == 429:
            raise ProviderIntegrationError("Provider rate limit reached", code="provider_rate_limited", status_code=429, retryable=True)
        if response.status_code >= 400:
            raise ProviderIntegrationError("Provider rejected the request", code="provider_request_rejected", status_code=502)
        return response

    async def _reasoning(self, provider: ProviderSpec, payload: dict[str, Any]) -> dict[str, Any]:
        prompt = str(payload.get("prompt") or payload.get("objective") or "").strip()
        if not prompt:
            raise ProviderIntegrationError("A prompt is required", code="invalid_request", status_code=422)
        key = self._key(provider)
        model = str(payload.get("model") or provider.model(self.settings) or "")
        if provider.id in {"openai", "groq", "openrouter"}:
            headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
            body = {"model": model, "input": prompt} if provider.id == "openai" else {"model": model, "messages": [{"role": "user", "content": prompt}]}
            response = await self._request("POST", f"{provider.base_url(self.settings)}/responses" if provider.id == "openai" else f"{provider.base_url(self.settings)}/chat/completions", headers=headers, json=body)
            data = response.json()
            text = data.get("output_text") or self._chat_text(data)
            return {"provider": provider.id, "model": model, "text": text, "raw": self._safe_metadata(data)}
        if provider.id == "anthropic":
            headers = {"x-api-key": key, "anthropic-version": "2023-06-01", "Content-Type": "application/json"}
            body = {"model": model, "max_tokens": int(payload.get("max_tokens") or 2048), "messages": [{"role": "user", "content": prompt}]}
            data = (await self._request("POST", f"{provider.base_url(self.settings)}/messages", headers=headers, json=body)).json()
            text = "".join(str(item.get("text", "")) for item in data.get("content", []) if isinstance(item, dict))
            return {"provider": provider.id, "model": model, "text": text, "raw": self._safe_metadata(data)}
        if provider.id == "gemini":
            headers = {"x-goog-api-key": key, "Content-Type": "application/json"}
            body = {"contents": [{"role": "user", "parts": [{"text": prompt}]}]}
            data = (await self._request("POST", f"{provider.base_url(self.settings)}/models/{model}:generateContent", headers=headers, json=body)).json()
            text = "".join(str(part.get("text", "")) for candidate in data.get("candidates", []) for part in candidate.get("content", {}).get("parts", []) if isinstance(part, dict))
            return {"provider": provider.id, "model": model, "text": text, "raw": self._safe_metadata(data)}
        raise CapabilityNotSupported("reasoning", provider.id)

    @staticmethod
    def _chat_text(data: dict[str, Any]) -> str:
        choices = data.get("choices") or []
        if not choices:
            return ""
        message = choices[0].get("message") or {}
        content = message.get("content", "")
        if isinstance(content, list):
            return "".join(str(item.get("text", "")) for item in content if isinstance(item, dict))
        return str(content)

    async def _embeddings(self, provider: ProviderSpec, payload: dict[str, Any]) -> dict[str, Any]:
        texts = payload.get("input") or payload.get("texts")
        if isinstance(texts, str):
            texts = [texts]
        if not isinstance(texts, list) or not texts:
            raise ProviderIntegrationError("input must contain one or more texts", code="invalid_request", status_code=422)
        headers = {"Authorization": f"Bearer {self._key(provider)}", "Content-Type": "application/json"}
        body = {"model": str(payload.get("model") or provider.model(self.settings) or "voyage-3.5"), "input": texts}
        data = (await self._request("POST", f"{provider.base_url(self.settings)}/embeddings", headers=headers, json=body)).json()
        return {"provider": provider.id, "model": body["model"], "embeddings": [item.get("embedding") for item in data.get("data", [])], "usage": data.get("usage")}

    async def _tts(self, provider: ProviderSpec, payload: dict[str, Any]) -> dict[str, Any]:
        text = str(payload.get("text") or "").strip()
        if not text:
            raise ProviderIntegrationError("text is required", code="invalid_request", status_code=422)
        if provider.id == "openai":
            headers = {"Authorization": f"Bearer {self._key(provider)}", "Content-Type": "application/json"}
            body = {"model": str(payload.get("model") or self.settings.openai_tts_model), "voice": str(payload.get("voice") or self.settings.openai_tts_voice), "input": text, "response_format": str(payload.get("format") or "mp3")}
            response = await self._request("POST", f"{provider.base_url(self.settings)}/audio/speech", headers=headers, json=body)
            return {"provider": provider.id, "content_type": response.headers.get("content-type", "audio/mpeg"), "audio_bytes": response.content}
        if provider.id == "elevenlabs":
            voice_id = str(payload.get("voice_id") or self.settings.elevenlabs_voice_id or "")
            if not voice_id:
                raise ProviderIntegrationError("ElevenLabs voice_id is not configured", code="provider_missing_setting", status_code=422)
            headers = {"xi-api-key": self._key(provider), "Content-Type": "application/json", "Accept": "audio/mpeg"}
            body = {"text": text, "model_id": str(payload.get("model") or provider.model(self.settings) or "eleven_multilingual_v2")}
            response = await self._request("POST", f"{provider.base_url(self.settings)}/text-to-speech/{voice_id}", headers=headers, json=body)
            return {"provider": provider.id, "content_type": response.headers.get("content-type", "audio/mpeg"), "audio_bytes": response.content}
        raise CapabilityNotSupported("tts", provider.id)

    async def _stt(self, provider: ProviderSpec, payload: dict[str, Any]) -> dict[str, Any]:
        content = payload.get("audio_bytes")
        filename = str(payload.get("filename") or "audio.wav")
        if not isinstance(content, (bytes, bytearray)):
            raise ProviderIntegrationError("audio_bytes is required for speech-to-text", code="invalid_request", status_code=422)
        if provider.id in {"openai", "groq"}:
            headers = {"Authorization": f"Bearer {self._key(provider)}"}
            files = {"file": (filename, bytes(content), str(payload.get("content_type") or "audio/wav"))}
            data = {"model": str(payload.get("model") or (self.settings.openai_stt_model if provider.id == "openai" else self.settings.groq_stt_model))}
            response = await self._request("POST", f"{provider.base_url(self.settings)}/audio/transcriptions", headers=headers, files=files, data=data)
            result = response.json()
            return {"provider": provider.id, "model": data["model"], "text": result.get("text", ""), "raw": self._safe_metadata(result)}
        if provider.id == "elevenlabs":
            headers = {"xi-api-key": self._key(provider)}
            files = {"file": (filename, bytes(content), str(payload.get("content_type") or "audio/wav"))}
            data = {"model_id": str(payload.get("model") or self.settings.elevenlabs_stt_model)}
            response = await self._request("POST", f"{provider.base_url(self.settings)}/speech-to-text", headers=headers, files=files, data=data)
            result = response.json()
            return {"provider": provider.id, "model": data["model_id"], "text": result.get("text", ""), "raw": self._safe_metadata(result)}
        raise CapabilityNotSupported("stt", provider.id)

    async def _image(self, provider: ProviderSpec, payload: dict[str, Any]) -> dict[str, Any]:
        prompt = str(payload.get("prompt") or "").strip()
        if not prompt:
            raise ProviderIntegrationError("prompt is required", code="invalid_request", status_code=422)
        if provider.id == "openai":
            headers = {"Authorization": f"Bearer {self._key(provider)}", "Content-Type": "application/json"}
            body = {"model": str(payload.get("model") or self.settings.openai_image_model), "prompt": prompt, "size": str(payload.get("size") or "1024x1024"), "quality": str(payload.get("quality") or "auto"), "n": int(payload.get("n") or 1), "response_format": "b64_json"}
            data = (await self._request("POST", f"{provider.base_url(self.settings)}/images/generations", headers=headers, json=body)).json()
            return {"provider": provider.id, "model": body["model"], "images": [{"b64_json": item.get("b64_json"), "revised_prompt": item.get("revised_prompt")} for item in data.get("data", [])]}
        if provider.id == "gemini":
            headers = {"x-goog-api-key": self._key(provider), "Content-Type": "application/json"}
            body = {"contents": [{"role": "user", "parts": [{"text": prompt}]}], "generationConfig": {"responseModalities": ["TEXT", "IMAGE"]}}
            data = (await self._request("POST", f"{provider.base_url(self.settings)}/models/{str(payload.get('model') or self.settings.gemini_image_model)}:generateContent", headers=headers, json=body)).json()
            images: list[dict[str, Any]] = []
            texts: list[str] = []
            for candidate in data.get("candidates", []):
                for part in candidate.get("content", {}).get("parts", []):
                    if not isinstance(part, dict):
                        continue
                    if part.get("text"):
                        texts.append(str(part["text"]))
                    inline = part.get("inlineData") or part.get("inline_data")
                    if inline:
                        images.append({"mime_type": inline.get("mimeType") or inline.get("mime_type"), "data": inline.get("data")})
            return {"provider": provider.id, "model": str(payload.get('model') or self.settings.gemini_image_model), "images": images, "text": "".join(texts)}
        raise CapabilityNotSupported("image", provider.id)

    @staticmethod
    def _safe_metadata(data: dict[str, Any]) -> dict[str, Any]:
        return {key: value for key, value in data.items() if key not in {"choices", "output", "content", "data", "candidates", "embedding", "embeddings"}}
