# Use official Python runtime parent image
FROM python:3.11-bullseye

# Set environment variables
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYCODE 1
ENV PORT=8000
EXPOSE 8000

# Set work directory
WORKDIR /code

# Install dependencies
COPY requirements.txt /code/
RUN apt-get update -y &&\
    pip install --upgrade pip &&\
    pip install -r requirements.txt

# Copy project \
COPY . /code/
