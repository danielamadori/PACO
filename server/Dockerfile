FROM python:3.12-slim

RUN apt-get update && \
    apt-get install -y iputils-ping && \
    apt-get install -y --no-install-recommends graphviz graphviz-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

RUN pip install jupyter

COPY src /app

EXPOSE 8000
EXPOSE 8888
CMD ["sh", "-c", "jupyter notebook --ip=0.0.0.0 --port=8888 --no-browser --allow-root & python3 -u server.py"]
