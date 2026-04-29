# Setup Guide for New Contributors

This guide walks you through everything needed to run the platform locally.

## Prerequisites

Make sure the following tools are installed before you begin:

| Tool | Minimum version | Notes |
|---|---|---|
| Python | 3.11+ | [python.org](https://www.python.org/downloads/) |
| Docker Desktop | latest | [docker.com](https://www.docker.com/products/docker-desktop/) — must be running |
| Git | any | to clone the repo |

---

## 1. Clone the repository

```bash
git clone <repo-url>
cd TPLN
```

---

## 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it:

- **Windows (PowerShell)**
  ```powershell
  Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
  .\.venv\Scripts\Activate.ps1
  ```
- **macOS / Linux**
  ```bash
  source .venv/bin/activate
  ```

---

## 3. Install dependencies

```bash
pip install -r backend/requirements.txt
pip install -r ui/requirements.txt
pip install -r crawler/requirements.txt
```

---

## 4. Start infrastructure (PostgreSQL + MeilisSearch)

```bash
docker compose up postgres meilisearch -d
```

Wait until both containers are healthy (usually 5–10 seconds):

```bash
docker compose ps
```

Both `tpln-postgres-1` and `tpln-meilisearch-1` should show **healthy**.

---

## 5. Run database migrations

```bash
cd backend
alembic upgrade head
cd ..
```

This creates all tables in the PostgreSQL database.

---

## 6. Start the backend

Open a **dedicated terminal** for the backend and run:

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --app-dir backend
```

Verify it is running: http://localhost:8000/health  
Interactive API docs: http://localhost:8000/docs

---

## 7. Start the frontend

Open another **dedicated terminal** for the UI and run:

```bash
python -m streamlit run ui/app.py --server.port 8501
```

The app will open automatically in your browser at http://localhost:8501

---

## Quick start (Windows only)

If you just want everything started at once, run the provided script from the repo root:

```powershell
.\start.ps1
```

This script handles all the steps above (Docker, migrations, backend, UI) automatically.

---

## Service overview

| Service | URL | Description |
|---|---|---|
| Streamlit UI | http://localhost:8501 | Web interface |
| FastAPI backend | http://localhost:8000 | REST API |
| API docs (Swagger) | http://localhost:8000/docs | Interactive API explorer |
| MeilisSearch | http://localhost:7700 | Full-text search engine |
| PostgreSQL | localhost:5432 | Database (user: `tpln`, password: `tpln_dev`, db: `tpln`) |

---

## Ingesting crawler data into the database

After the backend is running, populate the catalog from the existing crawler JSON files:

```powershell
python ingest_crawler_output.py
```

Optional flags:
```powershell
python ingest_crawler_output.py --api http://localhost:8000 --dir crawler/output
```

The script is safe to run multiple times — books already in the database are skipped as duplicates.

---

## Stopping everything

```bash
docker compose down
```

To also delete all stored data (database + search index):

```bash
docker compose down -v
```
