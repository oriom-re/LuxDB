
"""
🌟 LuxDB v2 Beings - Podstawowe Samoświadome Byty Astralne

Tylko najważniejsze beings potrzebne do uruchomienia systemu.
Pozostałe beings są w prototypes/beings/ i wczytywane dynamicznie.
"""

from .base_being import BaseBeing
from .manifestation import Manifestation
from .intention_being import IntentionBeing

# Beings załadowane przez SelfImprovementFlow z prototypów
# - LogicalBeing (prototypes/beings/logical_being.py)
# - ErrorHandlerBeing (prototypes/beings/error_handler_being.py)
# - PDFGeneratorBeing (prototypes/beings/pdf_generator_being.py)
# - GeneticIdentification (prototypes/beings/genetic_identification.py)
# - LuxBus (prototypes/beings/luxbus.py)
# - LuxResurerector (prototypes/beings/lux_resurector.py)
# - Runner (prototypes/beings/runner.py)
# - Save (prototypes/beings/save.py)
# - Load (prototypes/beings/load.py)
# - Types (prototypes/beings/types.py)

__all__ = ['BaseBeing', 'Manifestation', 'IntentionBeing']
