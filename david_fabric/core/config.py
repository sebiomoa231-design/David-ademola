from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """Configuration owned by the Intelligence Fabric boundary.

    The main David application keeps its existing provider settings in
    ``app.core.config.Settings``. Fabric settings are intentionally separate
    so importing the control plane cannot change chat, voice, or upload
    behavior.
    """

    model_config = SettingsConfigDict(
        env_file=str(PROJECT_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "David AI Intelligence Fabric"
    app_env: str = "development"
    host: str = "0.0.0.0"
    port: int = 8000
    cors_origins: str = "http://localhost:3000"

    # Kept for compatibility with the upstream Core package. The integrated
    # persistence layer uses David's JsonStorage instead of opening SQLite.
    database_path: str = str(PROJECT_ROOT / "data" / "david_fabric.sqlite3")
    storage_name: str = "intelligence_fabric"

    allow_external_side_effects: bool = False
    require_approval_for_deployment: bool = True
    require_approval_for_publish: bool = True
    require_approval_for_delete: bool = True
    require_approval_for_purchase: bool = True
    adapter_timeout_seconds: float = 2.0

    browser_use_url: str = ""
    playwright_url: str = ""
    openhands_url: str = ""
    comfyui_url: str = ""
    wan2gp_url: str = ""
    chatterbox_url: str = ""
    faster_whisper_url: str = ""
    langfuse_url: str = ""
    n8n_url: str = ""
    temporal_url: str = ""
    coolify_url: str = ""
    dokploy_url: str = ""
    creative_backend_url: str = ""
    voice_backend_url: str = ""

    @property
    def cors_origin_list(self) -> list[str]:
        return [x.strip() for x in self.cors_origins.split(",") if x.strip()]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
