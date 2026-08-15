import httpx
from david_fabric.core.config import settings
from david_fabric.services.registry import load_capabilities

URL_ATTRS = {
    "browser-use": "browser_use_url",
    "playwright": "playwright_url",
    "openhands": "openhands_url",
    "comfyui": "comfyui_url",
    "wan2gp": "wan2gp_url",
    "chatterbox": "chatterbox_url",
    "faster-whisper": "faster_whisper_url",
    "langfuse": "langfuse_url",
    "n8n": "n8n_url",
    "temporal": "temporal_url",
    "coolify": "coolify_url",
    "dokploy": "dokploy_url",
}

async def service_health():
    result={}
    async with httpx.AsyncClient(timeout=3) as client:
        for cid, attr in URL_ATTRS.items():
            url=getattr(settings, attr, "")
            if not url:
                result[cid]={"status":"unconfigured"}
                continue
            try:
                r=await client.get(url)
                result[cid]={"status":"healthy" if r.status_code < 500 else "unhealthy","code":r.status_code}
            except Exception as e:
                result[cid]={"status":"unreachable","error":str(e)[:160]}
    return result
