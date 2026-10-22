
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

WORKDIR /app

# Update pip and the certificate trust bundle for the security fix
RUN python -m pip install --no-cache-dir --upgrade \
    "pip>=26.2.2" \
    "certifi>=2026.10.19"

COPY requirements.txt .

RUN python -m pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY tests ./tests
COPY README.md .

EXPOSE 8000

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
