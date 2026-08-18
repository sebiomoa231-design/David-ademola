from pathlib import Path
import yaml

CONFIG = Path("config/capabilities.yaml")

def load_capabilities():
    with CONFIG.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return data.get("capabilities", [])

def get_capability(capability_id):
    for item in load_capabilities():
        if item["id"] == capability_id:
            return item
    return None

def match_capabilities(text: str):
    text = text.lower()
    scored = []
    for item in load_capabilities():
        keywords = item.get("keywords", [])
        score = sum(1 for k in keywords if k.lower() in text)
        if score:
            scored.append((score, item))
    return [item for _, item in sorted(scored, key=lambda x: x[0], reverse=True)]
