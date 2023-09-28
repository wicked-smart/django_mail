import subprocess

celery_cmd = ["celery", "-A", "mail", "worker", "--loglevel=info", "--uid=1000"]
subprocess.run(celery_cmd, check=True, cwd="/app")

