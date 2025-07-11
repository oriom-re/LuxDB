import os
from dotenv import load_dotenv

# Załaduj .env z katalogu lux_core oraz systemowe env
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

def load_env(config="default"):
    """
    Łączy zmienne z .env (lux_core) oraz systemowe os.environ.
    """
    env_vars = dict(os.environ)
    # Możesz dodać tu logikę filtrowania/prefiksowania
    result = {
        "env_name": env_vars.get("LUX_ENV", config),
        "resources": {
            "cpu": 2,
            "ram": "2GB"
        },
        "status": "initialized",
        "debug": env_vars.get("LUX_DEBUG", "false"),
        "secret_key": env_vars.get("LUX_SECRET_KEY", "")
    }
    return result

