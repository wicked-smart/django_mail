FROM python:3.10

# Set the working directory
WORKDIR /app

# Copy your application code into the container
COPY . /app

# Install dependencies
RUN pip3 install -r requirements.txt

# Copy the entrypoint script into the container
COPY entrypoint.sh /entrypoint.sh

# Make the entrypoint script executable
RUN chmod +x /entrypoint.sh

# Set the entrypoint
ENTRYPOINT ["/entrypoint.sh"]