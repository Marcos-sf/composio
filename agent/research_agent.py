#!/usr/bin/env python3
"""
Composio App Research Agent
An AI-powered search and information extraction agent that researches SaaS applications
for API capabilities, authentication, and buildability.
"""
import os
import sys
import json
import argparse
import urllib.parse
import requests
from bs4 import BeautifulSoup

# Define colors for CLI logging
BLUE = "\033[94m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"

def log_info(msg):
    print(f"{BLUE}[INFO]{RESET} {msg}")

def log_success(msg):
    print(f"{GREEN}[SUCCESS]{RESET} {msg}")

def log_warn(msg):
    print(f"{YELLOW}[WARN]{RESET} {msg}")

def log_error(msg):
    print(f"{RED}[ERROR]{RESET} {msg}")

def web_search(query, max_results=3):
    """
    Search the web for information using keyless DuckDuckGo search.
    Falls back to Tavily if TAVILY_API_KEY is present in the environment.
    """
    tavily_key = os.getenv("TAVILY_API_KEY")
    if tavily_key:
        log_info(f"Using Tavily search API for: '{query}'")
        try:
            r = requests.post(
                "https://api.tavily.com/search",
                json={"api_key": tavily_key, "query": query, "max_results": max_results},
                timeout=10
            )
            if r.status_code == 200:
                results = r.json().get("results", [])
                return [{"title": res.get("title", ""), "link": res.get("url", ""), "snippet": res.get("content", "")} for res in results]
        except Exception as e:
            log_warn(f"Tavily search failed: {e}. Falling back to keyless search.")

    log_info(f"Using keyless DuckDuckGo search for: '{query}'")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }
    url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code != 200:
            log_warn(f"DuckDuckGo search returned HTTP {r.status_code}. Keyless search throttled.")
            return []
        
        soup = BeautifulSoup(r.text, "html.parser")
        results = []
        for a in soup.find_all("a", class_="result__snippet")[:max_results]:
            parent = a.parent.parent
            title_el = parent.find("a", class_="result__url")
            title = title_el.text.strip() if title_el else ""
            link = title_el["href"] if title_el and "href" in title_el.attrs else ""
            if link.startswith("//"):
                link = "https:" + link
            # Clean redirects
            if "uddg=" in link:
                parsed = urllib.parse.urlparse(link)
                qs = urllib.parse.parse_qs(parsed.query)
                if "uddg" in qs:
                    link = qs["uddg"][0]
            snippet = a.text.strip()
            results.append({"title": title, "link": link, "snippet": snippet})
        return results
    except Exception as e:
        log_warn(f"DuckDuckGo keyless search failed: {e}")
        return []

def call_llm(prompt, schema=None):
    """
    Call an LLM (Gemini or OpenAI) via HTTP requests directly to extract structured data.
    Falls back to mock/heuristic extraction if no API keys are present.
    """
    openai_key = os.getenv("OPENAI_API_KEY")
    gemini_key = os.getenv("GEMINI_API_KEY")

    system_instruction = "You are an expert developer research assistant. Extract SaaS API specifications and return clean JSON conforming exactly to the requested schema. Do not add markdown formatting, only output raw JSON."

    if openai_key:
        log_info("Calling OpenAI API...")
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {openai_key}"
        }
        data = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": prompt}
            ],
            "response_format": {"type": "json_object"} if schema else None,
            "temperature": 0.1
        }
        try:
            r = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data, timeout=20)
            if r.status_code == 200:
                res_content = r.json()["choices"][0]["message"]["content"]
                return json.loads(res_content)
            else:
                log_error(f"OpenAI API returned status code {r.status_code}: {r.text}")
        except Exception as e:
            log_error(f"OpenAI connection error: {e}")

    elif gemini_key:
        log_info("Calling Gemini API...")
        headers = {"Content-Type": "application/json"}
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_key}"
        data = {
            "contents": [{"parts": [{"text": f"{system_instruction}\n\n{prompt}"}]}],
            "generationConfig": {
                "responseMimeType": "application/json",
                "temperature": 0.1
            }
        }
        try:
            r = requests.post(url, headers=headers, json=data, timeout=20)
            if r.status_code == 200:
                res_content = r.json()["candidates"][0]["content"]["parts"][0]["text"]
                return json.loads(res_content)
            else:
                log_error(f"Gemini API returned status code {r.status_code}: {r.text}")
        except Exception as e:
            log_error(f"Gemini connection error: {e}")

    # Fallback / Mock runner for demonstration when no keys are configured
    log_warn("No API Keys configured (OPENAI_API_KEY or GEMINI_API_KEY). Running local heuristic mock model.")
    return None

