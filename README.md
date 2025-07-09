# Ecommerce Order Recovery Agent

This project implements an AI-powered order recovery agent using Python and React.

## Backend
- FastAPI server exposing `/start` and `/status` endpoints
- LangGraph powered workflow that detects abandoned carts from Shopify, generates emails with OpenAI GPT-4o, and sends them via Gmail
- Uses `.env` values loaded with `python-dotenv`
- Can run in mock mode when the `MOCK` variable is enabled

Run the backend:
```bash
uvicorn backend.main:app --reload
```

## Frontend
A simple React + Vite + Tailwind dashboard to trigger the agent and show status.

Run the frontend:
```bash
cd frontend
npm install
npm run dev
```

## Setup
A `setup.sh` script installs backend and frontend dependencies for convenience.
