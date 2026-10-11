# Stage 1: Frontend Build
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Stage 2: Python Backend Runtime
FROM python:3.12-slim
WORKDIR /app

# Install system dependencies (build essentials if needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend codebase and assets
COPY backend/ /app/backend/
COPY dashboard/ /app/dashboard/
COPY --from=frontend-builder /app/frontend/dist /app/frontend/dist

# Environment and Network
ENV PYTHONPATH=/app/backend
ENV HOST=0.0.0.0
ENV PORT=8000

EXPOSE 8000

# Health check
HEALTHCHECK --interval=10s --timeout=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/shield/info || exit 1

# Launch Gateway
CMD ["python", "-m", "gateway.main"]
