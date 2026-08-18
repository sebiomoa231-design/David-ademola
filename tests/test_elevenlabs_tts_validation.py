import asyncio

import httpx
import pytest

from app.providers import elevenlabs_tts


class FakeAsyncClient:
    response: httpx.Response

    def __init__(self, *, response: httpx.Response, **_kwargs):
        self.response = response

    async def __aenter__(self):
        return self

    async def __aexit__(self, _exc_type, _exc, _traceback):
        return None

    async def post(self, *_args, **_kwargs):
        return self.response


def response(*, status_code=200, content=b"ID3valid-mp3", content_type="audio/mpeg"):
    return httpx.Response(
        status_code,
        headers={"content-type": content_type},
        content=content,
        request=httpx.Request("POST", "https://api.elevenlabs.io/v1/text-to-speech/test"),
    )


def client():
    return elevenlabs_tts.ElevenLabsTTSClient(
        api_key="test-key",
        voice_id="test-voice",
        model_id="eleven_multilingual_v2",
    )


def test_tts_accepts_real_mp3_response(monkeypatch):
    monkeypatch.setattr(
        elevenlabs_tts.httpx,
        "AsyncClient",
        lambda **kwargs: FakeAsyncClient(response=response(), **kwargs),
    )
    audio = asyncio.run(client().synthesize("Hello David"))
    assert audio.startswith(b"ID3")


@pytest.mark.parametrize(
    ("content", "content_type", "message"),
    [
        (b"", "audio/mpeg", "empty audio response"),
        (b'{"detail":"quota exceeded"}', "application/json", "instead of audio"),
        (b"not-an-mp3", "audio/mpeg", "invalid MP3 data"),
    ],
)
def test_tts_rejects_invalid_audio_response(monkeypatch, content, content_type, message):
    monkeypatch.setattr(
        elevenlabs_tts.httpx,
        "AsyncClient",
        lambda **kwargs: FakeAsyncClient(
            response=response(content=content, content_type=content_type), **kwargs
        ),
    )
    with pytest.raises(elevenlabs_tts.ElevenLabsError, match=message):
        asyncio.run(client().synthesize("Hello David"))


def test_tts_surfaces_provider_error_detail(monkeypatch):
    provider_response = response(
        status_code=401,
        content=b'{"detail":"invalid api key"}',
        content_type="application/json",
    )
    monkeypatch.setattr(
        elevenlabs_tts.httpx,
        "AsyncClient",
        lambda **kwargs: FakeAsyncClient(response=provider_response, **kwargs),
    )
    with pytest.raises(elevenlabs_tts.ElevenLabsError, match="invalid api key"):
        asyncio.run(client().synthesize("Hello David"))
