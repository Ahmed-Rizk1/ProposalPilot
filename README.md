# ProposalPilot

AI-powered sales proposal generator. Upload your product catalog and generate professional proposals in Arabic or English using Groq LLM.

## Features

- **Product Catalog** - CRUD operations for products with bilingual support (EN/AR)
- **Smart Matching** - Embedding-based product search using sentence-transformers
- **AI Proposal Generation** - Groq LLM (Llama 3.3 70B) generates tailored proposals
- **PDF Export** - Professional PDF proposals with ReportLab
- **Arabic/English** - Full support for both languages

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, Vite, Tailwind CSS, TypeScript |
| Backend | FastAPI, SQLAlchemy (async), Pydantic |
| Database | PostgreSQL + pgvector |
| LLM | Groq (Llama 3.3 70B) |
| Embeddings | sentence-transformers (local) |
| PDF | ReportLab |

## Project Structure

```
proposalpilot/
├── backend/           # FastAPI application
│   └── app/
│       ├── main.py
│       ├── config.py
│       ├── models/    # SQLAlchemy models
│       ├── routes/    # API endpoints
│       ├── controllers/ # Business logic
│       └── services/  # LLM, embeddings, PDF, DB
├── frontend/          # React application
│   └── src/
│       ├── pages/
│       ├── components/
│       └── api/
├── docker/            # Docker Compose
└── .env
```

## Quick Start

### 1. Prerequisites

- Docker + Docker Compose
- A [Groq API key](https://console.groq.com/keys)

### 2. Setup

```bash
cp .env.example .env
# Edit .env and add your GROQ_API_KEY
```

### 3. Run with Docker

```bash
cd docker
docker compose up -d
```

### 4. Access

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## Development

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/catalog/` | List all products |
| POST | `/api/v1/catalog/` | Create a product |
| PUT | `/api/v1/catalog/{id}` | Update a product |
| DELETE | `/api/v1/catalog/{id}` | Delete a product |
| GET | `/api/v1/catalog/search?q=` | Search products |
| POST | `/api/v1/proposals/generate` | Generate a proposal |
| GET | `/api/v1/proposals/` | List all proposals |
| GET | `/api/v1/proposals/{id}` | Get proposal details |
| GET | `/api/v1/proposals/{id}/download` | Download PDF |

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GROQ_API_KEY` | Groq API key | (required) |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+asyncpg://...` |
| `APP_ENV` | Environment | `development` |
