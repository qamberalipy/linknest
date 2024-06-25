# Use the official Python image from the Docker Hub
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file to the working directory
COPY requirements.txt .

# Install the dependencies specified in the requirements file
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code to the working directory
COPY . .

# Specify the port number the container should expose
EXPOSE 8000

# Command to run the FastAPI application using uvicorn, ensuring the .env file is sourced
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
