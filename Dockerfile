# Use a lightweight Python base image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy and install dependencies first to leverage Docker caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- ADD THIS LINE ---
# Install the trusted root certificates for SSL connections
RUN apt-get update && apt-get install -y ca-certificates

# Copy your backend and frontend code into the container
COPY ./app /app/app
COPY ./frontend /app/frontend

# Expose the port the app will run on
EXPOSE 8000

# The command to start the Uvicorn server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]