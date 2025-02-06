# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set environment variables to ensure output is logged immediately
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file and install the Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the rest of the application code to the container
COPY . .

# Specify the command to run your script
CMD ["python", "nancy.py"]