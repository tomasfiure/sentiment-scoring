# Use an official Python runtime as a base image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Run the application
#CMD ["python", "main.py"]
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8080", "main:app"]

