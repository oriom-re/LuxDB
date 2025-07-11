# lux_core/__init__.py
"""
LuxCore - Modularny system routingu i wykonywania zadań
"""
from .init import initialize_lux_core, get_system_info, test_route
from .routing import resolve, get_all_routes
from .auto_discovery import auto_register_routes, get_route_statistics

__version__ = "2.0.0"
__all__ = [
    "initialize_lux_core",
    "get_system_info", 
    "test_route",
    "resolve",
    "get_all_routes",
    "auto_register_routes",
    "get_route_statistics"
]
