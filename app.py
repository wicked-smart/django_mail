import subprocess

celery_cmd = ["celery", "-A", "mail", "worker", "--loglevel=info"]
subprocess.run(celery_cmd, check=True, cwd="/app")