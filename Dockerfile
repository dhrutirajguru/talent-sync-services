FROM python:3.11-slim

# Install uv (fast package manager — see Section 3.2 recommendation)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /code

COPY pyproject.toml ./
RUN uv sync --no-dev

COPY ./app ./app
COPY alembic.ini ./
COPY ./alembic ./alembic

ENV PATH="/code/.venv/bin:$PATH"

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
