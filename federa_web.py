
#!/usr/bin/env python3
"""
🌐 Federa Web - Interfejs webowy do komunikacji z Federą

Prosty serwer Flask do komunikacji z Federą przez przeglądarkę
"""

from flask import Flask, render_template, request, jsonify
from datetime import datetime
import json
import asyncio

app = Flask(__name__)

class FederaWebInterface:
    """Interfejs webowy do komunikacji z Federą"""
    
    def __init__(self):
        self.chat_history = []
        
    async def send_to_federa(self, message: str) -> dict:
        """Wysyła wiadomość do Federy - symulacja"""
        
        # Parsuj komendę
        parts = message.lower().split()
        command = parts[0] if parts else ""
        
        # Symuluj odpowiedzi Federy
        if command == "status":
            return {
                'type': 'status',
                'message': 'Jestem Federa - aktywna i monitoruję system! 🧠',
                'data': {
                    'active': True,
                    'modules': 2,
                    'system_load': 0.3,
                    'issues': 1
                }
            }
        elif command == "modules":
            return {
                'type': 'modules',
                'message': 'Oto lista modułów w systemie:',
                'data': {
                    'active': ['database_manager'],
                    'managed_by_federa': ['module_metadata_manager', 'realm_memory'],
                    'failed': ['realm_memory']
                }
            }
        elif command == "health":
            return {
                'type': 'health',
                'message': 'Sprawdzam zdrowie modułów...',
                'data': {
                    'database_manager': True,
                    'realm_memory': False,
                    'federa': True
                }
            }
        elif command == "help":
            return {
                'type': 'help',
                'message': 'Dostępne komendy: status, modules, health, diagnosis, logs',
                'data': {
                    'commands': [
                        'status - sprawdź mój status',
                        'modules - lista modułów',
                        'health - zdrowie modułów',
                        'diagnosis - diagnostyka systemu',
                        'logs - wyświetl logi'
                    ]
                }
            }
        elif command == "diagnosis":
            return {
                'type': 'diagnosis',
                'message': 'Przeprowadzam pełną diagnostykę systemu...',
                'data': {
                    'can_manage': True,
                    'working_components': ['federation_bus', 'database_manager'],
                    'issues': ['realm_memory: błąd konstruktora'],
                    'suggestions': ['Napraw konstruktor MemoryRealmModule']
                }
            }
        else:
            return {
                'type': 'conversation',
                'message': f'Rozumiem Twoje pytanie: "{message}". Jako Federa, jestem tutaj aby pomóc! Spróbuj komend: status, modules, health, diagnosis.',
                'data': {
                    'suggestion': 'Użyj "help" aby zobaczyć wszystkie dostępne komendy'
                }
            }

# Globalna instancja interfejsu
federa_web = FederaWebInterface()

@app.route('/')
def index():
    """Strona główna"""
    return render_template('federa_chat.html')

@app.route('/send', methods=['POST'])
def send_message():
    """Wysyła wiadomość do Federy"""
    try:
        data = request.json
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({'error': 'Pusta wiadomość'}), 400
        
        # Zapisz wiadomość użytkownika
        user_msg = {
            'timestamp': datetime.now().isoformat(),
            'sender': 'user',
            'message': message
        }
        federa_web.chat_history.append(user_msg)
        
        # Wyślij do Federy (symulacja)
        response = asyncio.run(federa_web.send_to_federa(message))
        
        # Zapisz odpowiedź Federy
        federa_msg = {
            'timestamp': datetime.now().isoformat(),
            'sender': 'federa',
            'message': response.get('message', 'Brak odpowiedzi'),
            'type': response.get('type', 'unknown'),
            'data': response.get('data', {})
        }
        federa_web.chat_history.append(federa_msg)
        
        return jsonify({
            'success': True,
            'response': federa_msg
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/history')
def get_history():
    """Pobiera historię chatu"""
    return jsonify({
        'history': federa_web.chat_history[-50:]  # Ostatnie 50 wiadomości
    })

@app.route('/clear')
def clear_history():
    """Czyści historię chatu"""
    federa_web.chat_history.clear()
    return jsonify({'success': True})

if __name__ == '__main__':
    print("🌐 Uruchamianie Federa Web Interface...")
    print("🔗 Otwórz: http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
