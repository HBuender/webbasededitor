# Use the official Python slim image as a base
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the FastAPI app into the container
COPY main.py /app/main.py

# Install FastAPI, Docker SDK for Python, and Pydantic without cache
RUN pip install --no-cache-dir fastapi uvicorn docker pydantic

# Expose the port for the FastAPI app
EXPOSE 8000

# Command to run the FastAPI app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
