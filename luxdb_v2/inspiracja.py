data = {
    "status": "working",             # główny status
    "schema": "<base64 or json>",    # opcjonalny opis struktury (np. tasków, typów danych)
    "module_on": True,               # aktywny moduł
    "progress": 0.42,                # opcjonalny postęp
    "eta": "3.5s",                   # czas oczekiwany
    "raport": {
        "status": "streaming",
        "chunks": {
            "0": "Pierwszy kawałek",
            "1": "Drugi kawałek"
        },
        "expected_chunks": 5
    },
    "metrics": {
        "memory_used": "45MB",
        "cpu": "23%"
    }
}


{
    "id": "event-abc123",
    "from": "ws-client-001",
    "type": "task_request",
    "data": {
        "status": "working",
        "schema": "<optional_schema>",
        ...
    },
    "task_tree": {
        "analyze": "running",
        "generate": "waiting",
        "stream": "idle"
    },
    "created_at": "2025-07-09T12:00:00Z"
}
