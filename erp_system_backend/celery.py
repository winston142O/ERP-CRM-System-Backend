import os
import psutil
from celery import Celery

# Initial Celery configuration
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'erp_system_backend.settings')
app = Celery('erp_system_backend')
app.config_from_object('django.conf:settings', namespace='CELERY')

# Get the total memory in bytes
total_memory = psutil.virtual_memory().total

# Convert total memory to GB
total_memory_gb = total_memory / (1024 ** 3)

# Calculate 25% of total memory and convert to KB
app.conf.worker_max_memory_per_child = int(0.25 * total_memory_gb * 1024 * 1024)  # in KB

# Set the number of workers (concurrency)
app.conf.worker_concurrency = 6

app.autodiscover_tasks()
