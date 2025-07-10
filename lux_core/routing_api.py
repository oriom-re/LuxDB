# lux_core/routing_api.py
"""
API do zarządzania routingiem w czasie rzeczywistym
"""
from typing import Dict, List, Optional, Any, Callable
from .routing import register_dynamic_route, unregister_dynamic_route, route_exists, get_route_metadata
from .decorators import lux_route, DECORATED_ROUTES
from .registry import LUX_ROUTING

class RoutingAPI:
    """
    API do zarządzania routingiem w czasie rzeczywistym
    """
    
    @staticmethod
    def add_route(path: str, function: Callable, metadata: Optional[Dict] = None) -> Dict:
        """
        Dodaje nową route dynamicznie
        """
        if route_exists(path):
            return {"status": "error", "message": f"Route {path} już istnieje"}
        
        register_dynamic_route(path, function, metadata)
        return {"status": "success", "message": f"Route {path} została dodana"}
    
    @staticmethod
    def remove_route(path: str) -> Dict:
        """
        Usuwa route dynamiczną
        """
        if path in LUX_ROUTING:
            return {"status": "error", "message": f"Nie można usunąć statycznej route {path}"}
        
        if unregister_dynamic_route(path):
            return {"status": "success", "message": f"Route {path} została usunięta"}
        else:
            return {"status": "error", "message": f"Route {path} nie istnieje"}
    
    @staticmethod
    def list_routes(route_type: Optional[str] = None) -> Dict:
        """
        Lista wszystkich route z opcjonalnym filtrowaniem
        """
        static_routes = list(LUX_ROUTING.keys())
        dynamic_routes = list(DECORATED_ROUTES.keys())
        
        if route_type == "static":
            return {"routes": static_routes, "type": "static", "count": len(static_routes)}
        elif route_type == "dynamic":
            return {"routes": dynamic_routes, "type": "dynamic", "count": len(dynamic_routes)}
        else:
            return {
                "static_routes": static_routes,
                "dynamic_routes": dynamic_routes,
                "total_count": len(static_routes) + len(dynamic_routes)
            }
    
    @staticmethod
    def get_route_info(path: str) -> Dict:
        """
        Zwraca szczegółowe informacje o route
        """
        if not route_exists(path):
            return {"status": "error", "message": f"Route {path} nie istnieje"}
        
        metadata = get_route_metadata(path)
        return {"status": "success", "path": path, "metadata": metadata}
    
    @staticmethod
    def update_route_metadata(path: str, metadata: Dict) -> Dict:
        """
        Aktualizuje metadane dynamicznej route
        """
        if path not in DECORATED_ROUTES:
            return {"status": "error", "message": f"Route {path} nie istnieje lub nie jest dynamiczna"}
        
        # Aktualizuj metadane
        DECORATED_ROUTES[path].update(metadata)
        return {"status": "success", "message": f"Metadane route {path} zostały zaktualizowane"}
    
    @staticmethod
    def search_routes(query: str) -> Dict:
        """
        Wyszukuje route zawierające zadany tekst
        """
        all_routes = list(LUX_ROUTING.keys()) + list(DECORATED_ROUTES.keys())
        matching_routes = [route for route in all_routes if query.lower() in route.lower()]
        
        return {
            "query": query,
            "matches": matching_routes,
            "count": len(matching_routes)
        }

# Dodaj API route
@lux_route("api/routing/add@v1", description="Dodaj nową route dynamicznie")
def add_route_api(path: str, function_module: str, function_name: str, metadata: Optional[Dict] = None):
    """API endpoint do dodawania route"""
    try:
        # Dynamically import function
        module = __import__(function_module, fromlist=[function_name])
        function = getattr(module, function_name)
        
        return RoutingAPI.add_route(path, function, metadata)
    except Exception as e:
        return {"status": "error", "message": f"Błąd podczas dodawania route: {str(e)}"}

@lux_route("api/routing/remove@v1", description="Usuń route dynamiczną")
def remove_route_api(path: str):
    """API endpoint do usuwania route"""
    return RoutingAPI.remove_route(path)

@lux_route("api/routing/list@v1", description="Lista wszystkich route")
def list_routes_api(route_type: Optional[str] = None):
    """API endpoint do listowania route"""
    return RoutingAPI.list_routes(route_type)

@lux_route("api/routing/info@v1", description="Informacje o konkretnej route")
def get_route_info_api(path: str):
    """API endpoint do pobierania informacji o route"""
    return RoutingAPI.get_route_info(path)

@lux_route("api/routing/search@v1", description="Wyszukaj route")
def search_routes_api(query: str):
    """API endpoint do wyszukiwania route"""
    return RoutingAPI.search_routes(query)
