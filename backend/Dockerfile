FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    WHISPER_CACHE_DIR=/data/whisper-cache \
    HEALTHCHECK_PATH=/health

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --shell /bin/bash appuser

COPY requirements.txt ./
RUN pip install --no-cache-dir --index-url https://download.pytorch.org/whl/cpu torch
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/uploads /app/instance /data \
    && chmod +x /app/entrypoint.sh \
    && chown -R appuser:appuser /app /data

EXPOSE 5000

ENV DATABASE_URL=sqlite:////data/database.db \
    CORS_ORIGINS=http://localhost,http://frontend:4173,http://nginx

USER appuser

ENTRYPOINT ["./entrypoint.sh"]

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=5 CMD python -c "import os, sys, urllib.request; path = os.environ.get('HEALTHCHECK_PATH', '/health'); url = f'http://127.0.0.1:5000{path}'; sys.exit(0 if urllib.request.urlopen(url).status == 200 else 1)"

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--threads", "4", "--timeout", "120", "app:create_app()"]
