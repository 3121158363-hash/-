# Intellect-Agent: Advanced Market Research Assistant

This application is a web-based interface for the Intellect-Agent, a tool for conducting market research.

## Running the Application with Docker

This application is designed to be run as a Docker container.

### Prerequisites

- Docker must be installed on your system.

### Build the Docker Image

Navigate to the project's root directory (where the `Dockerfile` is located) and run the following command to build the Docker image:

```bash
docker build -t intellect-agent .
```

### Run the Docker Container

Once the image is built, you can run the application with the following command:

```bash
docker run -p 5000:5000 intellect-agent
```

This will start the application and make it accessible at `http://localhost:5000` in your web browser.
