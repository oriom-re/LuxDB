
# 🚀 LuxDB v2 - Wdrożenie na VM

## 📋 Wymagania Systemowe

### Minimalne:
- **OS**: Linux (Ubuntu 20.04+, CentOS 8+, Debian 11+)
- **Python**: 3.8+
- **RAM**: 512MB
- **Dysk**: 100MB wolnego miejsca
- **CPU**: 1 vCPU

### Zalecane:
- **RAM**: 1GB+
- **Dysk**: 1GB+
- **CPU**: 2+ vCPU

## 🔧 Instrukcja Wdrożenia

### 1. Przygotowanie środowiska
```bash
# Sklonuj projekt
git clone <repo-url>
cd luxdb

# Zainstaluj zależności
pip install -r requirements.txt psutil requests
```

### 2. Uruchomienie testów
```bash
# Sprawdź kompatybilność systemu
python deploy_vm.py
```

### 3. Uruchomienie produkcyjne
```bash
# Start serwisu
python deploy_vm.py

# W osobnym terminalu - monitoring
python vm_health_check.py --monitor
```

## 🔍 Monitoring

### Health Check
```bash
# Jednorazowy check
python vm_health_check.py

# Ciągły monitoring (co 60s)
python vm_health_check.py --monitor

# Niestandardowy interwał
python vm_health_check.py --monitor --interval 30
```

### API Endpoints
```bash
# Status systemu
curl http://0.0.0.0:5000/status

# Health check
curl http://0.0.0.0:5000/health

# Metrics
curl http://0.0.0.0:5000/metrics
```

## 🛡️ Bezpieczeństwo VM

### Konfiguracja zapory
```bash
# Otwórz porty
sudo ufw allow 5000/tcp  # REST API
sudo ufw allow 5001/tcp  # WebSocket
sudo ufw enable
```

### Ograniczenia zasobów
```bash
# Systemd service limits
[Service]
MemoryLimit=1G
CPUQuota=80%
```

## 🔄 Automatyzacja

### Systemd Service
```ini
[Unit]
Description=LuxDB v2 Service
After=network.target

[Service]
Type=simple
User=luxdb
WorkingDirectory=/opt/luxdb
ExecStart=/usr/bin/python3 deploy_vm.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

### Cron Monitoring
```bash
# Dodaj do crontab
*/5 * * * * /usr/bin/python3 /opt/luxdb/vm_health_check.py >> /var/log/luxdb_health.log 2>&1
```

## 📊 Wydajność

### Benchmark VM
- **Startup**: < 5s
- **API Response**: < 100ms
- **Memory Usage**: ~50MB base
- **Throughput**: 100+ req/s

### Optymalizacja
```python
# vm_config.json
{
  "meditation_interval": 300,  # Zwiększ dla VM
  "harmony_check_interval": 120,
  "wisdom": {
    "query_timeout": 30,
    "auto_optimize": true
  }
}
```

## 🆘 Troubleshooting

### Problem: Port zajęty
```bash
# Znajdź proces
sudo netstat -tulpn | grep :5000
sudo kill -9 <PID>
```

### Problem: Brak uprawnień do bazy
```bash
# Napraw uprawnienia
chmod 664 db/vm_production.db
chown luxdb:luxdb db/vm_production.db
```

### Problem: Wysoki CPU
```bash
# Zwiększ interwały w konfiguracji
{
  "meditation_interval": 600,
  "harmony_check_interval": 300
}
```

## 📈 Skalowanie

### Horizontal Scaling
- Uruchom wiele instancji na różnych portach
- Użyj load balancer (nginx, haproxy)
- Shared database lub replicas

### Vertical Scaling
- Zwiększ RAM/CPU VM
- Optymalizuj konfigurację
- Użyj SSD storage

## ✅ Checklist Wdrożenia

- [ ] Sprawdzone wymagania systemowe
- [ ] Zainstalowane zależności
- [ ] Uruchomione testy deployment
- [ ] Skonfigurowany firewall
- [ ] Ustawiony monitoring
- [ ] Skonfigurowany systemd service
- [ ] Backup strategy
- [ ] Log rotation
- [ ] Alerting system

**LuxDB v2 gotowe do produkcji na VM!** 🚀
