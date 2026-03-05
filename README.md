# Platformă Evaluare Literatură Română

Platformă web pentru evaluarea continuă a literaturii române: crawler, recenzii, ranking-uri transparente.

## Tehnologii

- **Crawler**: Scrapy
- **Backend**: FastAPI (Python)
- **DB**: PostgreSQL
- **Căutare**: Meilisearch
- **UI**: Streamlit (MVP)

## Pornire rapidă

**Pornire completă (Docker + pip install + backend + UI):**

```bash
./start.sh
```

Crawlerul rulează automat la pornirea backend-ului.

### Pornire manuală

1. `docker-compose up -d`
2. `cd backend && pip install -r requirements.txt && alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000`
3. `cd ui && pip install -r requirements.txt && streamlit run app.py`

## API

- Documentație interactivă: http://localhost:8000/docs
- `GET /editions` – catalog
- `GET /editions/{id}` – detaliu ediție
- `GET /editions/{id}/reviews` – recenzii
- `POST /reviews` – adaugă recenzie (rate-limited)
- `GET /rankings` – ranking
- `GET /audit/editions/{id}` – audit trail
- `GET /export?format=csv|json` – export date
- `POST /ingest` – ingestie crawler

## Structură

```
proiect-tpln/
├── backend/       # FastAPI
├── crawler/       # Scrapy
├── ui/            # Streamlit
└── docker-compose.yml
```
