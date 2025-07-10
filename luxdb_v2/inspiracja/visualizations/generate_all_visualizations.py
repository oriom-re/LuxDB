#!/usr/bin/env python3
"""
Master generator - tworzy wszystkie wizualizacje systemu LuxCore
"""
import sys
import os
sys.path.insert(0, '/var/home/oriom/Dokumenty/Federacja/luxdb')

from generate_system_visualization import save_visualization
from generate_interactive_map import save_interactive_map
from generate_dashboard import save_dashboard
from lux_core.init import initialize_lux_core
from lux_core.routing import get_all_routes
from lux_core.auto_discovery import get_route_statistics

def generate_all_visualizations():
    """
    Generuje wszystkie wizualizacje systemu LuxCore
    """
    print("🎨 === LUXCORE VISUALIZATION SUITE === 🎨")
    print("Generowanie kompletnej wizualizacji systemu...\n")
    
    # Inicjalizacja systemu
    print("🔧 Inicjalizacja systemu LuxCore...")
    init_result = initialize_lux_core()
    stats = get_route_statistics()
    
    print(f"   ✅ System zainicjalizowany:")
    print(f"   📊 {stats['total_routes']} route ({stats['static_routes']} statycznych + {stats['dynamic_routes']} dynamicznych)")
    print(f"   📦 {len(init_result['discovery']['discovered_modules'])} modułów załadowanych")
    print()
    
    # Generowanie wizualizacji
    visualizations = []
    
    print("1. 📋 Generowanie podstawowej wizualizacji systemu...")
    try:
        viz_file = save_visualization()
        visualizations.append(("System Visualization", viz_file))
        print("   ✅ Podstawowa wizualizacja wygenerowana")
    except Exception as e:
        print(f"   ❌ Błąd: {e}")
    
    print("\n2. 🗺️ Generowanie interaktywnej mapy...")
    try:
        map_file = save_interactive_map()
        visualizations.append(("Interactive Map", map_file))
        print("   ✅ Interaktywna mapa wygenerowana")
    except Exception as e:
        print(f"   ❌ Błąd: {e}")
    
    print("\n3. 📊 Generowanie dashboardu metryk...")
    try:
        dashboard_file = save_dashboard()
        visualizations.append(("Analytics Dashboard", dashboard_file))
        print("   ✅ Dashboard metryk wygenerowany")
    except Exception as e:
        print(f"   ❌ Błąd: {e}")
    
    # Generowanie master index
    print("\n4. 🏠 Generowanie strony głównej...")
    try:
        index_file = generate_master_index(visualizations, stats, init_result)
        visualizations.append(("Master Index", index_file))
        print("   ✅ Strona główna wygenerowana")
    except Exception as e:
        print(f"   ❌ Błąd: {e}")
    
    # Podsumowanie
    print("\n" + "="*60)
    print("🎯 GENEROWANIE ZAKOŃCZONE!")
    print("="*60)
    print(f"📁 Wygenerowano {len(visualizations)} wizualizacji:")
    
    for i, (name, file_path) in enumerate(visualizations, 1):
        print(f"   {i}. {name}")
        print(f"      📄 {file_path}")
        print()
    
    if visualizations:
        print("🚀 Aby zobaczyć wizualizacje:")
        print("   • Otwórz pliki HTML w przeglądarce")
        print("   • Zacznij od 'Master Index' - zawiera linki do wszystkich")
        print("   • Każda wizualizacja ma inne funkcje i perspektywy")
        print()
        print("🎮 Funkcje wizualizacji:")
        print("   • System Visualization: Przegląd architektury")
        print("   • Interactive Map: Interaktywna mapa route")
        print("   • Analytics Dashboard: Metryki i wykresy")
        print("   • Master Index: Centrum kontroli")
    
    return visualizations