def heuristic_research(app_name, category, url, search_results):
    """
    Perform local heuristic classification if LLM is unavailable.
    Outputs a realistic extraction matching the schema.
    """
    full_text = " ".join([r["snippet"] + " " + r["title"] for r in search_results]).lower()
    
    # Defaults
    auth_methods = ["API Key"]
    self_serve = "yes"
    self_serve_detail = "Self-serve developer access available"
    api_type = "REST"
    api_breadth = "moderate"
    buildability = "yes"
    buildability_blocker = None
    confidence = "medium"
    one_liner = f"Cloud-based software platform for {category.lower()} tasks"
    evidence_urls = [r["link"] for r in search_results if r["link"]]
    
    # Auth heuristics
    if "oauth2" in full_text or "oauth 2" in full_text:
        auth_methods = ["OAuth2"]
    elif "api token" in full_text or "access token" in full_text:
        auth_methods = ["API Token"]
    elif "basic auth" in full_text:
        auth_methods = ["Basic Auth"]
        
    # Gating heuristics
    if "contact sales" in full_text or "enterprise-only" in full_text or "request a demo" in full_text:
        self_serve = "no"
        self_serve_detail = "Requires contact sales / custom enterprise onboarding"
        buildability = "needs outreach"
        buildability_blocker = "No self-serve developer credentials available; contract required"
    elif "free trial" in full_text or "14-day trial" in full_text or "30-day trial" in full_text:
        self_serve = "trial"
        self_serve_detail = "Free developer trial sandbox available"
    elif "free plan" in full_text or "freemium" in full_text or "hobby tier" in full_text:
        self_serve = "freemium"
        self_serve_detail = "Free tier available with basic API limits"
        
    # API heuristics
    if "graphql" in full_text:
        api_type = "GraphQL"
    if "soap" in full_text:
        api_type = "REST, SOAP"
        
    # Breadth heuristics
    if "very broad" in full_text or "comprehensive api" in full_text:
        api_breadth = "very broad"
    elif "broad api" in full_text or "hundreds of endpoints" in full_text:
        api_breadth = "broad"
    elif "narrow" in full_text or "limited endpoints" in full_text:
        api_breadth = "narrow"

    # MCP / Composio checking
    existing_mcp = any(k in full_text for k in ["mcp server", "model context protocol"])
    existing_composio = any(k in app_name.lower() for k in ["slack", "github", "hubspot", "salesforce", "twilio", "stripe"])

    return {
        "name": app_name,
        "url": url,
        "category": category,
        "one_liner": one_liner,
        "auth_methods": auth_methods,
        "self_serve": self_serve,
        "self_serve_detail": self_serve_detail,
        "api_type": api_type,
        "api_breadth": api_breadth,
        "api_doc_url": evidence_urls[0] if evidence_urls else f"https://developers.{url}",
        "existing_mcp": existing_mcp,
        "existing_composio": existing_composio,
        "buildability": buildability,
        "buildability_blocker": buildability_blocker,
        "evidence_urls": evidence_urls,
        "confidence": confidence,
        "notes": "Extracted via keyless search agent heuristic mode."
    }

def research_app(app_name, category, url, app_id=999):
    """
    Research a single app by querying developer docs and extracting its specifications.
    """
    log_info(f"Researching: {app_name} (Category: {category})")
    
    # 1. Execute targeted web searches
    queries = [
        f"{app_name} API developer documentation authentication",
        f"{app_name} API self-serve free sandbox signup pricing"
    ]
    
    search_results = []
    for q in queries:
        search_results.extend(web_search(q, max_results=2))
        
    log_info(f"Retrieved {len(search_results)} search results.")
    
    # 2. Formulate LLM prompt
    search_context = "\n".join([f"- Title: {r['title']}\n  URL: {r['link']}\n  Snippet: {r['snippet']}" for r in search_results])
    
    prompt = f"""
    You are researching the SaaS product "{app_name}" (website: {url}) in the category "{category}" to build an integration toolkit for AI agents.
    
    Using the search snippets below, analyze and extract key details:
    {search_context}
    
    Return a JSON object conforming exactly to this schema:
    {{
      "name": "{app_name}",
      "url": "{url}",
      "category": "{category}",
      "one_liner": "Single-line summary of product function",
      "auth_methods": ["OAuth2" or "API Key" or "API Token" or "Basic Auth" or "Bearer Token" etc.],
      "self_serve": "yes" | "trial" | "freemium" | "no",
      "self_serve_detail": "Detail about how a developer gets API access",
      "api_type": "REST" | "GraphQL" | "gRPC" | "REST, GraphQL" etc.,
      "api_breadth": "narrow" | "moderate" | "broad" | "very broad",
      "api_doc_url": "URL to the primary developer docs",
      "existing_mcp": true | false (whether there is a Model Context Protocol server for this app already),
      "existing_composio": true | false (whether this is already supported on Composio),
      "buildability": "yes" | "partial" | "needs outreach" | "no",
      "buildability_blocker": null or "The reason why it cannot be built as a self-serve agent tool today",
      "evidence_urls": ["List of relevant documentation URLs found"],
      "confidence": "high" | "medium" | "low",
      "notes": "Any other critical findings"
    }}
    """
    
    # 3. Call LLM or use heuristic extraction fallback
    data = call_llm(prompt)
    if not data:
        data = heuristic_research(app_name, category, url, search_results)
        
    data["id"] = app_id
    return data

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Composio SaaS App Research Agent")
    parser.add_argument("--app", type=str, help="Research a single app by name")
    parser.add_argument("--category", type=str, default="General", help="Category for single app")
    parser.add_argument("--url", type=str, default="", help="Website URL for single app")
    parser.add_argument("--limit", type=int, default=1, help="Max number of apps to research from registry")
    
    args = parser.parse_args()
    
    if args.app:
        # Research single custom app
        res = research_app(args.app, args.category, args.url or f"{args.app.lower().replace(' ', '')}.com", app_id=1)
        log_success(f"Research Completed!\n{json.dumps(res, indent=2)}")
    else:
        # Load from registry and research limited set
        try:
            with open("data/apps.json") as f:
                registry = json.load(f)
            log_info(f"Loaded registry of {len(registry)} apps. Running batch of {args.limit} apps...")
            
            results = []
            for item in registry[:args.limit]:
                res = research_app(item["name"], item["category"], item["url"], item["id"])
                results.append(res)
                log_success(f"Completed {item['name']}")
                
            print(f"\nBatch Completed. Results preview:")
            print(json.dumps(results, indent=2))
        except Exception as e:
            log_error(f"Failed to read apps.json: {e}")
