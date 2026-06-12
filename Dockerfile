FROM node:20-alpine AS frontend
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install
COPY frontend/ ./
RUN npm run build

FROM python:3.11-slim
WORKDIR /app/backend
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ .
ENV FRONTEND_DIST=/app/frontend/dist
ENV SERVE_STATIC=true
ENV CORS_ALLOW_ALL=true
ENV PORT=8080
COPY --from=frontend /app/frontend/dist /app/frontend/dist
EXPOSE 8080
CMD uvicorn app.main:app --host 0.0.0.0 --port 8080
