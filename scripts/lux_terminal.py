# lux_terminal.py
"""
Interaktywny terminal LuxCore do live debuggingu i zarządzania systemem.
"""
import sys
from lux_core.init import initialize_lux_core
from lux_core.routing import resolve_lux_uri

def lux_terminal():
    """Uruchamia interaktywny terminal LuxCore"""
    print("""
    🌟 Lux Terminal 🌟
    -----------------
    Witaj w interaktywnym terminalu LuxCore!
    Dostępne komendy:
      - help: Wyświetl pomoc
      - exit: Wyjdź z terminala
      - route <uri>: Wykonaj route (np. route system/routing/stats@v1)
    """)

    # Inicjalizacja systemu
    print("🔧 Inicjalizacja systemu...")
    initialize_lux_core()
    print("✅ System zainicjalizowany!")

    while True:
        try:
            command = input("lux> ").strip()
            if command == "exit":
                print("👋 Do zobaczenia!")
                break
            elif command == "help":
                print("""
    Dostępne komendy:
      - help: Wyświetl pomoc
      - exit: Wyjdź z terminala
      - route <uri>: Wykonaj route (np. route system/routing/stats@v1)
                """)
            elif command.startswith("route "):
                uri = command.split(" ", 1)[1]
                try:
                    func = resolve_lux_uri(uri)
                    result = func()
                    print("📊 Wynik:")
                    print(result)
                except Exception as e:
                    print(f"❌ Błąd: {e}")
            else:
                print("❓ Nieznana komenda. Użyj 'help' aby zobaczyć dostępne komendy.")
        except KeyboardInterrupt:
            print("\n👋 Do zobaczenia!")
            break

if __name__ == "__main__":
    lux_terminal()
