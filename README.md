# Intellect-Agent: AI-Powered Market Research Assistant

This web application is a professional-grade, AI-powered tool that automates in-depth market research. It is built with a robust Python backend (Flask, Celery, Redis) and is designed for easy deployment with Docker.

## Prerequisites

To deploy and run this application, you will need a server with the following installed:
- **Docker:** [Installation Guide](https://docs.docker.com/engine/install/)
- **Docker Compose:** [Installation Guide](https://docs.docker.com/compose/install/)

## 1. API Key Configuration

Before you can run the application, you must configure your API keys.

1.  **Locate the configuration file:**
    The API keys are managed in the `app/config.py` file.

2.  **Add your keys:**
    Open the file and replace the placeholder strings (`"YOUR_..._KEY_HERE"`) with your actual API keys for each of the following services:
    - **Apify:** For web scraping and social media analysis.
    - **Baidu AI Cloud:** For Natural Language Processing.
    - **Tushare:** For financial data (primary source).
    - **Financial Modeling Prep (FMP):** For financial data (fallback source).
    - **NewsAPI.org:** For news and policy analysis.

## 2. Deployment

This application is designed to be deployed with Docker Compose, which orchestrates the web server, background worker, and Redis services.

**Build and run the application:**
From the root of the project, run the following command:

```bash
sudo docker-compose up --build -d
```
This command will build the Docker image and start all the necessary services in the background.

## 3. How to Use the API

Once the application is running, you can interact with it via its REST API.

**A. Start an Analysis**

-   **Endpoint:** `/start_analysis`
-   **Method:** `POST`
-   **Body:** A JSON object with a `topic` key and an optional `deep_dive` boolean (defaults to `false`).

**Example `curl` command (Standard Analysis):**
```bash
curl -X POST -H "Content-Type: application/json" -d '{"topic": "the future of quantum computing"}' http://<your_server_ip>:8000/start_analysis
```

**Example `curl` command (Deep Dive Analysis):**
```bash
curl -X POST -H "Content-Type: application/json" -d '{"topic": "the future of quantum computing", "deep_dive": true}' http://<your_server_ip>:8000/start_analysis
```

**B. Check Task Status**

-   **Endpoint:** `/status/<task_id>`
-   **Method:** `GET`

Use the `task_id` from the previous step to check the progress and retrieve the final report.

**Example `curl` command:**
```bash
curl http://<your_server_ip>:8000/status/a1b2c3d4-e5f6-7890-1234-567890abcdef
```

The application's frontend is a simple, intuitive interface that uses this API. You can access it at `http://<your_server_ip>:8000`.
