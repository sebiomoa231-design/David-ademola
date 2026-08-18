from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "David AI Intelligence Fabric"
    app_env: str = "development"
    host: str = "0.0.0.0"
    port: int = 8000
    database_path: str = "data/david_fabric.sqlite3"
    cors_origins: str = "http://localhost:3000"

    allow_external_side_effects: bool = False
    require_approval_for_deployment: bool = True
    require_approval_for_publish: bool = True
    require_approval_for_delete: bool = True
    require_approval_for_purchase: bool = True

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

    @property
    def cors_origin_list(self):
        return [x.strip() for x in self.cors_origins.split(",") if x.strip()]

@lru_cache
def get_settings():
    return Settings()

settings = get_settings()
