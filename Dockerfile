# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install Graphviz
RUN apt-get update && apt-get install -y graphviz

# Make port 8080 available to the world outside this container
EXPOSE 8080

# Define environment variable
ENV NAME FEKDI-BI

# Run the application
CMD ["gunicorn", "test:app", "--bind", "0.0.0.0:8080"]
