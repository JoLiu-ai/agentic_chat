# Agentic Chat Product

A robust agentic chat application featuring autonomous agents capable of planning, tool use, and multi-step reasoning.

## Architecture

- **Backend**: FastAPI
- **Frontend**: Streamlit
- **Orchestration**: LangGraph
- **Database**: SQLite + ChromaDB

## Setup

1.  Clone the repository.
2.  Create a virtual environment: `python -m venv venv`
3.  Activate the environment: `source venv/bin/activate`
4.  Install dependencies: `pip install -r requirements.txt`
5.  Copy `.env.example` to `.env` and fill in your API keys.

## Running

### Backend
```bash
uvicorn app.main:app --reload
```

### Frontend
```bash
streamlit run ui/app.py
```
