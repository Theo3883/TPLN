#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"

# Helper: retry a command up to N times with delay
retry() {
  local -r -i max_attempts="$1"; shift
  local -r cmd=("$@")
  local -i attempt=1
  local rc=0
  while :; do
    "${cmd[@]}" && rc=0 || rc=$?
    if [ $rc -eq 0 ]; then
      return 0
    fi
    attempt=$((attempt + 1))
    if [ $attempt -gt $max_attempts ]; then
      return $rc
    fi
    sleep 2
  done
}

# Track child PIDs so we can clean up
CHILD_PIDS=()
cleanup() {
  echo "Shutting down..."
  for pid in "${CHILD_PIDS[@]:-}"; do
    if kill -0 "$pid" 2>/dev/null; then
      kill "$pid" 2>/dev/null || true
    fi
  done
}
trap cleanup EXIT

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
# Run alembic with retries in case DB is still initializing
if [ -d backend ]; then
  # Run alembic from the backend directory so it finds the 'alembic' scripts folder
  if ! retry 10 bash -c "cd backend && DATABASE_URL=\"postgresql+asyncpg://tpln:tpln@127.0.0.1:5433/tpln\" alembic upgrade head"; then
    echo "Warning: alembic migrations failed after retries. Continuing but the backend may not work." >&2
  fi
else
  echo "Warning: backend directory not found, skipping migrations." >&2
fi

echo ">>> Starting backend (FastAPI)..."
BACKEND_PID=""
if [ -d backend ]; then
  (cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000) &
  BACKEND_PID=$!
  CHILD_PIDS+=("$BACKEND_PID")
else
  echo "Warning: backend directory not found, skipping backend start." >&2
fi

echo ">>> Waiting for backend to be ready..."
if [ -n "${BACKEND_PID:-}" ]; then
  echo ">>> Waiting for backend to be ready..."
  for i in {1..30}; do
    if curl -sSf http://localhost:8000/health > /dev/null 2>&1; then
      break
    fi
    sleep 2
  done
fi

UI_PID=""
if [ -d ui ]; then
  echo ">>> Starting Streamlit UI..."
  (cd ui && streamlit run app.py --server.port 8501 --server.address 0.0.0.0) &
  UI_PID=$!
  CHILD_PIDS+=("$UI_PID")
else
  echo "Skipping Streamlit UI: ui directory not found." >&2
fi

FRONTEND_PID=""
if [ -d romanian-lit-eva ]; then
  echo ">>> Installing frontend dependencies (romanian-lit-eva)..."
  (cd romanian-lit-eva && npm install --silent)

  echo ">>> Starting frontend (Vite dev server)..."
  # Ensure the frontend uses the local backend API
  (cd romanian-lit-eva && VITE_API_BASE="http://localhost:8000" npm run dev --silent) &
  FRONTEND_PID=$!
  CHILD_PIDS+=("$FRONTEND_PID")
else
  echo "Skipping frontend: romanian-lit-eva directory not found." >&2
fi

echo ""
echo "=== Ready ==="
echo "  Backend:  http://localhost:8000"
echo "  API Docs: http://localhost:8000/docs"
echo "  UI:       http://localhost:8501"
echo "  Frontend: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop all services."
# Wait for background PIDs if they were started
for pid in "${CHILD_PIDS[@]:-}"; do
  if [ -n "$pid" ]; then
    wait "$pid" || true
  fi
done
