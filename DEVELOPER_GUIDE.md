# 🔄 FEDERACJA - Przewodnik Developerski

## 🏗️ Architektura Dwurepozytoryjna

Projekt FEDERACJA został podzielony na dwa niezależne repozytoria:

### 🔧 Backend - LuxDB (to repozytorium)
```bash
git clone https://github.com/oriom/luxdb.git
cd luxdb
pip install -r requirements.txt
```

**Zawiera:**
- Core engine bazy danych (LuxDB)
- API endpoints i routing
- System warstw (Layer 0-4)
- Zarządzanie bytami i realms
- Validation i security

### 🎨 Frontend - Dashboard
```bash
git clone https://github.com/oriom/federacja-frontend.git
cd federacja-frontend
python3 dev-server.py
```

**Zawiera:**
- Interaktywny dashboard
- Real-time monitorowanie
- Wizualizacja architektury
- Standalone deployment

## 🔄 Workflow Developerski

### Praca Lokalna
```bash
# Terminal 1: Backend
cd luxdb
python -m uvicorn main:app --reload --port 8000

# Terminal 2: Frontend  
cd federacja-frontend
python3 dev-server.py
# Otwórz: http://localhost:3000
```

### Integracja
- **API Base URL**: `http://localhost:8000` (dev) / `https://your-api.com` (prod)
- **CORS**: Skonfigurowany dla cross-origin requests
- **Environment Variables**: Zarządzane przez `.env` files

### Deployment
- **Backend**: Tradycyjny deploy na serwerze (Heroku, DigitalOcean, AWS)
- **Frontend**: One-click deploy na Vercel z GitHub integration

## 📋 Checklist przed Push

### Backend
- [ ] Testy przechodzą: `pytest`
- [ ] Linting: `flake8` / `black`
- [ ] API dokumentacja aktualna
- [ ] Migration files (jeśli są zmiany DB)

### Frontend
- [ ] Działające funkcje: `python3 dev-server.py`
- [ ] Responsive design sprawdzony
- [ ] Console bez błędów
- [ ] Vercel deploy test

## 🚀 Quick Commands

### Backend Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run tests  
pytest

# Start API server
uvicorn main:app --reload

# Database migrations
alembic upgrade head
```

### Frontend Development
```bash
# Start dev server
python3 dev-server.py

# Deploy to Vercel
vercel --prod

# Test standalone version
open index-standalone.html
```

## 🔗 Przydatne Linki

- **Backend Repo**: https://github.com/oriom/luxdb
- **Frontend Repo**: https://github.com/oriom/federacja-frontend  
- **Frontend Live**: https://federacja-frontend.vercel.app
- **API Docs**: http://localhost:8000/docs (dev)

---

*Rozdzielenie na dwa repozytoria = lepsze zarządzanie, szybszy development, łatwiejszy deploy!* 🎯✨
