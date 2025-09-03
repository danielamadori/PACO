FROM python:3.12-slim

RUN apt-get update && \
    apt-get install -y iputils-ping && \
    apt-get install -y --no-install-recommends graphviz graphviz-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt ./requirements-server.txt
COPY gui/requirements.txt ./requirements-gui.txt

RUN pip install --no-cache-dir -r requirements-server.txt
RUN pip install --no-cache-dir -r requirements-gui.txt
RUN pip install jupyter

COPY src ./src
COPY gui/src ./gui/src/
COPY *.ipynb ./
COPY CPIs ./CPIs
COPY simulator/ .simulator/

EXPOSE 8000
EXPOSE 8001
EXPOSE 8050
EXPOSE 8888

CMD sh -c "jupyter notebook --notebook-dir=/app --ip=0.0.0.0 --port=8888 --no-browser --allow-root --IdentityProvider.token='' & exec python3 src --gui"
