
# 📁 Prototypes - Folder Prototypowy

Ten folder zawiera prototypy funkcjonalności, które mogą być:

1. **Edytowane fizycznie** przez programistę w Replit
2. **Skopiowane automatycznie** przez system chmurowy
3. **Użyte jako fallback** gdy główne moduły nie działają

## Jak to działa:

### 1. Rozwój prototypów
```python
# Edytujesz prototypes/nowa_funkcja.py
def moja_funkcja():
    return "Nowa funkcjonalność"
```

### 2. Automatyczne kopiowanie
System chmurowy wykrywa zmiany i kopiuje prototyp do bazy jako nowy flow lub moduł.

### 3. Fallback mechanism
Gdy główny moduł nie działa, system automatycznie używa prototypu.

## Dostępne prototypy:

- **gpt_alternative.py** - Alternatywna komunikacja z Astrą
- **error_analysis.py** - Analiza błędów systemu  
- **[Dodaj więcej według potrzeb]**

## Namespace dla prototypów:

Każdy prototyp ma dostęp do:
- `engine` - AstralEngine instance
- `user_message` - Wiadomość użytkownika (jeśli dotyczy)
- `user_id` - ID użytkownika
- `error_stats` - Statystyki błędów (jeśli dostępne)

## Wymagania:

1. Prototyp musi ustawić `astra_response` w namespace
2. Opcjonalnie może ustawić `actions_executed` i `action_results`
3. Powinien być odporny na błędy (try-catch)

## Przykład użycia:

```python
def moja_funkcja():
    try:
        # Twoja logika
        result = engine.meditate()
        astra_response = f"Wynik: {result}"
        actions_executed = 1
    except Exception as e:
        astra_response = f"Błąd: {e}"
        actions_executed = 0

# Ustaw w namespace
astra_response = moja_funkcja()
```
