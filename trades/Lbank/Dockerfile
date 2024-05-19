# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /usr/src/app
COPY requirements.txt /usr/src/app

RUN pip install --no-cache-dir -r requirements.txt
RUN playwright install
RUN playwright install-deps
# Copy the current directory contents into the container at /usr/src/app
COPY . /usr/src/app/
WORKDIR /usr/src/app/lbank/

# Install any needed packages specified in requirements.txt

# Command to run the Scrapy spider
CMD ["scrapy", "crawl", "lbankscraper"]