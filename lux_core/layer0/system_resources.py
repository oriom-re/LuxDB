# layer0/system_resources.py
"""
Odczyt i monitoring CPU, RAM, dysku, sieci
"""
import psutil

def monitor_resources():
    return {
        "cpu": psutil.cpu_percent(),
        "ram": psutil.virtual_memory().percent,
        "disk": psutil.disk_usage('/').percent
    }
