# Container da API de suporte Avendre (FastAPI + Supabase remoto)
FROM python:3.12-slim

WORKDIR /app

COPY requisitos.txt .
RUN pip install --no-cache-dir -r requisitos.txt

COPY api/ ./api/

EXPOSE 8000

CMD ["ddtrace-run", "uvicorn", "api.principal:app", "--host", "0.0.0.0", "--port", "8000"]
