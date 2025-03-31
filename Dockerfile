# Use official Python 3.9 image as base
FROM python:3.9-slim

# Update system and install required packages
RUN apt-get update && apt-get install -y \
    wget \
    ffmpeg \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgl1-mesa-glx \
    xvfb \
    gnupg \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Install Google Chrome
# RUN apt-get update && apt-get install -y chromium-browser  \
#     && rm -rf /var/lib/apt/lists/*
# Uncomment the following lines if you want to install Google Chrome from the official repository
RUN apt-get update && \
    apt-get install -y wget gnupg && \
    wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && \
    apt-get install -y google-chrome-stable  

# Set display environment variable (for virtual display)
ENV DISPLAY=:99

# Create and set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create directory for recordings
RUN mkdir -p /tmp/meeting_records

# Command to run the application
CMD ["python", "./main.py"]