#!/bin/bash
set -e
cd "$(dirname "$0")"

echo "=== Starting Platformă Evaluare Literatură Română ==="

echo ">>> Starting Docker (PostgreSQL + Meilisearch)..."
docker-compose up -d

echo ">>> Waiting for PostgreSQL..."
for i in {1..30}; do
  docker-compose exec -T postgres pg_isready -U tpln -d tpln 2>/dev/null && break
  sleep 2
done

echo ">>> Waiting for Meilisearch..."
for i in {1..30}; do
  curl -s http://localhost:7700/health 2>/dev/null | grep -q "available" && break
  sleep 2
done

echo ">>> Installing backend dependencies..."
pip3 install -r backend/requirements.txt -q

echo ">>> Installing crawler dependencies..."
pip3 install -r crawler/requirements.txt -q

echo ">>> Installing UI dependencies..."
pip3 install -r ui/requirements.txt -q

echo ">>> Running database migrations..."
cd backend && alembic upgrade head && cd ..

echo ">>> Starting backend (FastAPI)..."
cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

echo ">>> Waiting for backend to be ready..."
until curl -s http://localhost:8000/ 2>/dev/null | grep -q "Platformă"; do
  sleep 2
done

echo ">>> Starting Streamlit UI..."
cd ui && streamlit run app.py --server.port 8501 --server.address 0.0.0.0 &
UI_PID=$!

echo ""
echo "=== Ready ==="
echo "  Backend:  http://localhost:8000"
echo "  API Docs: http://localhost:8000/docs"
echo "  UI:       http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop all services."
wait $BACKEND_PID $UI_PID
