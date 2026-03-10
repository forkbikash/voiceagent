.PHONY: install setup run-api run-agent run-all lint format docker-up docker-down \
       test-health test-token test-api open-playground

# ─── Setup ───────────────────────────────────────────────────────────

setup:
	python3 -m venv .venv
	.venv/bin/pip install -r requirements.txt
	@echo ""
	@echo "Done! Activate with: source .venv/bin/activate"

install:
	python3 -m pip install -r requirements.txt

# ─── Run Services ────────────────────────────────────────────────────

run-api:
	python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

run-agent:
	python3 agent_worker.py dev

run-all:
	@echo "Starting API server and agent worker..."
	@make run-api & make run-agent

# ─── Testing ─────────────────────────────────────────────────────────
#
# Quick test workflow:
#   1. make run-api          (Terminal 1)
#   2. make run-agent        (Terminal 2)
#   3. make test-api         (Terminal 3 — verifies both endpoints)
#   4. make open-playground  (opens browser for voice testing)
#
# In the playground:
#   - Click "Manual" tab
#   - Paste the LiveKit URL and token from test-token output
#   - Click "Connect"
#   - Speak into your mic — the agent will respond via voice
#   - Check Terminal 2 logs for "llm_race_winner" to see which model won

test-health:
	@echo "--- Health Check ---"
	@curl -s http://localhost:8000/api/voice/health | python3 -m json.tool

test-token:
	@echo "--- Token Generation ---"
	@curl -s -X POST http://localhost:8000/api/voice/token \
		-H "Content-Type: application/json" \
		-d '{"room_name":"test-room","participant_name":"user1"}' | python3 -m json.tool

test-api: test-health test-token
	@echo ""
	@echo "--- Validation: missing fields ---"
	@curl -s -X POST http://localhost:8000/api/voice/token \
		-H "Content-Type: application/json" \
		-d '{}' | python3 -m json.tool
	@echo ""
	@echo "All API tests passed."

open-playground:
	@open "https://agents-playground.livekit.io"

# ─── Code Quality ────────────────────────────────────────────────────

lint:
	ruff check .

format:
	ruff format .

# ─── Docker ──────────────────────────────────────────────────────────

docker-up:
	docker compose up -d --build

docker-down:
	docker compose down
