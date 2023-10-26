web: gunicorn project3_cs50.wsgi 
worker: celery -A mail worker --loglevel=info
release: python3 manage.py makemigrations && \
         python3 manage.py migrate && \
         python3 manage.py collectstatic --no-input

