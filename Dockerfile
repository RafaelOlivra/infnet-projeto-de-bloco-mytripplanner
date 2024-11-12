FROM python:3.11-slim

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create working directory
RUN mkdir /usr/src/app
WORKDIR /usr/src/app

# Copy requirements and install dependencies
COPY ./requirements-deploy.txt .
RUN python -m pip install --upgrade pip
RUN pip install --no-cache-dir pyarrow
RUN pip install --no-cache-dir -r requirements-deploy.txt

# Set environment variable
ENV PYTHONUNBUFFERED 1

# Copy the rest of the application code
COPY ./app ./app
COPY ./.env ./.env
COPY ./data ./data

# Set the command to run the application
CMD ["python", "-m", "streamlit", "run", "./app/0_🏠_Home.py"]
