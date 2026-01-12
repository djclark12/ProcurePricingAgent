# Procure-Price-Agent

A local-first demo showcasing two AI agents for procurement and pricing workflows.

![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.35+-red.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## Overview

This application demonstrates AI-powered agents for:

1. **Procurement Agent** – RFQ creation, quote comparison, award recommendation, negotiation email drafts
2. **Pricing Agent** – Sell-price recommendations based on cost, margins, competitor anchors, and demand signals

### Key Features

- 🔍 **Smart Item Search** – Natural language search across your catalog
- 📋 **Automated RFQ Generation** – Create request-for-quotes based on your needs
- 📊 **Vendor Comparison** – Side-by-side quote analysis with recommendations
- 💰 **Dynamic Pricing** – Margin-aware pricing with competitor analysis
- 📈 **Analytics Dashboard** – Spending trends, vendor performance, savings opportunities
- ✉️ **Negotiation Drafts** – AI-generated emails for vendor negotiations

## Prerequisites

- **Python 3.11+**
- **Azure OpenAI Resource** with a deployed chat model 
- Access to the deployment's endpoint, API key, and deployment name

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/djclark12/procure-price-agent.git
```

### 2. Create a Virtual Environment (Recommended)

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Copy the example environment file and fill in your Azure OpenAI credentials:

```bash
# Windows
copy .env.example .env

# macOS/Linux
cp .env.example .env
```

Open `.env` in your text editor and configure the following values:

```dotenv
# Your Azure OpenAI resource endpoint (include trailing slash)
AZURE_OPENAI_ENDPOINT=https://<your-resource>.openai.azure.com/

# Your Azure OpenAI API key (from Azure Portal)
AZURE_OPENAI_API_KEY=<your-api-key>

# API version (use latest stable or preview)
OPENAI_API_VERSION=2024-08-01-preview

# Your deployment name (NOT the model name!)
AZURE_OPENAI_DEPLOYMENT=<your-deployment-name>
```

> ⚠️ **Security Note**: Never commit your `.env` file to version control. It's already included in `.gitignore`.

> 💡 **Finding Your Credentials**:
> - **Endpoint & API Key**: Azure Portal → Your OpenAI Resource → "Keys and Endpoint"
> - **Deployment Name**: Azure AI Foundry → Deployments → Your deployment's name (e.g., `my-gpt4o`)

### 5. Seed the Database

```bash
python -m data.seed
```

This creates `data/procurement.db` with sample items, vendors, price lists, and competitor anchors.

### 6. Run the App

```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## Usage Guide

### Using the Chat Interface

The application provides a conversational interface where you can:

1. **Type natural language requests** in the chat input
2. **Use pre-built scenarios** from the sidebar dropdown
3. **Toggle visibility options** to see tool calls and agent reasoning

### Example Prompts

#### Procurement Workflows
```
"I need to procure 1000kg of EPDM rubber compound"
"Source 50 hydraulic seal kits with fast delivery"
"Get quotes for 500 safety gloves, prioritize lowest cost"
```

#### Pricing Recommendations
```
"What sell price should I set for EPDM rubber compound with 30% margin?"
"Recommend a sell price for carbon black"
"Price NBR rubber for a customer quote"
```

#### Analytics & Insights
```
"Show me our spending summary"
"Which vendors have the best performance?"
"Where can we find savings opportunities?"
"What are the price trends for raw materials?"
```

#### Catalog Queries
```
"What items do we have in the catalog?"
"What is the most expensive item we buy?"
"How many items do we have?"
```

---

## Demo Script

### Scenario 1: Buy Ergonomic Chairs

1. In the sidebar, select **Scenario 1** ("Buy 200 ergonomic chairs…").
2. Click **Load Scenario** – the prompt appears in the chat input.
3. Press Enter or click Send.
4. Watch the agent:
   - Search for matching items
   - Create an RFQ
   - Fetch and compare vendor quotes
   - Recommend an award decision
   - Draft a negotiation email

**Expected output**: A vendor comparison table, award recommendation with bullet reasoning, and a professional email asking the top vendor for better terms.

### Scenario 2: Source Laptops with Negotiation Email

1. Select **Scenario 2** and load it.
2. The agent handles a balanced cost/lead-time strategy and includes a negotiation email.

### Scenario 3: Set Sell Price

1. Select **Scenario 3** ("Set sell price for SKU MON-27-4K…").
2. The Pricing Agent retrieves cost basis, competitor anchors, and demand notes.
3. It recommends a sell price with a bullet-point rationale.

### Toggle Options

- **Show tool calls**: Displays each tool invocation (name, arguments, result summary).
- **Show intermediate notes**: Displays the agent's internal reasoning.

---

## Project Structure

```
procure-price-agent/
├── README.md
├── .env.example
├── requirements.txt
├── app.py                  # Streamlit UI
├── agent/
│   ├── __init__.py
│   ├── llm_client.py       # Azure OpenAI client wrapper
│   ├── prompts.py          # System/developer prompts
│   ├── schemas.py          # Pydantic models
│   ├── tools.py            # Pure Python tool functions
│   └── orchestrator.py     # Intent routing & tool-calling loop
├── data/
│   ├── seed.py             # DB seeding script
│   └── fixtures.sql        # SQL statements for sample data
└── tests/
    └── test_tools.py       # Unit tests for tools
```

---

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| `openai.AuthenticationError` | Invalid API key | Check `AZURE_OPENAI_API_KEY` in `.env` |
| `openai.NotFoundError: deployment not found` | Wrong deployment name | Use the **deployment name** from Azure, not the model name |
| `Connection refused` | Endpoint URL wrong | Ensure `AZURE_OPENAI_ENDPOINT` ends with `/` and is correct |
| Empty responses | API version mismatch | Try `2024-08-01-preview` or latest stable version |
| `ModuleNotFoundError` | Missing install | Re-run `pip install -r requirements.txt` |

### Deployment Name vs. Model Name

Azure OpenAI requires a **deployment name** (e.g., `my-gpt4o-deployment`), not the base model name (e.g., `gpt-4o`). When you deploy a model in Azure AI Foundry, you choose a deployment name—use that value for `AZURE_OPENAI_DEPLOYMENT`.

---

## Running Tests

```bash
pytest tests/ -v
```

Tests cover pricing logic and quote comparison without network calls.

---

## License

MIT – Demo purposes only.

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup

After cloning, install dev dependencies and run tests:

```bash
pip install -r requirements.txt
pytest tests/ -v
```

---

## Support

If you encounter issues:

1. Check the [Troubleshooting](#troubleshooting) section above
2. Ensure your Azure OpenAI deployment is active and has quota
3. Verify environment variables are correctly set
4. Open an issue with error details and steps to reproduce
