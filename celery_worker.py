import os
import sys
# Add current directory to path for Windows child processes
sys.path.insert(0, os.getcwd())

from webapp import create_app

app = create_app()
celery_app = app.extensions["celery"]

# CRITICAL: Explicitly ensure result backend is configured
celery_app.conf.update(
    result_backend=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    task_ignore_result=False,
    result_serializer='json',
    task_serializer='json',
    accept_content=['json'],
)

# Debug: Print configuration
print("=" * 60)
print("CELERY WORKER STARTING WITH CONFIG:")
print(f"  Result Backend: {celery_app.conf.result_backend}")
print(f"  Task Ignore Result: {celery_app.conf.task_ignore_result}")
print(f"  Result Serializer: {celery_app.conf.result_serializer}")
print("=" * 60)
