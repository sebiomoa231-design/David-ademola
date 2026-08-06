from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "David AI"
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    debug: bool = True
    cors_origins: str = "http://localhost:3000"
    request_timeout_seconds: int = 30
    max_upload_mb: int = 25
    provider_priority: str = (
        "gemini,groq,openrouter,cloudflare,cerebras,sambanova,huggingface"
    )

    gemini_api_key: str = ""
    groq_api_key: str = ""
    huggingface_api_key: str = ""
    openrouter_api_key: str = ""
    cloudflare_api_key: str = ""
    cerebras_api_key: str = ""
    sambanova_api_key: str = ""

    # Piper TTS — local/offline text-to-speech, no API key required.
    # piper_executable: path to the `piper` binary (installed separately,
    # see https://github.com/rhasspy/piper). piper_voice_model: path to the
    # .onnx voice model file. Defaults to the Ryan (high) model bundled in
    # backend/voices/ so it works out of the box; override in .env to use
    # a different model or an absolute path.
    piper_executable: str = "piper"
    piper_voice_model: str = "voices/en_US-ryan-high.onnx"

    @property
    def is_production(self) -> bool:
        return self.app_env.lower() == "production"

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def provider_priority_list(self) -> list[str]:
        return [p.strip() for p in self.provider_priority.split(",") if p.strip()]

    @property
    def max_upload_bytes(self) -> int:
        return self.max_upload_mb * 1024 * 1024


@lru_cache
def get_settings() -> Settings:
    return Settings()
