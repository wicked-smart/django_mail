import subprocess
import os

user_id = os.environ.get("USER_ID")

# Convert user_id to an integer
try:
    user_id = int(user_id)
except (ValueError, TypeError):
    user_id = None  # Handle the case where user_id is not a valid integer

if user_id is not None:
    celery_cmd = ["celery", "-A", "mail", "worker", "--loglevel=info", f"--uid={user_id}"]
    subprocess.run(celery_cmd, check=True, cwd="/app")
else:
    print("Invalid or missing USER_ID environment variable.")
