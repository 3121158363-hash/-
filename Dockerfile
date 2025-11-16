# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the requirements file into the container
COPY requirements.txt ./

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Create the logs directory
RUN mkdir -p app/logs

# Copy the rest of the application's code into the container
COPY . .

# Make port 8000 available
EXPOSE 8000

# The default command to run when starting the container
CMD ["gunicorn", "'app:create_app()'", "--bind", "0.0.0.0:8000"]
