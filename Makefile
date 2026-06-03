.PHONY: install dev test lint up down fe-dev

install:        ## Install backend (editable) + frontend deps
	cd backend && pip install -e ".[dev]"
	cd frontend && npm install

dev:            ## Run the backend API with reload
	cd backend && uvicorn app.main:app --reload --port 8000

fe-dev:         ## Run the Next.js frontend
	cd frontend && npm run dev

test:           ## Run backend tests
	cd backend && pytest -q

lint:           ## Lint backend
	cd backend && ruff check app tests

up:             ## Start backend + db via docker compose
	docker compose up --build

down:
	docker compose down
