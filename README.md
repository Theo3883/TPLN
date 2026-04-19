# Platformă Evaluare Literatură Română

Platformă web pentru evaluarea continuă a edițiilor de literatură română: crawler, recenzii, ranking-uri transparente, moderare și export date.

## Ce este implementat

### Crawler (`crawler/`)
- Trei crawlere BeautifulSoup4 + httpx pentru surse reale românești: **bookzone.ro**, **carturesti.ro**, **libris.ro**
- Extragere metadata: titlu, autori, ISBN, editură, an apariție, copertă
- Normalizare ISBN (10/13 cifre) și an publicare în fiecare crawler
- `run_all.py` — rulează toate trei crawlerele și afișează statistici per sursă (total cărți, cărți cu ISBN)
- Output JSON în `crawler/output/` (bookzone.json, carturesti.json, libris.json)

### Backend API (`backend/`) — FastAPI + PostgreSQL + Meilisearch
- **Ediții**: `GET /editions`, `GET /editions/{id}` — catalog cu paginare
- **Recenzii**: `GET /editions/{id}/reviews`, `POST /reviews` — adăugare recenzie cu rate-limiting (SlowAPI)
- **Ranking**: `GET /rankings` — scoring Bayesian cu shrinkage; include câmpuri de confidence
- **Audit**: `GET /audit/editions/{id}` — trail complet al actualizărilor de scor prin score events
- **Export**: `GET /export?format=csv|json` — export catalog
- **Ingestie**: `POST /ingest` — ingestie din crawler cu deduplicare (ISBN + titlu normalizat), `POST /ingest/run-crawler` — trigger manual
- **Moderare**: `GET /moderation/pending`, `POST /moderation/{id}/approve`, `POST /moderation/{id}/reject`
- **Căutare**: `GET /search?q=...` — full-text search prin Meilisearch
- Migrare schemă DB cu Alembic (`versions/001_initial_schema.py`)
- Crawlerul pornește automat la startup-ul backend-ului

### UI (`ui/`) — Streamlit
- **Catalog**: listare ediții, click pentru detaliu + recenzii
- **Căutare**: full-text search cu afișare rezultate
- **Ranking**: tabel cu scoruri și confidence
- **Moderare**: aprobare/respingere recenzii în așteptare
- **Export**: descărcare date CSV sau JSON
- Buton lateral pentru declanșarea manuală a crawlerului

### Infrastructură
- `docker-compose.yml` — PostgreSQL + Meilisearch containerizate
- `start.sh` / `start.ps1` — startup complet cu un singur comandă

## Tehnologii

| Componentă | Tehnologie |
|---|---|
| Crawler | BeautifulSoup4 + httpx |
| Backend | FastAPI, SQLAlchemy (async), asyncpg, Alembic, Pydantic, SlowAPI |
| Baza de date | PostgreSQL |
| Căutare full-text | Meilisearch |
| UI | Streamlit |
| Orchestrare | Docker Compose |

## Pornire rapidă

```bash
# Linux/macOS
./start.sh

# Windows
.\start.ps1
```

### Pornire manuală

```bash
docker-compose up -d
cd backend
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --host 0.0.0.0 --port 8000
# într-un terminal separat:
cd ui
pip install -r requirements.txt
streamlit run app.py
```

### Rulare crawler independent

```bash
cd crawler
pip install -r requirements.txt
python run_all.py
```

## Endpoint-uri API principale

| Metodă | Cale | Descriere |
|---|---|---|
| GET | `/editions` | Catalog ediții (paginat) |
| GET | `/editions/{id}` | Detaliu ediție |
| GET | `/editions/{id}/reviews` | Recenzii pentru o ediție |
| POST | `/reviews` | Adaugă recenzie (rate-limited) |
| GET | `/rankings` | Ranking cu scoring Bayesian |
| GET | `/search?q=` | Căutare full-text |
| GET | `/audit/editions/{id}` | Audit trail scor |
| GET | `/export?format=csv\|json` | Export date |
| POST | `/ingest` | Ingestie date crawler |
| POST | `/ingest/run-crawler` | Pornire crawler |
| GET | `/moderation/pending` | Recenzii în așteptare |
| POST | `/moderation/{id}/approve` | Aprobare recenzie |
| POST | `/moderation/{id}/reject` | Respingere recenzie |

Documentație interactivă: http://localhost:8000/docs

## Structură proiect

```
TPLN/
├── backend/          # FastAPI + SQLAlchemy + Alembic
│   ├── app/
│   │   ├── api/      # endpoints: editions, reviews, rankings, search, audit, export, ingest, moderation
│   │   ├── core/     # config, database, security/rate-limiting
│   │   ├── models/   # SQLAlchemy: Author, Book, Edition, Review, Reviewer, ScoreEvent
│   │   ├── schemas/  # Pydantic schemas
│   │   └── services/ # scoring, search, anti-abuse, crawler_runner
│   └── alembic/      # migrări DB
├── crawler/          # BeautifulSoup4 crawlere
│   ├── crawl_bookzone.py
│   ├── crawl_carturesti.py
│   ├── crawl_libris.py
│   ├── run_all.py
│   └── output/       # bookzone.json, carturesti.json, libris.json
├── ui/               # Streamlit: catalog, căutare, ranking, moderare, export
├── nlp/              # modul NLP opțional (sentiment LaRoSeDa — în lucru)
└── docker-compose.yml
```
