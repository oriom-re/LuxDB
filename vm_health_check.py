
#!/usr/bin/env python3
"""
💊 LuxDB v2 VM Health Check

Niezależny skrypt sprawdzania zdrowia systemu na VM
"""

import requests
import json
import time
import sys
from datetime import datetime

def check_rest_api(host="0.0.0.0", port=5000, timeout=5):
    """Sprawdza API REST"""
    try:
        url = f"http://{host}:{port}/status"
        response = requests.get(url, timeout=timeout)
        
        if response.status_code == 200:
            data = response.json()
            return {
                'status': 'healthy',
                'response_time': response.elapsed.total_seconds(),
                'data': data
            }
        else:
            return {
                'status': 'unhealthy',
                'error': f"HTTP {response.status_code}"
            }
            
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e)
        }

def check_websocket(host="0.0.0.0", port=5001):
    """Sprawdza WebSocket (podstawowy test)"""
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result == 0:
            return {'status': 'healthy', 'message': 'Port dostępny'}
        else:
            return {'status': 'unhealthy', 'error': 'Port niedostępny'}
            
    except Exception as e:
        return {'status': 'error', 'error': str(e)}

def check_database():
    """Sprawdza bazę danych"""
    try:
        import sqlite3
        import os
        
        db_path = "db/vm_production.db"
        if not os.path.exists(db_path):
            return {'status': 'warning', 'message': 'Baza nie istnieje'}
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM astral_beings")
        count = cursor.fetchone()[0]
        conn.close()
        
        return {
            'status': 'healthy',
            'beings_count': count,
            'db_size': os.path.getsize(db_path)
        }
        
    except Exception as e:
        return {'status': 'error', 'error': str(e)}

def check_system_resources():
    """Sprawdza zasoby systemowe"""
    try:
        import psutil
        
        # CPU
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # RAM
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        
        # Dysk
        disk = psutil.disk_usage('/')
        disk_percent = disk.percent
        
        return {
            'status': 'healthy',
            'cpu_percent': cpu_percent,
            'memory_percent': memory_percent,
            'disk_percent': disk_percent,
            'memory_available_mb': memory.available // (1024*1024),
            'disk_free_mb': disk.free // (1024*1024)
        }
        
    except Exception as e:
        return {'status': 'error', 'error': str(e)}

def run_full_health_check():
    """Uruchamia pełny health check"""
    print(f"🔍 LuxDB v2 VM Health Check - {datetime.now().isoformat()}")
    print("=" * 60)
    
    checks = {
        'REST API': check_rest_api,
        'WebSocket': check_websocket, 
        'Database': check_database,
        'System Resources': check_system_resources
    }
    
    results = {}
    overall_healthy = True
    
    for check_name, check_func in checks.items():
        print(f"\n📋 {check_name}...")
        result = check_func()
        results[check_name] = result
        
        if result['status'] == 'healthy':
            print(f"   ✅ {check_name}: OK")
            if 'response_time' in result:
                print(f"      ⏱️ Czas odpowiedzi: {result['response_time']:.3f}s")
            if 'beings_count' in result:
                print(f"      📊 Bytów w bazie: {result['beings_count']}")
            if 'cpu_percent' in result:
                print(f"      💻 CPU: {result['cpu_percent']:.1f}%")
                print(f"      🧠 RAM: {result['memory_percent']:.1f}% ({result['memory_available_mb']}MB free)")
                print(f"      💾 Dysk: {result['disk_percent']:.1f}% ({result['disk_free_mb']}MB free)")
                
        elif result['status'] == 'warning':
            print(f"   ⚠️ {check_name}: {result.get('message', 'Warning')}")
            
        else:
            print(f"   ❌ {check_name}: {result.get('error', 'Unknown error')}")
            overall_healthy = False
    
    print(f"\n{'='*60}")
    if overall_healthy:
        print("✅ System VM: ZDROWY")
        return True
    else:
        print("❌ System VM: PROBLEMY WYKRYTE")
        return False

def continuous_monitoring(interval=60):
    """Ciągły monitoring (dla długoterminowych testów)"""
    print(f"🔄 Rozpoczynam ciągły monitoring (interwał: {interval}s)")
    print("Naciśnij Ctrl+C aby zatrzymać...")
    
    try:
        while True:
            success = run_full_health_check()
            
            if not success:
                print("⚠️ Wykryto problemy - sprawdź logi")
            
            print(f"\n😴 Oczekiwanie {interval}s...")
            time.sleep(interval)
            
    except KeyboardInterrupt:
        print("\n🛑 Monitoring zatrzymany")

def main():
    """Główna funkcja"""
    import argparse
    
    parser = argparse.ArgumentParser(description='LuxDB v2 VM Health Check')
    parser.add_argument('--monitor', '-m', action='store_true',
                       help='Ciągły monitoring')
    parser.add_argument('--interval', '-i', type=int, default=60,
                       help='Interwał monitoringu (sekundy)')
    
    args = parser.parse_args()
    
    if args.monitor:
        continuous_monitoring(args.interval)
    else:
        success = run_full_health_check()
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
