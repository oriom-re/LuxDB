
# LuxDB Services

Ten folder zawiera dedykowane serwisy dla różnych trybów uruchamiania LuxDB.

## Dostępne serwisy

### 1. LuxAPI Service (`luxapi_service.py`)
**Standalone REST API**
- Port: 5000
- Tylko endpoints HTTP/REST
- Idealny dla: integracji z aplikacjami, API-only deployment

```bash
python service/luxapi_service.py
```

**Endpoints:**
- `GET /` - Informacje o serwisie
- `GET /api/health` - Health check
- `POST /api/auth/login` - Logowanie
- `POST /api/auth/register` - Rejestracja
- `GET /api/databases` - Lista baz danych
- `POST /api/databases/<db_name>/query` - Wykonanie zapytania SQL

### 2. LuxWS Service (`luxws_service.py`)
**Standalone WebSocket Server**
- Port: 5001
- Tylko komunikacja WebSocket
- Idealny dla: real-time aplikacji, live sync

```bash
python service/luxws_service.py
```

**Funkcjonalności:**
- Real-time synchronizacja danych
- Pokoje dla różnych baz danych
- Dwukierunkowa komunikacja
- Automatyczne heartbeat
- Zarządzanie sesjami użytkowników

### 3. LuxCore Service (`luxcore_service.py`)
**Zintegrowany serwis (API + WebSocket)**
- Development: API (5000) + WebSocket (5001)
- Deployment: Wszystko na porcie 5000
- Idealny dla: pełne aplikacje, production deployment

```bash
python service/luxcore_service.py
```

**Tryby:**
- **Development**: Osobne porty dla API i WebSocket
- **Deployment**: Zintegrowany serwer na jednym porcie

## Wybór serwisu

| Potrzebujesz | Użyj | Port(y) |
|--------------|------|---------|
| Tylko REST API | `luxapi_service.py` | 5000 |
| Tylko WebSocket | `luxws_service.py` | 5001 |
| Pełną funkcjonalność | `luxcore_service.py` | 5000+5001 lub 5000 |
| Production deployment | `luxcore_service.py` | 5000 |

## Konfiguracja środowiska

### Development
```bash
# Uruchom pełny stos
python service/luxcore_service.py

# Lub osobno:
python service/luxapi_service.py &
python service/luxws_service.py &
```

### Production/Deployment
```bash
# Ustaw zmienną środowiskową
export REPL_DEPLOYMENT=1

# Uruchom zintegrowany serwis
python service/luxcore_service.py
```

## Funkcjonalności wszystkich serwisów

### Wspólne
- Automatyczna konfiguracja bazy danych
- Tworzenie użytkownika testowego (`testuser` / `testpass123`)
- Okresowa konserwacja (czyszczenie wygasłych sesji)
- Obsługa sygnałów systemowych (graceful shutdown)
- Szczegółowe logowanie

### Specyficzne dla WebSocket
- Zarządzanie aktywnych połączeń
- Pokoje dla baz danych
- Broadcast zmian w czasie rzeczywistym
- Cleanup nieaktywnych połączeń

### Specyficzne dla API
- CORS włączony dla wszystkich endpoints
- Uwierzytelnianie przez Bearer token
- RESTful endpoints dla wszystkich operacji
- Obsługa błędów i walidacja

## Monitorowanie

Wszystkie serwisy udostępniają endpoint health check:
```
GET http://0.0.0.0:5000/api/health
```

Zwraca informacje o:
- Status serwisu
- Liczba baz danych
- Timestamp
- Wersja

## Bezpieczeństwo

⚠️ **Uwaga**: Domyślne klucze szyfrowania są przeznaczone tylko do rozwoju. 
W produkcji ustaw:
- `LUXAPI_SECRET_KEY` - dla REST API
- `LUXWS_SECRET_KEY` - dla WebSocket server
