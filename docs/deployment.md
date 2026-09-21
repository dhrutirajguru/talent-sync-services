## Local 
- cp .env.example .env          # generate a real JWT_SECRET_KEY if you want: openssl rand -hex 32
- uv sync
- docker compose up -d postgres # just the DB for now
- uv run alembic upgrade head
- uv run uvicorn app.main:app --reload