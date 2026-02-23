# ── Stage 1: Build the React frontend ───────────────────────────────────────
FROM node:20-alpine AS frontend-builder
WORKDIR /app/web/frontend
COPY web/frontend/package*.json ./
RUN npm ci --silent
COPY web/frontend/ ./
RUN npm run build

# ── Stage 2: Python runtime ──────────────────────────────────────────────────
FROM python:3.11-slim
WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

# Python deps
COPY requirements-web.txt ./
RUN pip install --no-cache-dir -r requirements-web.txt

# Copy source
COPY . .

# Copy built frontend
COPY --from=frontend-builder /app/web/frontend/dist /app/web/frontend/dist

EXPOSE 8000
ENV PYTHONPATH=/app

CMD ["python", "-m", "uvicorn", "web.backend.app:app", "--host", "0.0.0.0", "--port", "8000"]
