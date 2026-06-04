# Personal Finance Multi-Agent Analyzer

An AI-powered personal finance tool that uses the Claude API to run your expenses through a **three-agent pipeline** and return a spending analysis, personalized recommendations, and a monthly budget plan.

---

## Features

- Three AI agents in sequence: **Expense Analyzer → Financial Advisor → Budget Planner**
- Three input methods: manual entry, CSV upload, or free-text paste
- Two interfaces: **Streamlit web app** and a **FastAPI REST API** with a standalone HTML client
- Downloadable JSON reports
- All processing is done in memory — no expense data is stored

---

## Architecture

```
User Input
    │
    ▼
┌─────────────────────┐
│   Expense Analyzer  │  → Categorizes transactions, calculates totals, flags anomalies
└─────────────────────┘
    │
    ▼
┌─────────────────────┐
│  Financial Advisor  │  → Generates 5-7 actionable money-saving recommendations
└─────────────────────┘
    │
    ▼
┌─────────────────────┐
│   Budget Planner    │  → Creates a monthly budget with savings targets
└─────────────────────┘
    │
    ▼
  Report (analysis + recommendations + budget plan)
```

Each agent makes a separate Claude API call, so results build on each other.

---

## Project Structure

```
personal-finance-agent/
├── agents/
│   ├── __init__.py
│   ├── crew.py              # Main pipeline using the Anthropic SDK
│   ├── simple_crew.py       # Alternative pipeline using direct HTTP requests
│   ├── expense_analyzer.py  # Expense Analyzer agent definition (CrewAI)
│   ├── recommender.py       # Financial Advisor agent definition (CrewAI)
│   └── budget_agent.py      # Budget Planner agent definition (CrewAI)
├── app.py                          # Streamlit web interface
├── api_server.py                   # FastAPI REST server
├── personal_finance_agent.html     # Standalone HTML client (dark/light mode)
├── personal_finance_agent_fixed.html  # Updated HTML client
├── sample_expenses.csv             # Sample data for testing
├── requirements.txt
├── .env.example
└── .gitignore
```

---

## Quick Start

### Prerequisites

- Python 3.9+
- An [Anthropic API key](https://console.anthropic.com/)

### 1. Clone and install

```bash
git clone https://github.com/yjumatov/personal-finance-agent.git
cd personal-finance-agent

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
```

Open `.env` and set your API key:

```
ANTHROPIC_API_KEY=sk-ant-...
```

### 3. Run

**Option A — Streamlit app (full UI)**

```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501)

**Option B — FastAPI server + HTML client**

```bash
uvicorn api_server:app --reload
```

API runs at [http://localhost:8000](http://localhost:8000).  
Then open `personal_finance_agent.html` in your browser.

---

## Input Formats

### Manual entry
Add expenses one at a time through the sidebar form (date, amount, category, description).

### CSV upload

```csv
date,description,amount,category
2024-01-01,Grocery Store,65.50,Food
2024-01-02,Gas Station,45.00,Transport
2024-01-03,Netflix,15.99,Entertainment
```

A working example is included at `sample_expenses.csv`.

### Text paste

```
2024-01-15 Grocery Shopping 50.25
2024-01-16 Gas 45.00
2024-01-17 Coffee 8.50
```

---

## API Reference

### `GET /health`

Health check.

```json
{ "status": "ok" }
```

### `POST /run`

Analyze expense data and return the full report.

**Request body:**

```json
{
  "financial_data": {
    "expenses": [
      { "date": "2024-01-01", "description": "Grocery Store", "amount": 65.50, "category": "Food" },
      { "date": "2024-01-02", "description": "Gas Station",   "amount": 45.00, "category": "Transport" }
    ]
  }
}
```

**Success response:**

```json
{
  "status": "success",
  "analysis": "Expense breakdown by category...",
  "recommendations": "1. Reduce dining out by...",
  "budget": "Recommended monthly budget...",
  "agents_used": ["Expense Analyzer", "Financial Advisor", "Budget Planner"]
}
```

**Error response:**

```json
{
  "status": "error",
  "error": "Error message"
}
```

**Quick curl test:**

```bash
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{
    "financial_data": {
      "expenses": [
        {"date": "2024-01-01", "description": "Groceries", "amount": 65.50},
        {"date": "2024-01-02", "description": "Gas", "amount": 45.00}
      ]
    }
  }'
```

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| AI Model | Claude (Anthropic) |
| Agent Framework | CrewAI |
| Web UI | Streamlit |
| REST API | FastAPI + Uvicorn |
| Data handling | Pandas |
| Environment | python-dotenv |

---

## Configuration

| Variable | Required | Description |
|----------|----------|-------------|
| `ANTHROPIC_API_KEY` | Yes | API key from [console.anthropic.com](https://console.anthropic.com/) |

The default model in `agents/crew.py` and `agents/simple_crew.py` is `claude-opus-4-1`. You can change it to any current Anthropic model (e.g., `claude-sonnet-4-6`).

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for how to report issues, suggest features, or submit pull requests.

---

## License

MIT — see [LICENSE](LICENSE) for details.
