# Platformă Evaluare Literatură Română

Platformă web pentru evaluarea continuă a edițiilor de literatură română: crawler, recenzii, ranking-uri transparente, moderare, export date și analiză NLP sentiment.

## Ce este implementat

### Crawler (`crawler/`)
- Trei crawlere BeautifulSoup4 + httpx pentru surse reale românești: **bookzone.ro**, **carturesti.ro**, **libris.ro**
- Extragere metadata: titlu, autori, ISBN, editură, an apariție, copertă
- Normalizare ISBN (10/13 cifre) și an publicare în fiecare crawler
- `run_all.py` — rulează toate trei crawlerele și afișează statistici per sursă (total cărți, cărți cu ISBN)
- `scheduler.py` — rulează crawlerele automat la fiecare oră; poate fi pornit local sau ca serviciu Docker
- Output JSON în `crawler/output/` (bookzone.json, carturesti.json, libris.json)

### Backend API (`backend/`) — FastAPI + PostgreSQL + Meilisearch
- **Ediții**: `GET /editions`, `GET /editions/{id}` — catalog cu paginare
- **Recenzii**: `GET /editions/{id}/reviews`, `POST /reviews` — adăugare recenzie cu rate-limiting (SlowAPI); validare strictă Pydantic (rating 1.0–5.0 în pași de 0.5, conținut minim 20 caractere)
- **Ranking**: `GET /rankings` — scoring Bayesian cu shrinkage; include câmpuri de confidence
- **Audit**: `GET /audit/editions/{id}` — trail complet al actualizărilor de scor prin score events
- **Export**: `GET /export?format=csv|json` — export catalog
- **Ingestie**: `POST /ingest` — ingestie din crawler cu deduplicare (ISBN + titlu normalizat), `POST /ingest/run-crawler` — trigger manual (rate-limited 5/oră)
- **Moderare**: `GET /moderation/pending`, `POST /moderation/{id}/approve`, `POST /moderation/{id}/reject` — rate-limited 60/oră
- **Căutare**: `GET /search?q=...` — full-text search prin Meilisearch
- **NLP Sentiment**: `POST /sentiment/analyze` — analiză sentiment text românesc bazată pe LaRoSeDa; `GET /sentiment/reviews/{id}` — sentiment per recenzie; `GET /sentiment/editions/{id}` — rezumat agregat sentiment pentru o ediție
- **Error handling**: răspunsuri de eroare consistente în format JSON pentru 400, 404, 409, 422, 503, 500
- Migrare schemă DB cu Alembic (`versions/001_initial_schema.py`)
- Crawlerul pornește automat la startup-ul backend-ului

### UI (`ui/`) — Streamlit
- **Catalog**: listare ediții, click pentru detaliu + recenzii
- **Căutare**: full-text search cu afișare rezultate
- **Ranking**: tabel cu scoruri și confidence
- **Moderare**: aprobare/respingere recenzii în așteptare
- **Export**: descărcare date CSV sau JSON
- Buton lateral pentru declanșarea manuală a crawlerului

### NLP (`nlp/`)
- Modul de analiză sentiment pentru recenzii românești bazat pe lexiconul LaRoSeDa (Tache et al., EACL 2021)
- Detectare termeni pozitivi/negativi cu suport pentru negații și intensificatori
- Returnează label (pozitiv/negativ/neutru), scor în [-1, 1] și nivel de încredere

### Infrastructură
- `docker-compose.yml` — PostgreSQL + Meilisearch + serviciu crawler containerizate; crawlerul rulează automat la fiecare oră
- `start.sh` / `start.ps1` — startup complet cu un singur comandă

## Tehnologii

| Componentă | Tehnologie |
|---|---|
| Crawler | BeautifulSoup4 + httpx |
| Backend | FastAPI, SQLAlchemy (async), asyncpg, Alembic, Pydantic, SlowAPI |
| Baza de date | PostgreSQL |
| Căutare full-text | Meilisearch |
| NLP | Lexicon LaRoSeDa (Tache et al., EACL 2021) |
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
# O singură rulare:
python run_all.py
# Scheduler orar (rulare continuă):
python scheduler.py
```

### Crawler ca serviciu Docker (scheduler orar)

Serviciu `crawler` inclus în `docker-compose.yml` — pornit automat alături de celelalte servicii:

```bash
docker-compose up -d
# sau doar crawlerul:
docker-compose up -d crawler
```

Output-ul JSON este montat în `crawler/output/` pe host. Intervalul implicit este 1 oră.

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
| POST | `/ingest/run-crawler` | Pornire crawler (rate-limited) |
| GET | `/moderation/pending` | Recenzii în așteptare |
| POST | `/moderation/{id}/approve` | Aprobare recenzie (rate-limited) |
| POST | `/moderation/{id}/reject` | Respingere recenzie (rate-limited) |
| POST | `/sentiment/analyze` | Analiză sentiment text românesc |
| GET | `/sentiment/reviews/{id}` | Sentiment pentru o recenzie |
| GET | `/sentiment/editions/{id}` | Rezumat sentiment pentru o ediție |
| GET | `/health` | Health check aplicație |

Documentație interactivă: http://localhost:8000/docs

## Structură proiect

```
TPLN/
├── backend/          # FastAPI + SQLAlchemy + Alembic
│   ├── app/
│   │   ├── api/      # endpoints: editions, reviews, rankings, search, audit, export, ingest, moderation, sentiment
│   │   ├── core/     # config, database, security/rate-limiting, error-handlers
│   │   ├── models/   # SQLAlchemy: Author, Book, Edition, Review, Reviewer, ScoreEvent
│   │   ├── schemas/  # Pydantic schemas cu validatori
│   │   └── services/ # scoring, search, anti-abuse, crawler_runner
│   └── alembic/      # migrări DB
├── crawler/          # BeautifulSoup4 crawlere
│   ├── crawl_bookzone.py
│   ├── crawl_carturesti.py
│   ├── crawl_libris.py
│   ├── run_all.py
│   └── output/       # bookzone.json, carturesti.json, libris.json
├── ui/               # Streamlit: catalog, căutare, ranking, moderare, export
├── nlp/
│   └── sentiment/    # analiză sentiment română (LaRoSeDa lexicon, Tache et al. EACL 2021)
│       └── analyzer.py
└── docker-compose.yml
```

## Referințe

- LaRoSeDa dataset: https://huggingface.co/datasets/universityofbucharest/laroseda
- Tache et al. (2021). LaRoSeDa: A Large Romanian Sentiment Data Set. EACL 2021: https://aclanthology.org/2021.eacl-main.81.pdf
- FastAPI Documentation: https://fastapi.tiangolo.com/
- Streamlit Documentation: https://docs.streamlit.io/