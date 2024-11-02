# Usa Python 3.12 come immagine base
FROM python:3.12-slim

# Installa git con apt e pulisce la cache al termine
RUN apt-get update && \
    apt-get install -y --no-install-recommends git graphviz graphviz-dev&& \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Imposta la directory di lavoro
WORKDIR /app

# Copia requirements.txt e installa le dipendenze Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia tutti i file del progetto
COPY . .

# Rendi eseguibile start.sh
RUN chmod +x start.sh

# Avvia lo script
CMD ["./start.sh"]
