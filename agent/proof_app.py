#!/usr/bin/env python3
"""
Composio Integration Proof App
Demonstrates how the researched dataset (data/apps.json) directly translates into
runnable AI agent tools using the Composio SDK.
"""
import os
import sys
import json

# Define colors for console output
BLUE = "\033[94m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

def load_dataset(path="data/apps.json"):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: {path} not found. Please run the research scripts first.")
        sys.exit(1)

def print_banner():
    print(f"{BLUE}===============================================")
    print("      COMPOSIO TOOLKIT & PROOF GENERATOR       ")
    print(f"==============================================={RESET}")

def main():
    print_banner()
    apps = load_dataset()
    
    # Filter for Easy Wins: fully buildable, self-serve (yes/freemium), and broad/very broad API
    easy_wins = [
        a for a in apps 
        if a.get("buildability") == "yes" 
        and a.get("self_serve") in ("yes", "freemium") 
        and a.get("api_breadth") in ("broad", "very broad")
    ]
    
    print(f"\nFound {len(easy_wins)} 'Easy Win' apps in the research database.")
    print("These apps support self-serve access and are immediately buildable.")
    
    print("\nSelect an app to generate a Composio Tool Integration proof:")
    for idx, app in enumerate(easy_wins[:10], 1):
        print(f"  [{idx}] {app['name']} - {app['one_liner']}")
        
    try:
        choice = input(f"\nChoose an app [1-10] (default: 1): ").strip()
        choice_idx = int(choice) - 1 if choice else 0
        if choice_idx < 0 or choice_idx >= len(easy_wins):
            choice_idx = 0
    except ValueError:
        choice_idx = 0
        
    selected_app = easy_wins[choice_idx]
    print(f"\n{GREEN}Selected: {selected_app['name']}{RESET}")
    print(f"Category: {selected_app['category']}")
    print(f"Auth Method: {', '.join(selected_app['auth_methods'])}")
    print(f"API Type: {selected_app['api_type']}")
    print(f"Documentation: {selected_app['api_doc_url']}")
    
    print(f"\nGenerating Python integration code snippet for {selected_app['name']} using Composio:")
    
    # Map app names to standard Composio app keys
    composio_app_key = selected_app["name"].upper().replace(" ", "")
    
    code_snippet = f"""
# ========================================================
# Composio Integration Code for {selected_app['name']}
# Generated from research database (id: {selected_app['id']})
# ========================================================
import os
from openai import OpenAI
from composio import Composio, App

# 1. Initialize OpenAI and Composio clients
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", "your_openai_api_key"))
composio_client = Composio(api_key=os.getenv("COMPOSIO_API_KEY", "your_composio_api_key"))

# 2. Retrieve {selected_app['name']} tools from Composio
# Composio handles the {selected_app['auth_methods'][0] if selected_app['auth_methods'] else 'API Key'} authentication flow out of the box
try:
    # Get all tools for {selected_app['name']}
    tools = composio_client.get_tools(apps=[App.{composio_app_key}])
    print(f"Successfully loaded {{len(tools)}} actions for {selected_app['name']}!")
except Exception as e:
    # If the app isn't active on your Composio account yet, prompt the user to link it
    print(f"To use this toolkit, first run: 'composio add {selected_app['name'].lower().replace(' ', '-')}' in your terminal")
    tools = []

# Example execution flow:
# response = openai_client.chat.completions.create(
#     model="gpt-4o-mini",
#     messages=[{{"role": "user", "content": "Fetch the latest info using {selected_app['name']}"}}],
#     tools=tools,
#     tool_choice="auto"
# )
"""
    print(code_snippet)
    
    print(f"\n{YELLOW}Next Steps to run:{RESET}")
    print(f"1. Install Composio: `pip install composio` or `pip install composio-openai`")
    print(f"2. Add the tool to your local environment: `composio add {selected_app['name'].lower().replace(' ', '-')}`")
    print("3. Run your AI agent with full toolkit capabilities!")

if __name__ == "__main__":
    main()
