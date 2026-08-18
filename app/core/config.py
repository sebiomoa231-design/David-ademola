from functools import lru_cache
from pathlib import Path

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(PROJECT_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    app_name: str = "David AI"
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    debug: bool = False

    # Local Command Center development runs on 3001. Production must override
    # this with its exact deployed frontend origin through CORS_ORIGINS.
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000,http://localhost:3001,http://127.0.0.1:3001"
    request_timeout_seconds: int = 45
    max_upload_mb: int = 25
    data_dir: str = str(PROJECT_ROOT / "data")

    # Supabase is accessed only by the backend. Secret keys must be provided
    # through the deployment environment and are never bundled into frontend code.
    supabase_url: str = ""
    supabase_publishable_key: str = Field(
        default="",
        validation_alias=AliasChoices("SUPABASE_PUBLISHABLE_KEY", "SUPABASE_ANON_KEY"),
    )
    supabase_secret_key: str = Field(
        default="",
        validation_alias=AliasChoices("SUPABASE_SECRET_KEY", "SUPABASE_SERVICE_ROLE_KEY"),
    )
    database_url: str = ""
    supabase_storage_bucket: str = "Davidai"
    supabase_persistence_enabled: bool = False
    supabase_signed_url_ttl: int = 3600
    supabase_request_timeout_seconds: int = 20

    provider_priority: str = (
        "gemini,groq,openrouter,cloudflare,cerebras,sambanova,huggingface"
    )
    provider_max_retries: int = 1
    provider_health_timeout_seconds: int = 10

    # Agent runtime guardrails. Keep execution bounded and observable in every environment.
    agent_max_goal_chars: int = 12000
    agent_max_steps: int = 8
    agent_max_retries: int = 1
    agent_history_limit: int = 100
    external_agents_json: str = ""
    external_agent_timeout_seconds: int = 30

    openai_api_key: str = ""
    openai_api_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-5.3-mini"
    openai_image_model: str = "gpt-image-1"
    openai_tts_model: str = "gpt-4o-mini-tts"
    openai_tts_voice: str = "alloy"
    openai_stt_model: str = "gpt-4o-mini-transcribe"

    anthropic_api_key: str = ""
    anthropic_api_base_url: str = "https://api.anthropic.com/v1"
    anthropic_model: str = "claude-sonnet-4-5"

    gemini_api_key: str = Field(
        default="",
        validation_alias=AliasChoices("GEMINI_API_KEY", "Gemini_key"),
    )
    gemini_api_base_url: str = "https://generativelanguage.googleapis.com/v1beta"
    gemini_model: str = "gemini-3.6-flash"
    gemini_image_model: str = "gemini-3.1-flash-image"
    gemini_video_model: str = "veo-3.1-generate-preview"

    groq_api_key: str = Field(
        default="",
        validation_alias=AliasChoices("GROQ_API_KEY", "Groq_key"),
    )
    groq_api_base_url: str = "https://api.groq.com/openai/v1"
    groq_model: str = "llama-3.3-70b-versatile"
    groq_stt_model: str = "whisper-large-v3-turbo"

    openrouter_api_key: str = Field(
        default="",
        validation_alias=AliasChoices("OPENROUTER_API_KEY", "Openrouter_key"),
    )
    openrouter_api_base_url: str = "https://openrouter.ai/api/v1"
    openrouter_model: str = "openai/gpt-5.3-chat"

    voyage_api_key: str = ""
    voyage_api_base_url: str = "https://api.voyageai.com/v1"
    voyage_model: str = "voyage-3.5"

    elevenlabs_api_key: str = ""
    elevenlabs_api_base_url: str = "https://api.elevenlabs.io/v1"
    elevenlabs_model: str = "eleven_multilingual_v2"
    elevenlabs_stt_model: str = "scribe_v2"
    elevenlabs_voice_id: str = "5hZv9mAOcmcMt1TxA5Iz"
    elevenlabs_voice_style: str = "British, deep male, JARVIS-style"
    elevenlabs_speech_engine_id: str = ""
    elevenlabs_speech_engine_public_ws_url: str = ""

    runway_api_key: str = ""
    runway_api_base_url: str = "https://api.dev.runwayml.com/v1"
    runway_model: str = ""

    luma_api_key: str = ""
    luma_api_base_url: str = "https://api.lumalabs.ai/dream-machine/v1"
    luma_model: str = ""

    v0_api_key: str = ""
    v0_api_base_url: str = "https://api.v0.dev"
    v0_model: str = ""

    google_maps_api_key: str = ""

    render_api_key: str = ""
    render_api_base_url: str = "https://api.render.com/v1"
    render_owner_id: str = ""

    cloudflare_api_key: str = Field(
        default="",
        validation_alias=AliasChoices("CLOUDFLARE_API_KEY", "Cloudflare_key"),
    )
    cloudflare_account_id: str = ""
    cloudflare_model: str = "@cf/meta/llama-3.1-8b-instruct"

    cerebras_api_key: str = Field(
        default="",
        validation_alias=AliasChoices("CEREBRAS_API_KEY", "Cerebras_key"),
    )
    cerebras_model: str = "llama-3.3-70b"

    sambanova_api_key: str = Field(
        default="",
        validation_alias=AliasChoices("SAMBANOVA_API_KEY", "Sambanova_key"),
    )
    sambanova_model: str = "Meta-Llama-3.1-70B-Instruct"

    huggingface_api_key: str = Field(
        default="",
        validation_alias=AliasChoices("HUGGINGFACE_API_KEY", "Huggingface_key"),
    )
    huggingface_model: str = "openai/gpt-oss-120b:cerebras"

    # Owner configuration. Never put a real password in source control.
    owner_email: str = ""
    owner_password: str = ""

    # GitHub App integration (Section: multi-repository management).
    # The GitHub App is installed and approved by the owner on their own
    # account. All values are provided through the deployment environment
    # (Render) and are never bundled into frontend code, API responses,
    # or returned in error messages.
    github_app_id: str = ""
    github_app_private_key: str = ""
    github_client_id: str = ""
    github_client_secret: str = ""
    github_installation_id: str = ""
    github_installation_access_token: str = Field(
        default="",
        validation_alias=AliasChoices("GITHUB_INSTALLATION_ACCESS_TOKEN", "GITHUB_TOKEN"),
    )
    public_base_url: str = ""

    @property
    def github_is_configured(self) -> bool:
        has_installation_flow = bool(self.github_app_id and self.github_app_private_key and self.github_installation_id)
        has_oauth_flow = bool(self.github_client_id and self.github_client_secret)
        return bool(has_installation_flow or has_oauth_flow or self.github_installation_access_token)

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

    @property
    def supabase_is_configured(self) -> bool:
        return bool(self.supabase_url and self.supabase_secret_key)

    @property
    def supabase_database_is_configured(self) -> bool:
        return bool(self.supabase_url and self.supabase_secret_key and self.supabase_persistence_enabled)


@lru_cache
def get_settings() -> Settings:
    return Settings()
