# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Define environment variable
ENV PYTHONUNBUFFERED=1

# Run the application (Default command, can be overridden)
# CMD ["python", "src/main.py"]
CMD ["/bin/bash"]