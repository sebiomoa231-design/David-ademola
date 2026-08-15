from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(PROJECT_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "David AI"
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    debug: bool = False

    cors_origins: str = "http://localhost:3000"
    request_timeout_seconds: int = 45
    max_upload_mb: int = 25
    data_dir: str = str(PROJECT_ROOT / "data")

    provider_priority: str = (
        "gemini,groq,openrouter,cloudflare,cerebras,sambanova,huggingface"
    )
    provider_max_retries: int = 1

    openai_api_key: str = ""
    openai_model: str = "gpt-5.3-mini"

    gemini_api_key: str = ""
    gemini_model: str = "gemini-3.6-flash"

    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"

    openrouter_api_key: str = ""
    openrouter_model: str = "openai/gpt-5.3-chat"

    cloudflare_api_key: str = ""
    cloudflare_account_id: str = ""
    cloudflare_model: str = "@cf/meta/llama-3.1-8b-instruct"

    cerebras_api_key: str = ""
    cerebras_model: str = "llama-3.3-70b"

    sambanova_api_key: str = ""
    sambanova_model: str = "Meta-Llama-3.1-70B-Instruct"

    huggingface_api_key: str = ""
    huggingface_model: str = "openai/gpt-oss-120b:cerebras"

    # Piper TTS. The large ONNX model is intentionally not committed to
    # GitHub; build.sh downloads it from the official Piper voices repo.
    piper_executable: str = "piper"
    piper_voice_model: str = str(PROJECT_ROOT / "voices" / "en_US-ryan-high.onnx")
    piper_voice_url: str = (
        "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/"
        "en/en_US/ryan/high/en_US-ryan-high.onnx"
    )
    piper_voice_config_url: str = (
        "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/"
        "en/en_US/ryan/high/en_US-ryan-high.onnx.json"
    )

    # Owner configuration. Never put a real password in source control.
    owner_email: str = ""
    owner_password: str = ""

    @property
    def is_production(self) -> bool:
        return self.app_env.lower() == "production"

    @property
    def cors_origin_list(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.cors_origins.split(",")
            if origin.strip()
        ]

    @property
    def provider_priority_list(self) -> list[str]:
        return [
            p.strip().lower()
            for p in self.provider_priority.split(",")
            if p.strip()
        ]

    @property
    def max_upload_bytes(self) -> int:
        return self.max_upload_mb * 1024 * 1024


@lru_cache
def get_settings() -> Settings:
    return Settings()
