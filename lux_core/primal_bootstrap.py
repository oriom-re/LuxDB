# primal_bootstrap.py
# Scenariusz startowy warstwy 0 (primal layer)

scenario = {
    "steps": [
        {
            "uri": "lux://system/loader/load_env@v1",
            "args": {"config": "default"},
            "save_as": "env",
            "entity": {
                "id": "env-001",
                "type": "Environment",
                "meta": {"description": "Środowisko startowe warstwy 0"}
            }
        },
        {
            "uri": "lux://system/loader/validate_data@v1",
            "args": {"data": "init"},
            "save_as": "validation_result",
            "entity": {
                "id": "val-001",
                "type": "ValidationResult",
                "meta": {"description": "Wynik walidacji środowiska"}
            }
        }
    ]
}
