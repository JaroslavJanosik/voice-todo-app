FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/uploads /app/instance /data

EXPOSE 5000

ENV FLASK_APP=app.py \
    DATABASE_URL=sqlite:////data/database.db \
    CORS_ORIGINS=http://localhost,http://frontend:4173,http://nginx

CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
