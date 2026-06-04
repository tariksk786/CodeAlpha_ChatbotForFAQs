# Use an official lightweight Python runtime as a parent image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=5000

# Set the working directory in the container
WORKDIR /app

# Install system dependencies needed for compiling some python packages if any
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file and install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download NLTK data to cache them in the Docker image layers
# This prevents downloading them during container startup
RUN python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('wordnet'); nltk.download('omw-1.4')"

# Copy the rest of the application code into the container
COPY . .

# Create database and uploads directory to ensure permissions are correct
RUN mkdir -p database static/uploads

# Expose port 5000 for the Flask application
EXPOSE 5000

# Start the application using Gunicorn
CMD gunicorn --bind 0.0.0.0:$PORT app:app
