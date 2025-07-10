#!/usr/bin/env python3
"""
Interaktywna mapa systemu LuxCore z diagramami przepływu
"""
import sys
import os
import json
sys.path.insert(0, '/var/home/oriom/Dokumenty/Federacja/luxdb')

from lux_core.init import initialize_lux_core
from lux_core.routing import get_all_routes
from lux_core.auto_discovery import get_route_statistics

def generate_interactive_map():
    """
    Generuje interaktywną mapę systemu z diagramami
    """
    # Inicjalizacja i pobranie danych
    init_result = initialize_lux_core()
    all_routes = get_all_routes()
    stats = get_route_statistics()
    
    # Konwersja danych do formatu JSON-serializowalnego
    serializable_routes = {}
    for path, info in all_routes.items():
        serializable_routes[path] = {
            'type': info['type'],
            'metadata': info['metadata']
        }
    
    # Tworzenie struktury danych dla diagramu
    nodes = []
    edges = []
    
    # Kategoryzacja
    categories = {
        'system': {'color': '#3498db', 'icon': '⚙️'},
        'api': {'color': '#e74c3c', 'icon': '🔌'},
        'custom': {'color': '#f39c12', 'icon': '✨'}
    }
    
    # Tworzenie węzłów
    for path, info in all_routes.items():
        parts = path.split('/')
        category = parts[0] if parts else 'unknown'
        
        node_color = categories.get(category, {'color': '#95a5a6'})['color']
        node_icon = categories.get(category, {'icon': '📁'})['icon']
        
        nodes.append({
            'id': path,
            'label': f"{node_icon} {path.split('/')[-1]}",
            'title': f"<b>{path}</b><br>Type: {info['type']}<br>Description: {info['metadata'].get('description', 'N/A')}",
            'color': node_color,
            'group': category,
            'type': info['type']
        })
    
    # Tworzenie połączeń (przykładowe - na podstawie kategorii)
    for i, route1 in enumerate(all_routes.keys()):
        for j, route2 in enumerate(all_routes.keys()):
            if i < j:
                parts1 = route1.split('/')
                parts2 = route2.split('/')
                
                # Połącz jeśli mają wspólną kategorię i podkategorię
                if len(parts1) >= 2 and len(parts2) >= 2:
                    if parts1[0] == parts2[0] and parts1[1] == parts2[1]:
                        edges.append({
                            'from': route1,
                            'to': route2,
                            'color': {'color': '#95a5a6', 'opacity': 0.3}
                        })
    
    html = f"""
<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LuxCore Interactive System Map</title>
    <script src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            height: 100vh;
            overflow: hidden;
        }}
        .container {{
            display: flex;
            height: 100vh;
        }}
        .sidebar {{
            width: 350px;
            background: rgba(255, 255, 255, 0.95);
            padding: 20px;
            overflow-y: auto;
            box-shadow: 2px 0 10px rgba(0,0,0,0.1);
        }}
        .main-content {{
            flex: 1;
            position: relative;
        }}
        #network {{
            width: 100%;
            height: 100%;
            background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        }}
        .controls {{
            position: absolute;
            top: 20px;
            right: 20px;
            z-index: 1000;
        }}
        .control-btn {{
            background: rgba(255, 255, 255, 0.9);
            border: none;
            padding: 10px 15px;
            margin: 5px;
            border-radius: 5px;
            cursor: pointer;
            font-weight: bold;
            transition: all 0.3s ease;
        }}
        .control-btn:hover {{
            background: white;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }}
        .title {{
            font-size: 1.8em;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 20px;
            text-align: center;
        }}
        .stats-box {{
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
        }}
        .stat-item {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 8px;
        }}
        .legend {{
            margin-top: 20px;
        }}
        .legend-title {{
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 10px;
        }}
        .legend-item {{
            display: flex;
            align-items: center;
            margin-bottom: 8px;
        }}
        .legend-color {{
            width: 16px;
            height: 16px;
            border-radius: 3px;
            margin-right: 10px;
        }}
        .route-list {{
            margin-top: 20px;
        }}
        .route-category {{
            margin-bottom: 15px;
        }}
        .route-category-title {{
            font-weight: bold;
            color: #2c3e50;
            padding: 8px;
            background: #ecf0f1;
            border-radius: 5px;
            margin-bottom: 5px;
        }}
        .route-item {{
            font-size: 0.9em;
            padding: 5px 10px;
            background: white;
            border-radius: 3px;
            margin-bottom: 3px;
            border-left: 3px solid #3498db;
        }}
        .route-item.dynamic {{
            border-left-color: #e74c3c;
        }}
        .filter-controls {{
            margin-top: 20px;
        }}
        .filter-btn {{
            background: #3498db;
            color: white;
            border: none;
            padding: 8px 12px;
            margin: 3px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 0.9em;
        }}
        .filter-btn.active {{
            background: #e74c3c;
        }}
        .info-panel {{
            position: absolute;
            bottom: 20px;
            left: 20px;
            background: rgba(255, 255, 255, 0.9);
            padding: 15px;
            border-radius: 10px;
            min-width: 200px;
            display: none;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="sidebar">
            <div class="title">🌟 LuxCore Map</div>
            
            <div class="stats-box">
                <div class="stat-item">
                    <span>Total Routes:</span>
                    <span><strong>{stats['total_routes']}</strong></span>
                </div>
                <div class="stat-item">
                    <span>Static:</span>
                    <span><strong>{stats['static_routes']}</strong></span>
                </div>
                <div class="stat-item">
                    <span>Dynamic:</span>
                    <span><strong>{stats['dynamic_routes']}</strong></span>
                </div>
                <div class="stat-item">
                    <span>Modules:</span>
                    <span><strong>{len(init_result['discovery']['discovered_modules'])}</strong></span>
                </div>
            </div>
            
            <div class="legend">
                <div class="legend-title">🎨 Kategorie</div>
                <div class="legend-item">
                    <div class="legend-color" style="background: #3498db;"></div>
                    <span>System Routes</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background: #e74c3c;"></div>
                    <span>API Routes</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background: #f39c12;"></div>
                    <span>Custom Routes</span>
                </div>
            </div>
            
            <div class="filter-controls">
                <div class="legend-title">🔍 Filtry</div>
                <button class="filter-btn active" onclick="filterNodes('all')">Wszystkie</button>
                <button class="filter-btn" onclick="filterNodes('system')">System</button>
                <button class="filter-btn" onclick="filterNodes('api')">API</button>
                <button class="filter-btn" onclick="filterNodes('static')">Statyczne</button>
                <button class="filter-btn" onclick="filterNodes('dynamic')">Dynamiczne</button>
            </div>
            
            <div class="route-list">
                <div class="legend-title">📋 Route List</div>
                <div id="routeList"></div>
            </div>
        </div>
        
        <div class="main-content">
            <div class="controls">
                <button class="control-btn" onclick="network.fit()">🔍 Fit All</button>
                <button class="control-btn" onclick="togglePhysics()">⚡ Physics</button>
                <button class="control-btn" onclick="exportNetwork()">💾 Export</button>
            </div>
            
            <div id="network"></div>
            
            <div class="info-panel" id="infoPanel">
                <div id="nodeInfo"></div>
            </div>
        </div>
    </div>
    
    <script>
        // Dane dla sieci
        const nodes = new vis.DataSet({json.dumps(nodes, indent=8)});
        const edges = new vis.DataSet({json.dumps(edges, indent=8)});
        
        // Konfiguracja sieci
        const options = {{
            nodes: {{
                shape: 'dot',
                size: 16,
                font: {{
                    size: 12,
                    color: '#2c3e50'
                }},
                borderWidth: 2,
                shadow: true
            }},
            edges: {{
                width: 1,
                color: {{inherit: 'from'}},
                smooth: {{
                    type: 'continuous'
                }}
            }},
            physics: {{
                enabled: true,
                barnesHut: {{
                    gravitationalConstant: -8000,
                    centralGravity: 0.3,
                    springLength: 95,
                    springConstant: 0.04,
                    damping: 0.09
                }}
            }},
            interaction: {{
                hover: true,
                hoverConnectedEdges: true,
                selectConnectedEdges: true
            }},
            layout: {{
                improvedLayout: true
            }}
        }};
        
        // Inicjalizacja sieci
        const container = document.getElementById('network');
        const data = {{
            nodes: nodes,
            edges: edges
        }};
        const network = new vis.Network(container, data, options);
        
        // Obsługa zdarzeń
        network.on('click', function (params) {{
            if (params.nodes.length > 0) {{
                const nodeId = params.nodes[0];
                const node = nodes.get(nodeId);
                showNodeInfo(node);
            }}
        }});
        
        network.on('hoverNode', function (params) {{
            const nodeId = params.node;
            const node = nodes.get(nodeId);
            showNodeInfo(node);
        }});
        
        network.on('blurNode', function (params) {{
            hideNodeInfo();
        }});
        
        // Funkcje pomocnicze
        function showNodeInfo(node) {{
            const infoPanel = document.getElementById('infoPanel');
            const nodeInfo = document.getElementById('nodeInfo');
            
            nodeInfo.innerHTML = `
                <h4>${{node.label}}</h4>
                <p><strong>Path:</strong> ${{node.id}}</p>
                <p><strong>Type:</strong> ${{node.type}}</p>
                <p><strong>Group:</strong> ${{node.group}}</p>
            `;
            
            infoPanel.style.display = 'block';
        }}
        
        function hideNodeInfo() {{
            const infoPanel = document.getElementById('infoPanel');
            infoPanel.style.display = 'none';
        }}
        
        function filterNodes(filterType) {{
            // Aktualizuj przyciski
            document.querySelectorAll('.filter-btn').forEach(btn => {{
                btn.classList.remove('active');
            }});
            event.target.classList.add('active');
            
            // Filtrowanie węzłów
            const allNodes = nodes.get();
            let filteredNodes;
            
            if (filterType === 'all') {{
                filteredNodes = allNodes;
            }} else if (filterType === 'static' || filterType === 'dynamic') {{
                filteredNodes = allNodes.filter(node => node.type === filterType);
            }} else {{
                filteredNodes = allNodes.filter(node => node.group === filterType);
            }}
            
            // Aktualizuj sieć
            const filteredNodeIds = filteredNodes.map(node => node.id);
            const filteredEdges = edges.get().filter(edge => 
                filteredNodeIds.includes(edge.from) && filteredNodeIds.includes(edge.to)
            );
            
            network.setData({{
                nodes: filteredNodes,
                edges: filteredEdges
            }});
        }}
        
        function togglePhysics() {{
            const physicsEnabled = network.physics.physicsEnabled;
            network.setOptions({{physics: {{enabled: !physicsEnabled}}}});
        }}
        
        function exportNetwork() {{
            const canvas = network.canvas.frame.canvas;
            const dataURL = canvas.toDataURL();
            const link = document.createElement('a');
            link.download = 'luxcore_network.png';
            link.href = dataURL;
            link.click();
        }}
        
        // Wypełnij listę route
        function populateRouteList() {{
            const routeList = document.getElementById('routeList');
            const routes = {json.dumps(list(all_routes.keys()))};
            const routeInfo = {json.dumps(serializable_routes)};
            
            const categories = {{}};
            routes.forEach(route => {{
                const parts = route.split('/');
                const category = parts[0] || 'unknown';
                if (!categories[category]) {{
                    categories[category] = [];
                }}
                categories[category].push(route);
            }});
            
            let html = '';
            Object.keys(categories).forEach(category => {{
                html += `<div class="route-category">`;
                html += `<div class="route-category-title">${{category.toUpperCase()}}</div>`;
                categories[category].forEach(route => {{
                    const routeData = routeInfo[route];
                    const routeClass = routeData.type === 'dynamic' ? 'dynamic' : '';
                    html += `<div class="route-item ${{routeClass}}">${{route}}</div>`;
                }});
                html += `</div>`;
            }});
            
            routeList.innerHTML = html;
        }}
        
        // Inicjalizacja
        populateRouteList();
    </script>
</body>
</html>
    """
    
    return html

def save_interactive_map():
    """
    Zapisuje interaktywną mapę do pliku HTML
    """
    html_content = generate_interactive_map()
    
    output_file = '/var/home/oriom/Dokumenty/Federacja/luxdb/luxcore_interactive_map.html'
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ Interaktywna mapa systemu zapisana w: {output_file}")
    print(f"🌐 Otwórz plik w przeglądarce aby zobaczyć interaktywną mapę!")
    
    return output_file

if __name__ == "__main__":
    print("🗺️ Generowanie interaktywnej mapy systemu LuxCore...")
    output_file = save_interactive_map()
    print(f"\n🎯 Gotowe! Interaktywna mapa dostępna w: {output_file}")
    print("🎮 Funkcje: kliknij węzły, filtruj kategorie, eksportuj jako PNG!")
