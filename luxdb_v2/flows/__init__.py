
"""
🌊 LuxDB v2 Flows - Podstawowe Przepływy Astralnej Energii

Tylko najważniejsze flows potrzebne do uruchomienia systemu.
Pozostałe flows są w prototypes/flows/ i wczytywane dynamicznie.
"""

from .rest_flow import RestFlow
from .callback_flow import CallbackFlow

# Flows załadowane przez CloudFlowExecutor z prototypów
# - WebSocketFlow (prototypes/flows/ws_flow.py)
# - GPTFlow (prototypes/flows/gpt_flow.py)
# - HybridGPTFlow (prototypes/flows/hybrid_gpt_flow.py)
# - SelfHealingFlow (prototypes/flows/self_healing_flow.py)
# - SelfImprovementFlow (prototypes/flows/self_improvement_flow.py)
# - AutomatedTestingFlow (prototypes/flows/automated_testing_flow.py)
# - IntentionFlow (prototypes/flows/intention_flow.py)
# - SecureCodeFlow (prototypes/flows/secure_code_flow.py)
# - StatefulTaskFlow (prototypes/flows/stateful_task_flow.py)
# - FederationFlow (prototypes/flows/federation_flow.py)
# - OriomFlow (prototypes/flows/oriom_flow.py)
# - PDFGeneratorFlow (prototypes/flows/pdf_generator_flow.py)
# - LuxBusWSFlow (prototypes/flows/luxbus_ws_flow.py)

__all__ = ['RestFlow', 'CallbackFlow']
