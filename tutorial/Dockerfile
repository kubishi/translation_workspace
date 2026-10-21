# Build from the repo root: docker compose -f tutorial/docker-compose.yml build
FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

WORKDIR /app
COPY . .

RUN uv sync

EXPOSE 8888
CMD ["uv", "run", "jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root", "tutorial/tutorial.ipynb"]
