# 🚀 ProposalPilot

> **AI-Powered Enterprise Sales Proposal Generator with Multi-Format Document RAG**

ProposalPilot transforms how teams create winning sales proposals. By uploading company knowledge documents (PDFs, DOCX, TXT), ProposalPilot leverages **Retrieval-Augmented Generation (RAG)** and **Groq (Llama 3.3 70B)** to generate tailored, highly relevant enterprise sales proposals with live AI interactive chat editing and professional PDF export.

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Vercel-000000?style=for-the-badge&logo=vercel&logoColor=white)](https://proposal-pilot-eight.vercel.app/)
[![Frontend](https://img.shields.io/badge/Frontend-React%20%7C%20TypeScript%20%7C%20Vite-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://proposal-pilot-eight.vercel.app/)
[![Backend](https://img.shields.io/badge/Backend-FastAPI%20%7C%20Python-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://proposal-pilot-eight.vercel.app/)
[![Database](https://img.shields.io/badge/Database-Supabase%20PostgreSQL-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white)](https://supabase.com)
[![AI Engine](https://img.shields.io/badge/AI Engine-Groq%20Llama%203.3-F05032?style=for-the-badge&logo=groq&logoColor=white)](https://groq.com)

---

## 🔗 Live Application

- **Live Web Application:** [https://proposal-pilot-eight.vercel.app/](https://proposal-pilot-eight.vercel.app/)

---

## ✨ Key Features

- 📄 **Multi-Format Document RAG**: Upload PDFs, Word documents (`.docx`), and text files (`.txt`). Automatically chunks and embeds documents for context-aware retrieval.
- ⚡ **AI Sales Proposal Generation**: Powered by Groq's Llama 3.3 70B model for ultra-fast generation of enterprise sales proposals tailored to client demands and company context.
- 💬 **Live AI Proposal Chatbot**: Interactively edit, refine, expand, or rewrite generated proposals using a live AI assistant.
- 📥 **Export to PDF & DOCX**: Download generated proposals as clean, professionally styled PDF documents or editable text files.
- 🏢 **Organization Branding**: Configure company profiles, default proposal guidelines, and branding context applied across all proposals.
- 🔒 **Secure Auth**: JWT token-based authentication and secure session management.
- 📊 **Metrics & Observability**: Real-time performance tracking and system metrics monitoring endpoints.

---

## 🛠️ Tech Stack

| Layer | Technology | Description |
|-------|-----------|-------------|
| **Frontend** | React 18, TypeScript, Vite, Tailwind CSS | High-performance SPA deployed on **Vercel** |
| **Backend** | FastAPI, Python 3.11+, Pydantic | Asynchronous RESTful API deployed on **Render** |
| **Database** | Supabase PostgreSQL (`pgvector`) | Relational database with vector similarity search |
| **LLM Engine** | Groq (Llama 3.3 70B Versatile) | Ultra-fast LLM inference for proposal generation & chat |
| **PDF Engine** | ReportLab / PyPDF | Server-side PDF compilation & document extraction |
| **Hosting** | Vercel (Frontend), Render (Backend) | Distributed cloud deployment |

---

## 📂 Repository Structure

```text
proposalpilot/
├── backend/                  # FastAPI Application
│   ├── app/
│   ├── routes/               # API Endpoints (Auth, Docs, Proposals, Org, Observability)
│   ├── services/             # LLM (Groq), RAG pipeline, PDF compilation
│   ├── auth.py               # Authentication & JWT security
│   ├── config.py             # App environment & Settings configuration
│   ├── database.py           # Database connection & session management
│   ├── models.py             # SQLAlchemy ORM models
│   ├── main.py               # FastAPI entrypoint & router mounts
│   └── requirements.txt      # Python dependencies
│
├── frontend/                 # Vite + React SPA
│   ├── src/
│   │   ├── api.ts            # Centralized API client & HTTP interceptor
│   │   ├── App.tsx           # React Router & main layout
│   │   ├── components/       # UI Components & Layouts
│   │   ├── lib/              # Environment config (`lib/env.ts`)
│   │   └── pages/            # App pages (Dashboard, Documents, Proposals, Generate, Edit, Settings)
│   ├── vercel.json           # Vercel SPA routing configuration
│   └── vite.config.ts        # Vite dev server & build settings
└── README.md
```

---

## 🌐 Environment Variables

### Backend Configuration (`backend/.env`)

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `GROQ_API_KEY` | **Yes** | Groq Cloud API Key | `gsk_...` |
| `DATABASE_URL` | **Yes** | PostgreSQL Connection String | `postgresql+asyncpg://user:pass@host:5432/dbname` |
| `APP_ENV` | No | App Environment (`development` / `production`) | `production` |
| `SECRET_KEY` | No | JWT Signing Key | `your-secret-key-here` |

### Frontend Configuration (Vercel Environment Variables)

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `VITE_API_BASE_URL` | **Yes** | Public URL of deployed backend | `https://your-backend.onrender.com` |

---

## 🚀 Deployment Guide

### 1. Database (Supabase PostgreSQL)
1. Create a project on [Supabase](https://supabase.com/).
2. Copy the Connection String URI (`postgresql+asyncpg://...`).

### 2. Backend (Render)
1. Deploy the `backend/` directory as a **Web Service** on [Render](https://render.com/).
2. Set Build Command: `pip install -r requirements.txt`
3. Set Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Add Environment Variables (`GROQ_API_KEY`, `DATABASE_URL`, `APP_ENV=production`).

### 3. Frontend (Vercel)
1. Connect repository to [Vercel](https://vercel.com/) and select the `frontend/` directory as Root.
2. Framework Preset: **Vite**
3. Add Environment Variable:
   - `VITE_API_BASE_URL` = `https://<your-render-backend-name>.onrender.com`
4. Deploy!

---

## 💻 Local Development

### Prerequisites
- Python 3.11+
- Node.js 18+
- [Groq API Key](https://console.groq.com/keys)

### Backend Setup

```bash
cd backend
python -m venv .venv
# On Windows: .venv\Scripts\activate | On macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```
- API Documentation available at: `http://localhost:8000/docs`

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```
- Web Application available at: `http://localhost:5173`

---

## 🔌 Core API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/auth/register` | Register new user account |
| `POST` | `/api/auth/login` | Login & receive JWT access token |
| `GET` | `/api/documents/` | List uploaded RAG knowledge documents |
| `POST` | `/api/documents/upload` | Upload & parse document (PDF/DOCX/TXT) |
| `POST` | `/api/proposals/generate` | Generate RAG sales proposal using Groq LLM |
| `GET` | `/api/proposals/` | List generated proposals |
| `POST` | `/api/proposals/{id}/chat` | Send message to AI chatbot to edit proposal |
| `GET` | `/api/proposals/{id}/download` | Download compiled proposal PDF |
| `GET` | `/api/observability/metrics` | View system & request performance metrics |

---

## 📄 License

Distributed under the MIT License.
