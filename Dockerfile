# Use an official Python runtime as a parent image
FROM python:3.6-slim

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Create the volume to persist the test results
VOLUME /app/data/

# Install any needed packages
RUN pip install pipenv
RUN pipenv install

# Run app.py when the container launches
CMD ["pipenv", "run", "python", "run.py"]
