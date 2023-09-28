# Use an official Python runtime as a parent image
FROM python:3.10

# Set the working directory in the container
WORKDIR /app

# Copy your Django project code into the container (assuming it's in the current directory)
COPY . /app/

# Install any dependencies required for your Django and Celery project
RUN pip install -r requirements.txt

# Create a new user
RUN useradd -m prem

# Set a password for the new user
RUN echo 'prem:PremR1s2B3w4N5p' | chpasswd

# Grant permissions to the new user
RUN chmod -R 700 /app/mail
RUN chown -R prem:prem /app/mail

ENV USER_ID $(id -u prem)

# Start your Django application and Celery worker
CMD ["python3", "app.py"]
