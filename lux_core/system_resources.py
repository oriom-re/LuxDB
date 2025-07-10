# layer0/system_resources.py
"""
Odczyt i monitoring CPU, RAM, dysku, sieci
"""
import psutil
import os
from .decorators import lux_route

@lux_route("system/resources/monitor@v2", description="Monitoruj zasoby systemowe w czasie rzeczywistym")
def monitor_resources():
    return {
        "cpu": psutil.cpu_percent(),
        "ram": psutil.virtual_memory().percent,
        "disk": psutil.disk_usage('/').percent
    }

@lux_route("system/resources/detect@v2", description="Wykryj wszystkie dostępne zasoby sprzętowe")
def detect_hardware():
    """Wykrywanie wszystkich dostępnych zasobów sprzętowych"""
    disks = {}
    for part in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(part.mountpoint)
            disks[part.device] = {
                "mountpoint": part.mountpoint,
                "fstype": part.fstype,
                "total": usage.total,
                "used": usage.used,
                "free": usage.free,
                "percent": usage.percent
            }
        except Exception:
            continue
    
    return {
        "cpu_count": psutil.cpu_count(logical=True),
        "cpu_count_physical": psutil.cpu_count(logical=False),
        "cpu_freq": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None,
        "ram_total": psutil.virtual_memory().total,
        "ram_available": psutil.virtual_memory().available,
        "ram_percent": psutil.virtual_memory().percent,
        "swap_total": psutil.swap_memory().total,
        "swap_used": psutil.swap_memory().used,
        "disks": disks,
        "network_interfaces": list(psutil.net_if_addrs().keys()),
        "hostname": os.uname().nodename if hasattr(os, 'uname') else os.getenv('HOSTNAME', 'unknown'),
        "platform": os.name,
        "boot_time": psutil.boot_time()
    }

@lux_route("system/resources/analyze@v2", description="Analizuj pojemność systemu i daj rekomendacje")
def analyze_capacity():
    """Analiza pojemności systemu i rekomendacje"""
    hw = detect_hardware()
    recommendations = []
    
    if hw["ram_percent"] > 80:
        recommendations.append("HIGH_RAM_USAGE")
    if hw["cpu_count"] < 2:
        recommendations.append("LOW_CPU_COUNT")
    
    return {
        "hardware": hw,
        "recommendations": recommendations,
        "capacity_score": min(100, (hw["cpu_count"] * 10) + (hw["ram_total"] // (1024**3) * 5))
    }
