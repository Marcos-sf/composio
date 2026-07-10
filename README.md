# Composio App Research Dashboard

> AI-powered analysis of **100 SaaS applications** across **10 categories** — evaluating auth methods, API surface, self-serve access, and agent buildability for Composio integration.

## 🔗 Live Dashboard
[**View the deployed dashboard →**](https://composio-research.vercel.app)

## 📊 Key Findings

| Metric | Value |
|--------|-------|
| Apps Researched | 100 |
| Fully Buildable | 86 |
| Easy Wins (self-serve + broad API) | 47 |
| Already on Composio | 59 |
| Have MCP Servers | 21 |
| Require Sales Outreach | 15 |

### Top Patterns
1. **OAuth 2.0 standard dominates** — used by 57% of apps, highlighting Composio's centralized OAuth handler advantage.
2. **63% self-serve access** — 63 apps offer free/freemium API access for immediate builder usage.
3. **Support & Enterprise APIs are gated** — Support and Helpdesk has the lowest self-serve rate (only 2/10), requiring sales outreach.
4. **Developer Tools & Productivity = 100% buildable** — easiest expansion categories with 10/10 buildable API surfaces.
5. **REST APIs rule** — 91% of apps utilize REST APIs, simplifying schema serialization.

## 🏗️ Project Structure

```
├── agent/
│   ├── config.py       # 100-app list, categories, JSON schema
│   ├── main.py         # Core research agent + analysis engine
│   └── verifier.py     # Verification pipeline (with human-in-the-loop audit logs)
├── data/
│   ├── apps.json       # Full 100-app dataset
│   ├── stats.json      # Aggregate statistics
│   └── verification_report.json
├── dashboard/
│   └── index.html      # Self-contained HTML dashboard (single file)
├── build_dashboard.py  # Generates dashboard from dataset
└── README.md
```

## 🤖 How the Agent Works

1. **App List** → 100 apps across 10 categories (CRM, Support, Messaging, Marketing, E-Commerce, Scraping, Developer platforms, Productivity, Fintech, AI & Media)
2. **Web Research** → Automated search for developer docs, auth methods, API type, pricing
3. **LLM Extraction** → Structured JSON extraction of key fields per app using GPT-4o-mini/Gemini
4. **Human-in-the-Loop Gate** → High/Medium confidence filtering and manual sandbox auditing
5. **Verification Audit** → Stratified sample cross-referencing to output transparent correction logs
6. **Dashboard Build** → Single-file HTML compilation with embedded data, charts, and interactive table

## 🚀 Running Locally

```bash
# Generate the dashboard from data
python3 build_dashboard.py

# Open in browser
open dashboard/index.html

# Run analysis
python3 agent/main.py

# Run verification
python3 agent/verifier.py
```

## 📂 Categories Covered
| Category | Apps | Buildable | Self-Serve |
|----------|------|-----------|------------|
| CRM and Sales | 10 | 9 | 5 |
| Support and Helpdesk | 10 | 8 | 2 |
| Communications and Messaging | 10 | 10 | 9 |
| Marketing, Ads, Email and Social | 10 | 10 | 9 |
| Ecommerce | 10 | 7 | 5 |
| Data, SEO and Scraping | 10 | 8 | 7 |
| Developer, Infra and Data platforms | 10 | 10 | 8 |
| Productivity and Project Management | 10 | 10 | 7 |
| Finance and Fintech | 10 | 7 | 7 |
| AI, Research and Media-native | 10 | 7 | 4 |

## ✅ Verification

- **Schema validation**: 100% pass (all required fields present)
- **20-app stratified sample**: 2 per category, cross-referenced
- **First-Pass Agent Accuracy**: 91.0%
- **Post-Verification Accuracy**: 98.0%
- **Confidence**: 80% high, 20% medium, 0% low

---

Built for the **Composio AI Product Ops Intern** take-home assignment.
