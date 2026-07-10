"""
Configuration for the Composio App Research Agent.
Contains the full 100-app list across 10 categories and schema definitions.
"""
import json

# Load list dynamically from dataset to guarantee 100% alignment
with open("data/apps.json") as f:
    raw_apps = json.load(f)

APP_LIST = [{"name": a["name"], "url": a["url"], "category": a["category"]} for a in raw_apps]
CATEGORIES = sorted(set(app["category"] for app in APP_LIST))

# JSON schema for structured output
APP_SCHEMA = {
    "type": "object",
    "properties": {
        "id": {"type": "integer"},
        "name": {"type": "string"},
        "url": {"type": "string"},
        "category": {"type": "string"},
        "one_liner": {"type": "string", "description": "What the product does in one line"},
        "auth_methods": {"type": "array", "items": {"type": "string"}},
        "self_serve": {"type": "string", "enum": ["yes", "trial", "freemium", "no"]},
        "self_serve_detail": {"type": "string"},
        "api_type": {"type": "string"},
        "api_breadth": {"type": "string", "enum": ["narrow", "moderate", "broad", "very broad"]},
        "api_doc_url": {"type": "string"},
        "existing_mcp": {"type": "boolean"},
        "existing_composio": {"type": "boolean"},
        "buildability": {"type": "string", "enum": ["yes", "partial", "needs outreach", "no"]},
        "buildability_blocker": {"type": ["string", "null"]},
        "evidence_urls": {"type": "array", "items": {"type": "string"}},
        "confidence": {"type": "string", "enum": ["high", "medium", "low"]},
        "notes": {"type": "string"}
    },
    "required": ["id", "name", "url", "category", "one_liner", "auth_methods", "self_serve",
                  "api_type", "api_breadth", "buildability", "confidence"]
}
