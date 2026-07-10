"""
Research Agent - Core orchestrator for Composio app analysis.
Researches 100 apps across 10 categories using web search + LLM extraction.
"""
import json
import os
import sys
from config import APP_LIST, CATEGORIES


def load_dataset(path="data/apps.json"):
    """Load the current dataset."""
    with open(path, "r") as f:
        return json.load(f)


def compute_stats(apps):
    """Compute aggregate statistics from the dataset."""
    stats = {
        "total": len(apps),
        "categories": {},
        "auth_distribution": {},
        "self_serve_breakdown": {"yes": 0, "trial": 0, "freemium": 0, "no": 0},
        "buildability": {"yes": 0, "partial": 0, "needs outreach": 0, "no": 0},
        "api_types": {},
        "api_breadth": {"narrow": 0, "moderate": 0, "broad": 0, "very broad": 0},
        "confidence": {"high": 0, "medium": 0, "low": 0},
        "has_mcp": 0,
        "on_composio": 0,
        "easy_wins": [],
        "outreach_needed": [],
    }

    for app in apps:
        cat = app["category"]
        if cat not in stats["categories"]:
            stats["categories"][cat] = {"count": 0, "buildable": 0, "self_serve": 0}
        stats["categories"][cat]["count"] += 1

        # Auth methods
        for auth in app.get("auth_methods", []):
            stats["auth_distribution"][auth] = stats["auth_distribution"].get(auth, 0) + 1

        # Self-serve
        ss = app.get("self_serve", "no")
        stats["self_serve_breakdown"][ss] = stats["self_serve_breakdown"].get(ss, 0) + 1
        if ss in ("yes", "freemium"):
            stats["categories"][cat]["self_serve"] += 1

        # Buildability
        b = app.get("buildability", "no")
        stats["buildability"][b] = stats["buildability"].get(b, 0) + 1
        if b == "yes":
            stats["categories"][cat]["buildable"] += 1

        # API type
        api = app.get("api_type", "Unknown")
        stats["api_types"][api] = stats["api_types"].get(api, 0) + 1

        # API breadth
        breadth = app.get("api_breadth", "moderate")
        stats["api_breadth"][breadth] = stats["api_breadth"].get(breadth, 0) + 1

        # Confidence
        conf = app.get("confidence", "medium")
        stats["confidence"][conf] = stats["confidence"].get(conf, 0) + 1

        # MCP & Composio
        if app.get("existing_mcp"):
            stats["has_mcp"] += 1
        if app.get("existing_composio"):
            stats["on_composio"] += 1

        # Easy wins: self-serve + buildable + broad+ API
        if b == "yes" and ss in ("yes", "freemium") and breadth in ("broad", "very broad"):
            stats["easy_wins"].append(app["name"])

        # Outreach needed
        if b in ("needs outreach",) or ss == "no":
            stats["outreach_needed"].append(app["name"])

    return stats


def generate_analysis(apps, stats):
    """Generate pattern analysis insights."""
    insights = []

    # 1. Auth patterns
    total = stats["total"]
    oauth_count = stats["auth_distribution"].get("OAuth2", 0) + stats["auth_distribution"].get("OAuth", 0)
    apikey_count = stats["auth_distribution"].get("API Key", 0) + stats["auth_distribution"].get("API Token", 0) + stats["auth_distribution"].get("Bearer Token", 0) + stats["auth_distribution"].get("Personal Access Token", 0)
    insights.append(f"OAuth 2.0 is the dominant auth method, used by {oauth_count} of {total} apps. API Key variants are close behind at {apikey_count}.")

    # 2. Self-serve
    ss = stats["self_serve_breakdown"]
    accessible = ss["yes"] + ss["freemium"]
    insights.append(f"{accessible} of {total} apps ({accessible*100//total}%) offer self-serve API access (free or freemium), making them immediately buildable without sales contact.")

    # 3. Buildability
    b = stats["buildability"]
    insights.append(f"{b['yes']} apps are fully buildable, {b['partial']} are partially buildable, and {b['needs outreach']} require sales outreach.")

    # 4. Easy wins
    insights.append(f"Top easy wins for Composio integration: {', '.join(stats['easy_wins'][:15])}...")

    # 5. Category patterns
    for cat in sorted(stats["categories"].keys()):
        c = stats["categories"][cat]
        insights.append(f"{cat}: {c['buildable']}/{c['count']} fully buildable, {c['self_serve']}/{c['count']} self-serve accessible.")

    return insights


if __name__ == "__main__":
    apps = load_dataset()
    stats = compute_stats(apps)
    insights = generate_analysis(apps, stats)

    # Save stats
    with open("data/stats.json", "w") as f:
        json.dump(stats, f, indent=2)

    # Print insights
    print("\n=== COMPOSIO APP RESEARCH: KEY INSIGHTS ===\n")
    for i, insight in enumerate(insights, 1):
        print(f"  {i}. {insight}")

    print(f"\n  Total apps: {stats['total']}")
    print(f"  Already on Composio: {stats['on_composio']}")
    print(f"  Have MCP servers: {stats['has_mcp']}")
    print(f"  Easy wins: {len(stats['easy_wins'])}")
    print(f"  Outreach needed: {len(stats['outreach_needed'])}")
