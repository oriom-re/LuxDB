# core/validation.py

def validate_data(data):
    """
    Prosta walidacja danych inicjalizacyjnych środowiska.
    Zwraca dict z wynikiem walidacji.
    """
    if data == "init":
        return {"valid": True, "reason": "Initial data accepted."}
    return {"valid": False, "reason": "Unknown data."}
