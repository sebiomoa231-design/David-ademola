"""Create or recreate the ElevenLabs Speech Engine resource for David AI.

Run this administrative script once after setting ELEVENLABS_API_KEY and
ELEVENLABS_SPEECH_ENGINE_PUBLIC_WS_URL. It prints only the resulting engine ID.
"""
from __future__ import annotations

import asyncio
import os

from dotenv import load_dotenv


async def create_speech_engine() -> str:
    from elevenlabs import AsyncElevenLabs

    api_key = os.environ.get("ELEVENLABS_API_KEY", "").strip()
    public_ws_url = os.environ.get("ELEVENLABS_SPEECH_ENGINE_PUBLIC_WS_URL", "").strip()
    name = os.environ.get("ELEVENLABS_SPEECH_ENGINE_NAME", "David AI Speech Engine").strip()

    if not api_key:
        raise RuntimeError("ELEVENLABS_API_KEY is required")
    if not public_ws_url.startswith("wss://"):
        raise RuntimeError("ELEVENLABS_SPEECH_ENGINE_PUBLIC_WS_URL must start with wss://")
    if not public_ws_url.endswith("/ws"):
        raise RuntimeError("ELEVENLABS_SPEECH_ENGINE_PUBLIC_WS_URL must end with /ws")

    client = AsyncElevenLabs(api_key=api_key)
    engine = await client.speech_engine.create(
        name=name,
        speech_engine={"ws_url": public_ws_url},
        overrides={"first_message": True},
    )
    return engine.engine_id


async def main() -> None:
    load_dotenv()
    engine_id = await create_speech_engine()
    print(f"Speech Engine ID: {engine_id}")


if __name__ == "__main__":
    asyncio.run(main())
