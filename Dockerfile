# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Install Redis
RUN apt-get update && apt-get install -y redis-server

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the requirements file into the container
COPY requirements.txt ./

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application's code into the container
COPY . .

# Make port 5000 available
EXPOSE 5000

# Create a startup script
COPY <<'EOF' /usr/src/app/start.sh
#!/bin/sh
# Start Redis
redis-server --daemonize yes
# Start Celery worker in the background
celery -A app.celery_worker worker --loglevel=info &
# Start Gunicorn
gunicorn --bind 0.0.0.0:5000 "app.server:app"
EOF

# Make the script executable
RUN chmod +x /usr/src/app/start.sh

# Run the startup script
CMD ["/usr/src/app/start.sh"]
