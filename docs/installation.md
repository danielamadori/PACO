---
title: Installation
layout: default
---

## Prerequisites

To run the application, you can use either **Python** or **Docker**. Only one of these is required.

- **Python 3.12+**
- **Docker**

To install **Python**, follow the instructions on [Python's official website](https://www.python.org/downloads/). For **Docker**, you can find installation steps on [Docker's official website](https://docs.docker.com/get-docker/).

---

## Quick Start

### Using Python

To start the application using Python, follow these steps:

1. Ensure all dependencies are installed:
    ```bash
    pip install -r requirements.txt
    ```
2. Run the application:
    ```bash
    cd src
    python3 app.py
    ```
3. Open a browser and go to `http://127.0.0.1:8050` to view the app.

### Using Docker

To start the application using Docker, follow these steps:

1. Pull and start the Docker:
    ```bash
    docker pull danielamadori/paco:latest
    docker run -d -p 8050:8050 -it --name PACO danielamadori/paco:latest
    docker logs PACO
    ```
   Note: Replace latest with a specific version number if needed.
2. Open a browser and navigate to `http://127.0.0.1:8050` to access the application.

---