# layer0/bootstrap.py
"""
Inicjalizacja i ładowanie zmiennych środowiskowych (bootstrap warstwy 0)
"""
from ..decorators import lux_route


@lux_route("system/bootstrap/env/load@v1", description="Ładowanie zmiennych środowiskowych z pliku")
def load_env(config="default", filepath=".env"):
    """
    Ładowanie zmiennych środowiskowych z pliku .env.
    Domyślnie ładuje plik .env w bieżącym katalogu.
    """
    try:
        env_vars = load_env_file(filepath)
        return {"status": "loaded", "config": config, "env_vars": env_vars}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def load_env_file(filepath):
    env_vars = {}
    with open(filepath) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, value = line.split("=", 1)
                env_vars[key.strip()] = value.strip()
    return env_vars
