#!/usr/bin/env python3
"""
Graficzna wizualizacja systemu LuxCore - mapa architektury i routingu
"""
import sys
import os
sys.path.insert(0, '/var/home/oriom/Dokumenty/Federacja/luxdb')

from lux_core.init import initialize_lux_core
from lux_core.routing import get_all_routes
from lux_core.auto_discovery import get_route_statistics

def generate_system_visualization():
    """
    Generuje HTML wizualizację systemu LuxCore
    """
    # Inicjalizacja i pobranie danych
    init_result = initialize_lux_core()
    all_routes = get_all_routes()
    stats = get_route_statistics()
    
    # Grupowanie route według kategorii
    route_categories = {}
    for path, info in all_routes.items():
        parts = path.split('/')
        category = parts[0] if parts else 'unknown'
        subcategory = parts[1] if len(parts) > 1 else 'general'
        
        if category not in route_categories:
            route_categories[category] = {}
        if subcategory not in route_categories[category]:
            route_categories[category][subcategory] = []
        
        route_categories[category][subcategory].append({
            'path': path,
            'type': info['type'],
            'description': info['metadata'].get('description', 'Brak opisu')
        })
    
    # Generowanie HTML
    html = f"""
<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LuxCore System Architecture</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        }}
        h1 {{
            text-align: center;
            color: #2c3e50;
            margin-bottom: 10px;
            font-size: 2.5em;
            background: linear-gradient(45deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        .subtitle {{
            text-align: center;
            color: #7f8c8d;
            margin-bottom: 30px;
            font-size: 1.2em;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        .stat-card {{
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            padding: 25px;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 10px 20px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }}
        .stat-card:hover {{
            transform: translateY(-5px);
        }}
        .stat-number {{
            font-size: 3em;
            font-weight: bold;
            margin-bottom: 10px;
        }}
        .stat-label {{
            font-size: 1.1em;
            opacity: 0.9;
        }}
        .categories-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 30px;
            margin-top: 40px;
        }}
        .category-card {{
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            border-left: 5px solid #3498db;
        }}
        .category-title {{
            font-size: 1.5em;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 20px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        .subcategory {{
            margin-bottom: 20px;
            background: #f8f9fa;
            border-radius: 10px;
            padding: 15px;
        }}
        .subcategory-title {{
            font-weight: bold;
            color: #34495e;
            margin-bottom: 10px;
            font-size: 1.1em;
        }}
        .route-item {{
            display: flex;
            align-items: center;
            margin-bottom: 8px;
            padding: 8px;
            background: white;
            border-radius: 5px;
            border-left: 3px solid #3498db;
        }}
        .route-item.dynamic {{
            border-left-color: #e74c3c;
        }}
        .route-path {{
            font-family: 'Courier New', monospace;
            font-weight: bold;
            color: #2c3e50;
            flex: 1;
        }}
        .route-type {{
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 0.8em;
            font-weight: bold;
            margin-left: 10px;
        }}
        .route-type.static {{
            background: #3498db;
            color: white;
        }}
        .route-type.dynamic {{
            background: #e74c3c;
            color: white;
        }}
        .route-description {{
            font-size: 0.9em;
            color: #7f8c8d;
            margin-top: 5px;
        }}
        .legend {{
            display: flex;
            justify-content: center;
            gap: 30px;
            margin-top: 30px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 10px;
        }}
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .legend-color {{
            width: 20px;
            height: 20px;
            border-radius: 3px;
        }}
        .legend-color.static {{
            background: #3498db;
        }}
        .legend-color.dynamic {{
            background: #e74c3c;
        }}
        .architecture-flow {{
            margin-top: 40px;
            padding: 30px;
            background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
            border-radius: 15px;
        }}
        .flow-title {{
            font-size: 1.8em;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 20px;
            text-align: center;
        }}
        .flow-diagram {{
            display: flex;
            justify-content: center;
            align-items: center;
            flex-wrap: wrap;
            gap: 20px;
        }}
        .flow-step {{
            background: white;
            padding: 15px 20px;
            border-radius: 10px;
            border: 2px solid #3498db;
            font-weight: bold;
            color: #2c3e50;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        .flow-arrow {{
            font-size: 1.5em;
            color: #3498db;
            margin: 0 10px;
        }}
        @media (max-width: 768px) {{
            .categories-grid {{
                grid-template-columns: 1fr;
            }}
            .stats-grid {{
                grid-template-columns: 1fr;
            }}
            .flow-diagram {{
                flex-direction: column;
            }}
            .flow-arrow {{
                transform: rotate(90deg);
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🌟 LuxCore System Architecture</h1>
        <p class="subtitle">Dynamiczny system routingu i wykonywania zadań - Wersja 2.0</p>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number">{stats['total_routes']}</div>
                <div class="stat-label">Łączna liczba Route</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{stats['static_routes']}</div>
                <div class="stat-label">Route Statyczne</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{stats['dynamic_routes']}</div>
                <div class="stat-label">Route Dynamiczne</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{len(init_result['discovery']['discovered_modules'])}</div>
                <div class="stat-label">Załadowane Moduły</div>
            </div>
        </div>
        
        <div class="architecture-flow">
            <div class="flow-title">🔄 Przepływ Architektury</div>
            <div class="flow-diagram">
                <div class="flow-step">Auto-Discovery</div>
                <div class="flow-arrow">→</div>
                <div class="flow-step">Module Loading</div>
                <div class="flow-arrow">→</div>
                <div class="flow-step">Route Registration</div>
                <div class="flow-arrow">→</div>
                <div class="flow-step">Dynamic Routing</div>
                <div class="flow-arrow">→</div>
                <div class="flow-step">API Execution</div>
            </div>
        </div>
        
        <div class="categories-grid">
    """
    
    # Generowanie kart kategorii
    for category, subcategories in route_categories.items():
        category_icon = {
            'system': '⚙️',
            'api': '🔌',
            'custom': '✨'
        }.get(category, '📁')
        
        html += f"""
            <div class="category-card">
                <div class="category-title">{category_icon} {category.upper()}</div>
        """
        
        for subcategory, routes in subcategories.items():
            html += f"""
                <div class="subcategory">
                    <div class="subcategory-title">📋 {subcategory.title()}</div>
            """
            
            for route in routes:
                route_class = 'dynamic' if route['type'] == 'dynamic' else 'static'
                html += f"""
                    <div class="route-item {route_class}">
                        <div>
                            <div class="route-path">{route['path']}</div>
                            <div class="route-description">{route['description']}</div>
                        </div>
                        <div class="route-type {route_class}">{route['type'].upper()}</div>
                    </div>
                """
            
            html += "</div>"
        
        html += "</div>"
    
    # Zakończenie HTML
    html += f"""
        </div>
        
        <div class="legend">
            <div class="legend-item">
                <div class="legend-color static"></div>
                <span>Route Statyczne (Registry)</span>
            </div>
            <div class="legend-item">
                <div class="legend-color dynamic"></div>
                <span>Route Dynamiczne (Decorators)</span>
            </div>
        </div>
        
        <div style="text-align: center; margin-top: 40px; padding: 20px; background: #f8f9fa; border-radius: 10px;">
            <p style="color: #7f8c8d; font-size: 0.9em;">
                🚀 Wygenerowano automatycznie przez LuxCore System v2.0<br>
                📊 Dane z {len(init_result['discovery']['discovered_modules'])} modułów | 
                🔄 {stats['total_routes']} route dostępnych | 
                ⚡ Auto-discovery aktywne
            </p>
        </div>
    </div>
</body>
</html>
    """
    
    return html

def save_visualization():
    """
    Zapisuje wizualizację do pliku HTML
    """
    html_content = generate_system_visualization()
    
    output_file = '/var/home/oriom/Dokumenty/Federacja/luxdb/luxcore_system_visualization.html'
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ Wizualizacja systemu zapisana w: {output_file}")
    print(f"🌐 Otwórz plik w przeglądarce aby zobaczyć pełną mapę architektury!")
    
    return output_file

if __name__ == "__main__":
    print("🎨 Generowanie wizualizacji systemu LuxCore...")
    output_file = save_visualization()
    print(f"\n🎯 Gotowe! Wizualizacja dostępna w: {output_file}")
