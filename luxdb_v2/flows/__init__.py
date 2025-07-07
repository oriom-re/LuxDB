
"""
🌊 LuxDB v2 Flows - TYLKO Stałe Przepływy Systemowe

FLOWS = STAŁE PLIKI SYSTEMOWE (niezmienne)
- Podstawowa infrastruktura
- Komunikacja HTTP/WebSocket  
- Naprawy i stabilność systemu

Wszystkie NOWE funkcjonalności powstają jako BEINGS w prototypes/beings/
- Świadome, inteligentne byty
- Samomodyfikujące się
- Z własną logią i algorytmami
"""

from .rest_flow import RestFlow
from .callback_flow import CallbackFlow
from .self_healing_flow import SelfHealingFlow
from .repair_flow import RepairFlow
from .cloud_flow_executor import CloudFlowExecutor

# BEINGS zastępują flows - nowe funkcjonalności tylko jako świadome byty:
# - GPTBeing (prototypes/beings/) - zastępuje gpt_flow
# - WebSocketBeing (prototypes/beings/) - zastępuje ws_flow  
# - FederationBeing (prototypes/beings/) - zastępuje federation_flow
# - PDFGeneratorBeing (prototypes/beings/) - zastępuje pdf_generator_flow
# - AutomatedTestingBeing (prototypes/beings/) - zastępuje automated_testing_flow

__all__ = ['RestFlow', 'CallbackFlow']
