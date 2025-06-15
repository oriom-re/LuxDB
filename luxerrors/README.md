
# LuxErrors - Universal Error Handling System

LuxErrors to niezależny system obsługi błędów wyodrębniony z biblioteki LuxDB. Zapewnia ustandaryzowane podejście do zarządzania błędami w aplikacjach Python.

## 🚀 Funkcje

- **Ustandaryzowane kody błędów** - Hierarchiczny system kodów błędów
- **Kontekstowe informacje** - Bogate informacje o błędach z kontekstem
- **Automatyczna detekcja** - Inteligentne wykrywanie typów błędów
- **Integracja z logowaniem** - Wbudowana obsługa logowania
- **Kolektor błędów** - Zbieranie błędów w operacjach batch
- **Dekoratory** - Łatwa obsługa błędów przez dekoratory
- **Walidacja danych** - Wbudowane narzędzia walidacji

## 📦 Instalacja

```bash
pip install luxerrors
```

## 🛠️ Szybki start

### Podstawowe użycie

```python
from luxerrors import LuxError, ValidationError, handle_errors

# Rzucanie błędu z kontekstem
try:
    raise ValidationError(
        "Invalid user data",
        field_errors={"email": "Invalid format"},
        context={"user_id": 123}
    )
except LuxError as e:
    print(e.get_detailed_info())
```

### Dekorator obsługi błędów

```python
from luxerrors import handle_errors

@handle_errors("user_creation", return_result=True)
def create_user(username: str, email: str):
    if not username:
        raise ValidationError("Username is required")
    return {"id": 1, "username": username}

success, result = create_user("john", "john@example.com")
```

### Kolektor błędów dla operacji batch

```python
from luxerrors import ErrorCollector

collector = ErrorCollector("batch_import")

for item in data:
    collector.increment_total()
    try:
        process_item(item)
        collector.add_success()
    except Exception as e:
        collector.add_error(e, {"item": item})

summary = collector.get_summary()
print(f"Success rate: {summary['success_rate']:.1f}%")
```

### Integracja z logowaniem

```python
from luxerrors import get_error_logger, log_error_event

logger = get_error_logger()

try:
    risky_operation()
except Exception as e:
    log_error_event(e, operation="data_sync", structured=True)
```

## 📚 Dokumentacja

### Kody błędów

System używa hierarchicznych kodów błędów:

- **1000-1999**: Błędy ogólne
- **2000-2999**: Błędy połączenia  
- **3000-3999**: Błędy danych
- **4000-4999**: Błędy operacji
- **5000-5999**: Błędy systemu plików
- **6000-6999**: Błędy API/HTTP
- **7000-7999**: Błędy zewnętrznych usług

### Typy wyjątków

- `LuxError` - Bazowy wyjątek systemu
- `ValidationError` - Błędy walidacji danych
- `ConnectionError` - Błędy połączenia
- `DataNotFoundError` - Błędy braku danych
- `DuplicateDataError` - Błędy duplikatów
- `OperationError` - Błędy operacji

### Narzędzia

- `ErrorCollector` - Zbieranie błędów w operacjach batch
- `ErrorLogger` - Specjalizowany logger błędów
- `handle_errors` - Dekorator obsługi błędów
- `safe_execute` - Bezpieczne wykonywanie funkcji

## 🎯 Przykłady użycia

Zobacz plik `examples.py` dla szczegółowych przykładów użycia wszystkich funkcji biblioteki.

## 🤝 Rozwój

LuxErrors jest częścią ekosystemu LuxDB. Zapraszamy do współpracy:

- Zgłaszanie błędów i propozycji
- Rozwijanie nowych funkcji
- Poprawa dokumentacji

## 📄 Licencja

MIT License - szczegóły w pliku LICENSE.

## 🔗 Linki

- [Repozytorium](https://github.com/luxdb/luxerrors)
- [Dokumentacja](https://luxerrors.readthedocs.io)
- [LuxDB](https://github.com/luxdb/luxdb)
