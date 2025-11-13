# Intellect-Agent: Advanced Market Research Assistant

This is a web-based application that automates market research. It is built with a Python backend using Flask, Celery, and Redis, and a simple HTML/CSS/JavaScript frontend. The entire application is containerized with Docker for easy deployment.

## Prerequisites

To deploy and run this application, you will need a server with the following installed:
- **Docker:** [Installation Guide](https://docs.docker.com/engine/install/)
- **Docker Compose:** [Installation Guide](https://docs.docker.com/compose/install/) (Recommended for easier management)

## Deployment

There are two ways to deploy the application: using `docker-compose` (recommended) or using a manual `docker build` and `run` command.

### Recommended: Using Docker Compose

1.  **Create a `docker-compose.yml` file:**
    Create a file named `docker-compose.yml` in the root of the project with the following content:

    ```yml
    version: '3.8'
    services:
      redis:
        image: "redis:alpine"
        ports:
          - "6379:6379"

      web:
        build: .
        ports:
          - "5000:5000"
        depends_on:
          - redis

      worker:
        build: .
        command: celery -A app.celery_worker worker --loglevel=info
        depends_on:
          - redis
    ```

2.  **Build and run the application:**
    From the root of the project, run the following command:

    ```bash
    sudo docker-compose up --build -d
    ```
    This will build the Docker images, start the Redis server, the Gunicorn web server, and the Celery worker in the background.

### Manual Deployment

1.  **Build the Docker image:**
    From the root of the project, run the following command:

    ```bash
    sudo docker build -t intellect-agent .
    ```

2.  **Run the application:**
    You will need to start a Redis container, and then the application container.

    ```bash
    # Start Redis
    sudo docker run -d --name redis -p 6379:6379 redis:alpine

    # Start the application
    sudo docker run -d --name intellect-agent -p 5000:5000 --link redis:redis intellect-agent
    ```

## How to Use

1.  **Access the application:**
    Once deployed, the application will be accessible at `http://<your_server_ip>:5000`.

2.  **Start an analysis:**
    In the input field, type the topic you want to research (e.g., "the future of AI in education") and click "Start Analysis".

3.  **Monitor the progress:**
    A new card will appear in the feed, showing the live status of the analysis.

4.  **Authorize the plugin (if required):**
    If the agent determines that it needs the `Public_Opinion_Miner_Plugin`, a dialog will appear asking for your authorization. Click "Authorize" to allow the agent to proceed.

5.  **View the final report:**
    Once the analysis is complete, the final, structured five-part report will be displayed on the card.

## Customizing the Public Opinion Plugin

This application supports a file-based plugin for public opinion analysis. To use your own plugin:

1.  **Create a `plugin.py` file:**
    In the root of the project, create a file named `plugin.py`.

2.  **Implement the `run_opinion_miner` function:**
    The file must contain a function with the following signature:

    ```python
    def run_opinion_miner(plugin_input):
        # plugin_input is a dictionary with a "topic" key.
        # Your code to scrape and analyze public opinion goes here.
        # The function must return a dictionary with the following keys:
        # "high_frequency_topics", "core_pain_points", "unmet_needs"
        pass
    ```
    A `plugin.py` template is included in the project to serve as an example. If no `plugin.py` file is found, the agent will use its own internal simulation.
