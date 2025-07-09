from .routing import resolve_function

LUX_ROUTING = {
    "system/loader/load_env@v1": "module://core.env:load_env",
    "system/loader/validate_data@v1": "module://core.validation:validate_data",
    "system/loader/load_env@v2": "module://core.env:load_env_v2",
    "system/loader/validate_data@v2": "module://core.validation:validate_data_v2"
}

def resolve_lux_uri(lux_path):
    if "@" in lux_path:
        base, version = lux_path.split("@")
    else:
        base, version = lux_path, "latest"
    full_key = f"{base}@{version}"
    if full_key not in LUX_ROUTING:
        if version == "latest":
            available = [k for k in LUX_ROUTING.keys() if k.startswith(f"{base}@v")]
            if not available:
                raise ValueError(f"Nie znaleziono żadnej wersji dla {base}")
            latest = sorted(available, key=lambda k: int(k.split("@v")[-1]), reverse=True)[0]
            full_key = latest
        else:
            raise ValueError(f"Brak zarejestrowanego path: {full_key}")
    return resolve_function(LUX_ROUTING[full_key])