def generate_master_index(visualizations, stats, init_result):
    """
    Generuje stronę główną z linkami do wszystkich wizualizacji
    """
    all_routes = get_all_routes()
    
    # Przykładowe route do demonstracji
    demo_routes = [
        ("system/resources/monitor@v2", "Monitorowanie zasobów systemowych"),
        ("system/bootstrap/env@v2", "Bootstrap środowiska"),
        ("api/routing/stats@v1", "Statystyki routingu"),
        ("system/routing/discover@v1", "Auto-discovery modułów")
    ]
    
    html = f"""
<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LuxCore - Master Control Center</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 40px 20px;
        }}
        .header {{
            text-align: center;
            background: rgba(255, 255, 255, 0.95);
            padding: 50px 30px;
            border-radius: 25px;
            margin-bottom: 40px;
            box-shadow: 0 25px 50px rgba(0,0,0,0.1);
        }}
        .logo {{
            font-size: 4em;
            margin-bottom: 20px;
        }}
        .title {{
            font-size: 3em;
            font-weight: bold;
            background: linear-gradient(45deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 15px;
        }}
        .subtitle {{
            color: #7f8c8d;
            font-size: 1.3em;
            margin-bottom: 30px;
        }}
        .status-badge {{
            display: inline-block;
            background: linear-gradient(45deg, #2ecc71, #27ae60);
            color: white;
            padding: 12px 25px;
            border-radius: 25px;
            font-weight: bold;
            margin: 0 10px;
            animation: pulse 2s infinite;
        }}
        @keyframes pulse {{
            0% {{ transform: scale(1); }}
            50% {{ transform: scale(1.05); }}
            100% {{ transform: scale(1); }}
        }}
        .stats-showcase {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        .stat-card {{
            background: rgba(255, 255, 255, 0.95);
            padding: 30px;
            border-radius: 20px;
            text-align: center;
            box-shadow: 0 15px 30px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }}
        .stat-card:hover {{
            transform: translateY(-10px);
        }}
        .stat-icon {{
            font-size: 2.5em;
            margin-bottom: 15px;
        }}
        .stat-number {{
            font-size: 2.5em;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 10px;
        }}
        .stat-label {{
            color: #7f8c8d;
            font-size: 1.1em;
        }}
        .visualizations-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 30px;
            margin-bottom: 40px;
        }}
        .viz-card {{
            background: rgba(255, 255, 255, 0.95);
            padding: 30px;
            border-radius: 20px;
            box-shadow: 0 15px 30px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }}
        .viz-card:hover {{
            transform: translateY(-5px);
        }}
        .viz-icon {{
            font-size: 3em;
            margin-bottom: 20px;
            text-align: center;
        }}
        .viz-title {{
            font-size: 1.5em;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 15px;
        }}
        .viz-description {{
            color: #7f8c8d;
            margin-bottom: 20px;
            line-height: 1.6;
        }}
        .viz-button {{
            display: inline-block;
            background: linear-gradient(45deg, #3498db, #2980b9);
            color: white;
            padding: 12px 25px;
            border-radius: 25px;
            text-decoration: none;
            font-weight: bold;
            transition: all 0.3s ease;
        }}
        .viz-button:hover {{
            background: linear-gradient(45deg, #2980b9, #3498db);
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }}
        .demo-section {{
            background: rgba(255, 255, 255, 0.95);
            padding: 30px;
            border-radius: 20px;
            margin-bottom: 40px;
            box-shadow: 0 15px 30px rgba(0,0,0,0.1);
        }}
        .demo-title {{
            font-size: 1.8em;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 20px;
            text-align: center;
        }}
        .demo-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }}
        .demo-item {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            border-left: 4px solid #3498db;
        }}
        .demo-route {{
            font-family: 'Courier New', monospace;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 8px;
        }}
        .demo-desc {{
            color: #7f8c8d;
            font-size: 0.9em;
        }}
        .footer {{
            text-align: center;
            color: white;
            padding: 30px;
            background: rgba(0, 0, 0, 0.2);
            border-radius: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">🌟</div>
            <div class="title">LuxCore</div>
            <div class="subtitle">Master Control Center</div>
            <div class="status-badge">🔴 SYSTEM ONLINE</div>
            <div class="status-badge">⚡ v2.0.0 ACTIVE</div>
        </div>
        
        <div class="stats-showcase">
            <div class="stat-card">
                <div class="stat-icon">🚀</div>
                <div class="stat-number">{stats['total_routes']}</div>
                <div class="stat-label">Total Routes</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">📊</div>
                <div class="stat-number">{stats['static_routes']}</div>
                <div class="stat-label">Static Routes</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">⚡</div>
                <div class="stat-number">{stats['dynamic_routes']}</div>
                <div class="stat-label">Dynamic Routes</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">📦</div>
                <div class="stat-number">{len(init_result['discovery']['discovered_modules'])}</div>
                <div class="stat-label">Loaded Modules</div>
            </div>
        </div>
        
        <div class="visualizations-grid">
            <div class="viz-card">
                <div class="viz-icon">🏗️</div>
                <div class="viz-title">System Architecture</div>
                <div class="viz-description">
                    Kompletny przegląd architektury systemu z mapą wszystkich route, 
                    kategorii i zależności. Idealny do zrozumienia struktury systemu.
                </div>
                <a href="luxcore_system_visualization.html" class="viz-button">
                    📋 Otwórz Wizualizację
                </a>
            </div>
            
            <div class="viz-card">
                <div class="viz-icon">🗺️</div>
                <div class="viz-title">Interactive Map</div>
                <div class="viz-description">
                    Interaktywna mapa sieci route z możliwością filtrowania, 
                    eksploracji połączeń i eksportu. Używa vis.js do wizualizacji.
                </div>
                <a href="luxcore_interactive_map.html" class="viz-button">
                    🌐 Otwórz Mapę
                </a>
            </div>
            
            <div class="viz-card">
                <div class="viz-icon">📊</div>
                <div class="viz-title">Analytics Dashboard</div>
                <div class="viz-description">
                    Dashboard z wykresami, metrykami i live monitoringiem. 
                    Zawiera wykresy Chart.js i analizę wydajności systemu.
                </div>
                <a href="luxcore_dashboard.html" class="viz-button">
                    📈 Otwórz Dashboard
                </a>
            </div>
        </div>
        
        <div class="demo-section">
            <div class="demo-title">🎮 Przykładowe Route do Testowania</div>
            <div class="demo-grid">
    """
    
    for route, description in demo_routes:
        html += f"""
                <div class="demo-item">
                    <div class="demo-route">{route}</div>
                    <div class="demo-desc">{description}</div>
                </div>
        """
    
    html += f"""
            </div>
        </div>
        
        <div class="footer">
            <p>🚀 <strong>LuxCore System v2.0.0</strong></p>
            <p>Dynamiczny system routingu z auto-discovery</p>
            <p>📊 {stats['total_routes']} route aktywnych | 
               🔄 {len(init_result['discovery']['discovered_modules'])} modułów | 
               ⚡ System operacyjny</p>
        </div>
    </div>
</body>
</html>
    """
    
    output_file = '/var/home/oriom/Dokumenty/Federacja/luxdb/luxcore_master_index.html'
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    return output_file

if __name__ == "__main__":
    visualizations = generate_all_visualizations()
    
    if visualizations:
        print("🎯 Zalecane pliki do otwarcia:")
        print("   1. luxcore_master_index.html - START HERE! 🏠")
        print("   2. luxcore_dashboard.html - Metryki i wykresy 📊")
        print("   3. luxcore_interactive_map.html - Interaktywna mapa 🗺️")
        print("   4. luxcore_system_visualization.html - Architektura 🏗️")
        print()
        print("✨ Ciesz się wizualizacją systemu LuxCore!")
    else:
        print("❌ Nie udało się wygenerować żadnych wizualizacji.")
