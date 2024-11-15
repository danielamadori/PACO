FROM python:3.12-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends graphviz graphviz-dev redis-server && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY src /app

CMD ["sh", "-c", "redis-server --daemonize yes && python3 -u app.py"]