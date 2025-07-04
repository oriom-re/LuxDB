# lux-core-bus.md

LuxCoreBus – Wewnętrzny i zewnętrzny system komunikacji bytów

🎯 Cel
Stworzenie jednego, uniwersalnego systemu komunikacji opartego o komunikaty typu packet, który może działać:

lokalnie między modułami LuxCore

przez WebSocket między klientem a serwerem

pomiędzy bytami w rozproszonej sieci LuxChain

🧠 Główne założenia
🔄 Pub/Sub – Każdy byt może emitować i subskrybować wiadomości

🧱 UID Routing – Wiadomości kierowane do/by UID (np. tasków, klientów, bytów)

🧩 Stream Support – Obsługa transmisji pakietowej (np. chunkowane wiadomości)

🧠 State Memory – System zapamiętuje, które fragmenty zostały odebrane

🔁 Recovery – Obsługa retransmisji i synchronizacji zagubionych danych

🧭 Dispatcher – Centralna jednostka przekierowująca dane

📦 Struktura pakietu
json
Kopiuj
Edytuj
{
  "uid": "task_abc123",
  "from": "clientA",
  "to": "clientB" | "dispatcher" | null,
  "type": "command" | "event" | "stream",
  "chunk": 3,
  "of": 12,
  "is_final": false,
  "data": "...",
  "timestamp": 172344567.001,
  "status": "ack" | "missing" | "complete"
}
📡 Warstwy działania
1. LuxDispatcher
Przekazuje pakiety do odpowiednich odbiorców (to)

Buforuje dane jeśli odbiorcy nie ma (cache + retry)

2. LuxStreamManager
Obsługuje dane chunkowane

Prowadzi history, ack, missing

3. LuxClient
Wysyła i odbiera wiadomości

Zgłasza zapotrzebowanie na brakujące pakiety

Może służyć jako punkt wymiany między użytkownikami (np. LuxInputStream)

💬 Przykłady
🔁 Potwierdzenie odebranych chunków
json


{
  "uid": "stream_abc",
  "from": "clientB",
  "type": "stream",
  "status": "ack",
  "ack": [0, 1, 2]
}
🔍 Zapytanie o brakujące pakiety
json


{
  "uid": "stream_abc",
  "from": "clientB",
  "type": "stream",
  "status": "missing",
  "missing": [3, 4]
}
🧰 Możliwe zastosowania
Komunikacja między funkcjami LuxWorker w wielu językach

Transmisja LuxInputStream (znaki w czasie rzeczywistym)

Synchronizacja modeli i klientów w LuxChain

Lokalna komunikacja między mikrobytami LuxCore

Emulacja WebSocket w środowiskach bezpośrednich

📅 Następne kroki
 Implementacja lux_dispatcher.py

 Bufor LuxStreamMemory

 API do tworzenia i obsługi wiadomości

 Protokół retransmisji i zakończenia streamu