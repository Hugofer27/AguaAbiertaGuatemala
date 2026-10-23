import os
import json
import base64

base_dir = "D:/Documentos D/BaseDatosGT H2O/Investigación Antigravity"
bundle_path = os.path.join(base_dir, "data/processed/dashboard_data_bundle.json")

with open(bundle_path, 'r', encoding='utf-8') as f:
    bundle_data = json.load(f)

# Serialize to string
bundle_json_str = json.dumps(bundle_data, ensure_ascii=False)

html_code = f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>RÍOS ABIERTOS GT — Data Dashboard & Interactive Watershed Map</title>
  
  <!-- Leaflet CSS -->
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=" crossorigin=""/>
  
  <!-- Fonts -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">

  <style>
    :root {{
      --bg-dark: #080c14;
      --sidebar-bg: #0b111e;
      --panel-bg: rgba(14, 21, 37, 0.88);
      --card-bg: rgba(18, 27, 46, 0.75);
      --card-hover: rgba(26, 38, 64, 0.95);
      --border-color: rgba(56, 189, 248, 0.18);
      --border-glow: rgba(56, 189, 248, 0.45);
      
      --accent-blue: #38bdf8;
      --accent-cyan: #06b6d4;
      --accent-teal: #14b8a6;
      --accent-emerald: #10b981;
      --accent-amber: #f59e0b;
      --accent-rose: #f43f5e;
      --accent-purple: #a855f7;
      
      --text-main: #f8fafc;
      --text-muted: #94a3b8;
      --text-dim: #64748b;
      
      --shadow-sm: 0 4px 12px rgba(0, 0, 0, 0.4);
      --shadow-lg: 0 16px 36px -10px rgba(0, 0, 0, 0.8);
    }}

    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}

    body {{
      font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background-color: var(--bg-dark);
      color: var(--text-main);
      overflow-x: hidden;
      height: 100vh;
      display: flex;
    }}

    /* Layout: Sidebar + Main Content */
    .app-layout {{
      display: flex;
      width: 100vw;
      height: 100vh;
      overflow: hidden;
    }}

    /* SIDEBAR */
    aside.sidebar {{
      width: 260px;
      min-width: 260px;
      background: var(--sidebar-bg);
      border-right: 1px solid var(--border-color);
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      z-index: 100;
      overflow-y: auto;
    }}

    .sidebar-header {{
      padding: 20px 18px 16px 18px;
      border-bottom: 1px solid rgba(255, 255, 255, 0.06);
    }}

    .brand {{
      display: flex;
      align-items: center;
      gap: 10px;
    }}

    .brand-logo {{
      width: 38px;
      height: 38px;
      background: linear-gradient(135deg, #0284c7, #0d9488);
      border-radius: 10px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 900;
      font-size: 1.1rem;
      color: #fff;
      box-shadow: 0 0 15px rgba(2, 132, 199, 0.5);
    }}

    .brand-text h2 {{
      font-size: 0.95rem;
      font-weight: 800;
      letter-spacing: -0.3px;
      color: #fff;
      line-height: 1.2;
    }}

    .brand-text span {{
      font-size: 0.7rem;
      color: var(--accent-blue);
      font-weight: 600;
      letter-spacing: 0.5px;
      text-transform: uppercase;
    }}

    .sidebar-search {{
      margin: 14px 16px 8px 16px;
      position: relative;
    }}

    .sidebar-search input {{
      width: 100%;
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-radius: 8px;
      padding: 8px 12px 8px 32px;
      font-size: 0.8rem;
      color: #fff;
      outline: none;
      transition: all 0.2s;
    }}

    .sidebar-search input:focus {{
      border-color: var(--accent-blue);
      background: rgba(255, 255, 255, 0.08);
      box-shadow: 0 0 8px rgba(56, 189, 248, 0.3);
    }}

    .sidebar-search svg {{
      position: absolute;
      left: 10px;
      top: 9px;
      width: 14px;
      height: 14px;
      fill: var(--text-dim);
    }}

    .sidebar-nav {{
      padding: 10px 12px;
      flex: 1;
    }}

    .nav-group-title {{
      font-size: 0.65rem;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 1.2px;
      color: var(--text-dim);
      padding: 12px 8px 4px 8px;
    }}

    .nav-item {{
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 8px 12px;
      border-radius: 8px;
      color: var(--text-muted);
      text-decoration: none;
      font-size: 0.82rem;
      font-weight: 600;
      transition: all 0.15s;
      margin-bottom: 2px;
      cursor: pointer;
    }}

    .nav-item svg {{
      width: 16px;
      height: 16px;
      fill: currentColor;
    }}

    .nav-item:hover {{
      background: rgba(255, 255, 255, 0.05);
      color: #fff;
    }}

    .nav-item.active {{
      background: rgba(56, 189, 248, 0.12);
      color: var(--accent-blue);
      border: 1px solid rgba(56, 189, 248, 0.25);
    }}

    .sidebar-footer {{
      padding: 14px 16px;
      border-top: 1px solid rgba(255, 255, 255, 0.06);
      font-size: 0.72rem;
      color: var(--text-dim);
    }}

    .live-indicator {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      color: var(--accent-emerald);
      font-weight: 700;
      font-size: 0.7rem;
      margin-bottom: 4px;
    }}

    .live-dot {{
      width: 8px;
      height: 8px;
      background: var(--accent-emerald);
      border-radius: 50%;
      box-shadow: 0 0 8px var(--accent-emerald);
      animation: pulse 1.8s infinite;
    }}

    @keyframes pulse {{
      0% {{ opacity: 0.5; transform: scale(0.9); }}
      50% {{ opacity: 1; transform: scale(1.2); }}
      100% {{ opacity: 0.5; transform: scale(0.9); }}
    }}

    /* MAIN VIEW */
    main.main-content {{
      flex: 1;
      height: 100vh;
      display: flex;
      flex-direction: column;
      overflow-y: auto;
      background: radial-gradient(circle at 50% 20%, #0d1527 0%, var(--bg-dark) 100%);
    }}

    /* Top Dashboard Header */
    .dashboard-header {{
      padding: 18px 24px;
      border-bottom: 1px solid var(--border-color);
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
      align-items: center;
      gap: 16px;
      background: rgba(11, 17, 30, 0.75);
      backdrop-filter: blur(12px);
      -webkit-backdrop-filter: blur(12px);
    }}

    .dash-titles h1 {{
      font-size: 1.35rem;
      font-weight: 900;
      letter-spacing: -0.5px;
      color: #fff;
      display: flex;
      align-items: center;
      gap: 10px;
    }}

    .dash-titles h1 span.tag-cat {{
      background: linear-gradient(135deg, #0ea5e9, #14b8a6);
      padding: 3px 8px;
      border-radius: 6px;
      font-size: 0.7rem;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }}

    .dash-sub {{
      font-size: 0.8rem;
      color: var(--text-muted);
      margin-top: 2px;
    }}

    /* Stat Pills */
    .stat-pills {{
      display: flex;
      align-items: center;
      gap: 8px;
      flex-wrap: wrap;
    }}

    .pill {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 5px 12px;
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-radius: 20px;
      font-size: 0.75rem;
      font-weight: 700;
      color: #e2e8f0;
    }}

    .pill-accent {{
      background: rgba(56, 189, 248, 0.12);
      border-color: rgba(56, 189, 248, 0.35);
      color: var(--accent-blue);
    }}

    .pill-live {{
      background: rgba(16, 185, 129, 0.12);
      border-color: rgba(16, 185, 129, 0.35);
      color: var(--accent-emerald);
    }}

    /* Notice Banner */
    .data-banner {{
      margin: 16px 24px 0 24px;
      padding: 10px 16px;
      background: rgba(6, 182, 212, 0.08);
      border: 1px solid rgba(6, 182, 212, 0.25);
      border-radius: 10px;
      font-size: 0.78rem;
      color: #93c5fd;
      line-height: 1.5;
    }}

    .data-banner strong {{
      color: #38bdf8;
    }}

    /* MAP CONTAINER SECTION */
    .map-section {{
      padding: 16px 24px;
      flex: 1;
      display: flex;
      flex-direction: column;
      min-height: 540px;
    }}

    .map-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 10px;
    }}

    .map-title h3 {{
      font-size: 1.05rem;
      font-weight: 800;
      color: #fff;
    }}

    .map-title span {{
      font-size: 0.78rem;
      color: var(--text-muted);
    }}

    .map-wrapper {{
      flex: 1;
      min-height: 480px;
      background: #000;
      border: 1px solid var(--border-color);
      border-radius: 14px;
      position: relative;
      overflow: hidden;
      box-shadow: var(--shadow-lg);
    }}

    #map {{
      width: 100%;
      height: 100%;
      background: #060911;
    }}

    /* Custom Map Legend Bar (Overlaid at bottom of map) */
    .map-legend-bar {{
      position: absolute;
      bottom: 14px;
      left: 14px;
      z-index: 1000;
      background: rgba(11, 17, 30, 0.92);
      backdrop-filter: blur(8px);
      -webkit-backdrop-filter: blur(8px);
      border: 1px solid rgba(255, 255, 255, 0.12);
      border-radius: 30px;
      padding: 6px 16px;
      display: flex;
      align-items: center;
      gap: 16px;
      box-shadow: 0 4px 20px rgba(0, 0, 0, 0.6);
      font-size: 0.75rem;
      font-weight: 700;
    }}

    .legend-item {{
      display: flex;
      align-items: center;
      gap: 6px;
      color: #cbd5e1;
    }}

    .legend-dot {{
      width: 10px;
      height: 10px;
      border-radius: 50%;
    }}

    /* Floating Layer Controller on Map (Top Right) */
    .map-layers-control {{
      position: absolute;
      top: 14px;
      right: 14px;
      z-index: 1000;
      background: rgba(11, 17, 30, 0.92);
      backdrop-filter: blur(10px);
      -webkit-backdrop-filter: blur(10px);
      border: 1px solid rgba(56, 189, 248, 0.3);
      border-radius: 12px;
      padding: 12px 14px;
      width: 250px;
      box-shadow: 0 8px 24px rgba(0,0,0,0.7);
    }}

    .layers-title {{
      font-size: 0.75rem;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0.8px;
      color: var(--accent-blue);
      margin-bottom: 8px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}

    .layer-row {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 5px 0;
      font-size: 0.78rem;
      color: #e2e8f0;
      cursor: pointer;
    }}

    .layer-row label {{
      display: flex;
      align-items: center;
      gap: 8px;
      cursor: pointer;
    }}

    .layer-row input[type="checkbox"] {{
      accent-color: var(--accent-blue);
      cursor: pointer;
    }}

    /* BOTTOM FEATURE CARDS (THE 4 CARDS SHOWN IN REFERENCE) */
    .bottom-cards-section {{
      padding: 10px 24px 30px 24px;
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
      gap: 16px;
    }}

    .feature-card {{
      background: var(--card-bg);
      border: 1px solid var(--border-color);
      border-radius: 14px;
      padding: 18px 20px;
      transition: all 0.25s ease;
      cursor: pointer;
      display: flex;
      flex-direction: column;
      gap: 8px;
      box-shadow: var(--shadow-sm);
      position: relative;
    }}

    .feature-card:hover {{
      background: var(--card-hover);
      border-color: var(--accent-blue);
      transform: translateY(-3px);
      box-shadow: 0 12px 28px -8px rgba(56, 189, 248, 0.25);
    }}

    .card-icon {{
      font-size: 1.5rem;
      margin-bottom: 2px;
      color: var(--accent-blue);
    }}

    .feature-card h4 {{
      font-size: 1.05rem;
      font-weight: 800;
      color: #fff;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }}

    .feature-card p {{
      font-size: 0.82rem;
      color: var(--text-muted);
      line-height: 1.45;
    }}

    .card-meta {{
      margin-top: 6px;
      font-size: 0.72rem;
      font-family: 'JetBrains Mono', monospace;
      color: var(--accent-teal);
      font-weight: 600;
    }}

    /* LEAFLET POPUP CUSTOMIZATION */
    .leaflet-popup-content-wrapper {{
      background: rgba(11, 17, 30, 0.95) !important;
      color: #fff !important;
      border: 1px solid var(--accent-blue) !important;
      border-radius: 12px !important;
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.8) !important;
      backdrop-filter: blur(12px) !important;
    }}

    .leaflet-popup-tip {{
      background: rgba(11, 17, 30, 0.95) !important;
      border: 1px solid var(--accent-blue) !important;
    }}

    .station-popup {{
      padding: 4px;
      font-size: 0.82rem;
      line-height: 1.4;
      min-width: 260px;
    }}

    .pop-tag {{
      display: inline-block;
      font-size: 0.65rem;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      padding: 2px 6px;
      border-radius: 4px;
      margin-bottom: 4px;
    }}

    .tag-usac {{ background: rgba(168, 85, 247, 0.25); color: #c084fc; border: 1px solid rgba(168, 85, 247, 0.4); }}
    .tag-insivumeh {{ background: rgba(16, 185, 129, 0.25); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.4); }}
    .tag-toc {{ background: rgba(245, 158, 11, 0.25); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.4); }}

    .pop-title {{
      font-size: 0.95rem;
      font-weight: 800;
      color: #fff;
      margin-bottom: 6px;
      border-bottom: 1px solid rgba(255, 255, 255, 0.1);
      padding-bottom: 4px;
    }}

    .pop-grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 6px;
      margin: 8px 0;
    }}

    .pop-stat {{
      background: rgba(255, 255, 255, 0.04);
      padding: 4px 6px;
      border-radius: 6px;
    }}

    .pop-stat .k {{
      font-size: 0.65rem;
      color: var(--text-muted);
      text-transform: uppercase;
    }}

    .pop-stat .v {{
      font-size: 0.85rem;
      font-weight: 700;
      color: #38bdf8;
      font-family: 'JetBrains Mono', monospace;
    }}

    /* SLIDE-OVER DETAIL DRAWER */
    #detail-drawer {{
      position: fixed;
      top: 0;
      right: -420px;
      width: 420px;
      height: 100vh;
      background: var(--sidebar-bg);
      border-left: 1px solid var(--border-color);
      box-shadow: -10px 0 30px rgba(0, 0, 0, 0.8);
      z-index: 2000;
      transition: right 0.3s cubic-bezier(0.16, 1, 0.3, 1);
      display: flex;
      flex-direction: column;
      padding: 24px;
      overflow-y: auto;
    }}

    #detail-drawer.open {{
      right: 0;
    }}

    .drawer-close {{
      align-self: flex-end;
      background: rgba(255, 255, 255, 0.08);
      border: none;
      color: #fff;
      padding: 6px 12px;
      border-radius: 6px;
      cursor: pointer;
      font-weight: 700;
      font-size: 0.8rem;
    }}

    .drawer-content h3 {{
      margin-top: 10px;
      font-size: 1.2rem;
      color: #fff;
    }}

    /* Responsive */
    @media (max-width: 900px) {{
      aside.sidebar {{
        display: none;
      }}
      .map-legend-bar {{
        flex-wrap: wrap;
        border-radius: 12px;
      }}
    }}
  </style>
</head>
<body>

  <div class="app-layout">
    
    <!-- SIDEBAR -->
    <aside class="sidebar">
      <div>
        <div class="sidebar-header">
          <div class="brand">
            <div class="brand-logo">GT</div>
            <div class="brand-text">
              <h2>RÍOS ABIERTOS GT</h2>
              <span>Observatorio Hídrico</span>
            </div>
          </div>
        </div>

        <div class="sidebar-search">
          <svg viewBox="0 0 24 24"><path d="M10 2a8 8 0 015.293 13.998l4.704 4.705a1 1 0 01-1.414 1.414l-4.705-4.704A8 8 0 1110 2zm0 2a6 6 0 100 12 6 6 0 000-12z"/></svg>
          <input type="text" id="station-search" placeholder="Buscar río o estación..." onkeyup="searchStations(this.value)">
        </div>

        <nav class="sidebar-nav">
          <div class="nav-group-title">OVERVIEW</div>
          <div class="nav-item active" onclick="switchView('map')">
            <svg viewBox="0 0 24 24"><path d="M3 13h8V3H3v10zm0 8h8v-6H3v6zm10 0h8V11h-8v10zm0-18v6h8V3h-8z"/></svg>
            Dashboard Principal
          </div>
          <div class="nav-item" onclick="zoomToMotagua()">
            <svg viewBox="0 0 24 24"><path d="M20.5 3l-.16.03L15 5.1 9 3 3.36 4.9c-.21.07-.36.25-.36.48V20.5c0 .28.22.5.5.5l.16-.03L9 18.9l6 2.1 5.64-1.9c.21-.07.36-.25.36-.48V3.5c0-.28-.22-.5-.5-.5zM15 19l-6-2.11V5l6 2.11V19z"/></svg>
            Interactive Map
          </div>

          <div class="nav-group-title">MONITORING</div>
          <div class="nav-item" onclick="filterMapLayer('usac')">
            <svg viewBox="0 0 24 24"><path d="M19.5 21a3 3 0 003-3v-4.5a3 3 0 00-3-3h-1.5V6a3 3 0 00-3-3h-6a3 3 0 00-3 3v4.5H4.5a3 3 0 00-3 3V18a3 3 0 003 3h15zM12 5a1 1 0 011 1v4.5H11V6a1 1 0 011-1z"/></svg>
            Calidad del Agua & Fármacos
          </div>
          <div class="nav-item" onclick="filterMapLayer('insivumeh')">
            <svg viewBox="0 0 24 24"><path d="M12 2a10 10 0 100 20 10 10 0 000-20zm1 14.93V18a1 1 0 11-2 0v-1.07A7.002 7.002 0 015.07 11H4a1 1 0 110-2h1.07A7.002 7.002 0 0111 3.07V2a1 1 0 112 0v1.07A7.002 7.002 0 0118.93 9H20a1 1 0 110 2h-1.07A7.002 7.002 0 0113 16.93zM12 7a5 5 0 100 10 5 5 0 000-10z"/></svg>
            Hidrología & Caudales
          </div>
          <div class="nav-item" onclick="filterMapLayer('toc')">
            <svg viewBox="0 0 24 24"><path d="M19 4h-3.5l-1-1h-5l-1 1H5v2h14M6 19a2 2 0 002 2h8a2 2 0 002-2V7H6v12z"/></svg>
            Plásticos Fluviales (TOC)
          </div>
          <div class="nav-item" onclick="filterMapLayer('motagua')">
            <svg viewBox="0 0 24 24"><path d="M4 11a1 1 0 011 1 7 7 0 007 7 1 1 0 010 2 9 9 0 01-9-9 1 1 0 011-1zm0-4a1 1 0 011 1 11 11 0 0011 11 1 1 0 010 2 13 13 0 01-13-13 1 1 0 011-1zm0-4a1 1 0 011 1 15 15 0 0015 15 1 1 0 010 2 17 17 0 01-17-17 1 1 0 011-1z"/></svg>
            Red Fluvial Motagua (1,626)
          </div>

          <div class="nav-group-title">RESEARCH & OPEN DATA</div>
          <div class="nav-item" onclick="openDrawer('USAC ERIS', 'Tesis M.Sc. Paque López & Cáceres Sobalvarro (2025). Monitoreo de DBO5, DQO y 15 contaminantes emergentes farmacéuticos en la cuenca del Río Motagua y descargas hospitalarias mediante HPLC-MS/MS.')">
            <svg viewBox="0 0 24 24"><path d="M12 3L1 9l11 6 9-4.91V17h2V9L12 3zM3.45 9L12 4.33 20.55 9 12 13.67 3.45 9zM5 13.18v4L12 21l7-3.82v-4L12 17l-7-3.82z"/></svg>
            Tesis USAC ERIS 2025
          </div>
          <div class="nav-item" onclick="downloadMasterInventory()">
            <svg viewBox="0 0 24 24"><path d="M19.35 10.04C18.67 6.59 15.64 4 12 4 9.11 4 6.6 5.64 5.35 8.04 2.34 8.36 0 10.91 0 14c0 3.31 2.69 6 6 6h13c2.76 0 5-2.24 5-5 0-2.64-2.05-4.78-4.65-4.96zM17 13l-5 5-5-5h3V9h4v4h3z"/></svg>
            Descargar Inventario (CSV)
          </div>
        </nav>
      </div>

      <div class="sidebar-footer">
        <div class="live-indicator">
          <div class="live-dot"></div>
          <span>INSIVUMEH SENSOR LIVE</span>
        </div>
        <div>Boletines: 20/10/2026 20:00</div>
        <div style="margin-top: 4px; font-family: 'JetBrains Mono', monospace;">Antigravity Engine v2.0</div>
      </div>
    </aside>

    <!-- MAIN CONTENT -->
    <main class="main-content">
      
      <!-- Top Bar Header -->
      <div class="dashboard-header">
        <div class="dash-titles">
          <h1>
            RÍOS ABIERTOS GT <span style="font-weight: 400; color: #94a3b8;">Data Dashboard</span>
            <span class="tag-cat">Guatemala</span>
          </h1>
          <div class="dash-sub">Cuenca del Río Motagua, Río Las Vacas & Red Hidrológica Nacional</div>
        </div>

        <div class="stat-pills">
          <div class="pill pill-live">
            <span style="display:inline-block; width:6px; height:6px; background:#10b981; border-radius:50%;"></span>
            8 Estaciones Tiempo Real (INSIVUMEH)
          </div>
          <div class="pill pill-accent">
            📍 32 Estaciones Calidad USAC
          </div>
          <div class="pill">
            🌊 1,626 Tramos Motagua (HydroRIVERS)
          </div>
          <div class="pill">
            🗑️ 140 Desembocaduras TOC
          </div>
        </div>
      </div>

      <!-- Alert Data Notice -->
      <div class="data-banner">
        <strong>Fuentes de datos oficiales integradas en este mapa:</strong> INSIVUMEH (Boletín Hidrológico Caribe No. 880 año 2026 con aforos de Panajax y Gualán), USAC Escuela Regional de Ingeniería Sanitaria ERIS (Tesis 2025 HPLC-MS/MS de contaminantes farmacéuticos), The Ocean Cleanup (modelo global de macroplásticos e Interceptor 006) y USGS/WWF HydroRIVERS.
      </div>

      <!-- MAP SECTION -->
      <div class="map-section">
        <div class="map-header">
          <div class="map-title">
            <h3>Interactive Watershed Map</h3>
            <span>Río Motagua, Río Las Vacas, tributarios y estaciones de monitoreo — control interactivo de capas</span>
          </div>
          <div>
            <span style="font-size: 0.75rem; color: var(--accent-blue); font-weight: 700; cursor: pointer;" onclick="resetMapView()">↺ Centrar Cuenca Motagua</span>
          </div>
        </div>

        <div class="map-wrapper">
          <div id="map"></div>

          <!-- Floating Layer Controller -->
          <div class="map-layers-control">
            <div class="layers-title">
              <span>Capas Activas</span>
              <span style="font-size: 0.65rem; color: var(--text-dim);">SIG / WGS84</span>
            </div>
            <div class="layer-row">
              <label><input type="checkbox" id="chk-motagua" checked onchange="toggleLayer('motagua')"> Red Fluvial Motagua</label>
              <span style="color:#38bdf8; font-weight:800;">1,626</span>
            </div>
            <div class="layer-row">
              <label><input type="checkbox" id="chk-usac" checked onchange="toggleLayer('usac')"> Calidad & Fármacos USAC</label>
              <span style="color:#c084fc; font-weight:800;">32</span>
            </div>
            <div class="layer-row">
              <label><input type="checkbox" id="chk-insivumeh" checked onchange="toggleLayer('insivumeh')"> Aforos Tiempo Real INSIVUMEH</label>
              <span style="color:#34d399; font-weight:800;">8</span>
            </div>
            <div class="layer-row">
              <label><input type="checkbox" id="chk-toc" checked onchange="toggleLayer('toc')"> The Ocean Cleanup / Barreras</label>
              <span style="color:#fbbf24; font-weight:800;">3</span>
            </div>
          </div>

          <!-- Bottom Legend Bar Overlay (like in screenshot) -->
          <div class="map-legend-bar">
            <div class="legend-item">
              <div class="legend-dot" style="background: #38bdf8; box-shadow: 0 0 8px #38bdf8;"></div>
              <span>Río Motagua (Caudal Modelado)</span>
            </div>
            <div class="legend-item">
              <div class="legend-dot" style="background: #c084fc; box-shadow: 0 0 8px #c084fc;"></div>
              <span>32 Puntos Calidad USAC ERIS</span>
            </div>
            <div class="legend-item">
              <div class="legend-dot" style="background: #34d399; box-shadow: 0 0 8px #34d399;"></div>
              <span>Tiempo Real INSIVUMEH</span>
            </div>
            <div class="legend-item">
              <div class="legend-dot" style="background: #fbbf24; box-shadow: 0 0 8px #fbbf24;"></div>
              <span>The Ocean Cleanup</span>
            </div>
          </div>
        </div>
      </div>

      <!-- BOTTOM 4 FEATURE CARDS (EXACT MATCH TO REFERENCE IMAGE) -->
      <div class="bottom-cards-section">
        
        <div class="feature-card" onclick="zoomToLasVacas()">
          <div class="card-icon">🗺️</div>
          <h4>Mapa interactivo <span>→</span></h4>
          <p>Ríos, estaciones y puntos de muestreo en alta resolución. Explora la red de drenaje desde Ciudad de Guatemala hasta el Golfo de Honduras.</p>
          <div class="card-meta">1,626 tramos vectorizados | HydroRIVERS</div>
        </div>

        <div class="feature-card" onclick="openDrawer('Calidad del Agua & Fármacos', 'Resumen analítico de los parámetros muestreados en 32 puntos de la cuenca: Oxígeno Disuelto colapsado en Río Las Vacas (<1.5 mg/L), DBO5 de hasta 691 mg/L en alcantarillado, y presencia de sulfamidas (sulfadiazina, sulfametoxazol) y cafeína (>50,000 ng/L).')">
          <div class="card-icon">🧪</div>
          <h4>Calidad del agua <span>→</span></h4>
          <p>pH, conductividad, DBO, DQO y fármacos disponibles. Mediciones por HPLC-MS/MS en Las Vacas y descargas hospitalarias.</p>
          <div class="card-meta">32 estaciones | USAC ERIS 2025</div>
        </div>

        <div class="feature-card" onclick="openDrawer('Datos Históricos y Caudales', 'Series de niveles hidrométricos y caudales reportados por INSIVUMEH en el Boletín No. 880 (20/10/2026): Estación Gualán (Motagua) registrando 344.54 m³/s y Panajax (Las Vacas) con 10.56 m³/s. Base meteorológica de 64 estaciones.')">
          <div class="card-icon">📈</div>
          <h4>Datos históricos <span>→</span></h4>
          <p>Tendencias por fecha, sitio y fuente. Caudales diarios en vivo, niveles normales mínimos y alertas de crecidas (BHE).</p>
          <div class="card-meta">INSIVUMEH Boletín No. 880 | Octubre 2026</div>
        </div>

        <div class="feature-card" onclick="openDrawer('Transparencia y Participación', 'Guía y registro de datos faltantes para solicitar mediante la Ley de Acceso a la Información Pública (Decreto 57-2008) al MARN (SIGEGAR), EMPAGUA y MSPAS. Descarga de datos abiertos en CSV.')">
          <div class="card-icon">👥</div>
          <h4>Participación pública <span>→</span></h4>
          <p>Observaciones, peticiones Decreto 57-2008 y datos abiertos para la construcción colaborativa de RÍOS ABIERTOS GT.</p>
          <div class="card-meta">Transparencia Decreto 57-2008 | Datos Abiertos</div>
        </div>

      </div>

    </main>
  </div>

  <!-- SLIDE-OVER DETAIL DRAWER -->
  <div id="detail-drawer">
    <button class="drawer-close" onclick="closeDrawer()">✕ Cerrar</button>
    <div class="drawer-content" id="drawer-body">
      <h3>Detalle de la Estación</h3>
      <p>Selecciona una estación en el mapa para ver sus mediciones completas.</p>
    </div>
  </div>

  <!-- Leaflet JS -->
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=" crossorigin=""></script>

  <!-- Embedded GeoJSON & Stations Data -->
  <script>
    const DATA_BUNDLE = {bundle_json_str};

    let map;
    let motaguaLayerGroup;
    let usacLayerGroup;
    let insivumehLayerGroup;
    let tocLayerGroup;

    document.addEventListener("DOMContentLoaded", function() {{
      initMap();
    }});

    function initMap() {{
      // Center on Guatemala / Motagua basin
      map = L.map('map', {{
        center: [14.95, -89.95],
        zoom: 8.5,
        zoomControl: true,
        attributionControl: false
      }});

      // CartoDB Dark Matter Basemap (Matches reference image aesthetic perfectly!)
      L.tileLayer('https://{{s}}.basemaps.cartocdn.com/dark_all/{{z}}/{{x}}/{{y}}{{r}}.png', {{
        subdomains: 'abcd',
        maxZoom: 19
      }}).addTo(map);

      // Attribution small bottom right
      L.control.attribution({{position: 'bottomright', prefix: 'RÍOS ABIERTOS GT | HydroRIVERS | INSIVUMEH | USAC'}}).addTo(map);

      // 1. MOTAGUA RIVER REACHES LAYER
      motaguaLayerGroup = L.layerGroup();
      if (DATA_BUNDLE.motagua_river_network && DATA_BUNDLE.motagua_river_network.features) {{
        L.geoJSON(DATA_BUNDLE.motagua_river_network, {{
          style: function(feature) {{
            const strahler = feature.properties.strahler_order || 1;
            const q = feature.properties.dis_av_cms || 5;
            
            // Highlight mainstem and scale width by stream order
            let weight = 1.2;
            let color = '#0284c7';
            let opacity = 0.65;

            if (strahler >= 5 || q > 50) {{
              weight = 3.5;
              color = '#38bdf8'; // Glowing neon cyan
              opacity = 0.95;
            }} else if (strahler >= 3) {{
              weight = 2.0;
              color = '#0ea5e9';
              opacity = 0.8;
            }}

            return {{
              color: color,
              weight: weight,
              opacity: opacity,
              lineCap: 'round',
              lineJoin: 'round'
            }};
          }},
          onEachFeature: function(feature, layer) {{
            const p = feature.properties;
            layer.bindPopup(`
              <div class="station-popup">
                <span class="pop-tag" style="background:#0284c7; color:#fff;">Tramo Fluvial Motagua</span>
                <div class="pop-title">ID HydroRIVERS: ${{p.hyriv_id}}</div>
                <div class="pop-grid">
                  <div class="pop-stat"><span class="k">Orden Strahler</span><span class="v">${{p.strahler_order}}</span></div>
                  <div class="pop-stat"><span class="k">Caudal Modelado</span><span class="v">${{p.dis_av_cms}} m³/s</span></div>
                  <div class="pop-stat"><span class="k">Longitud</span><span class="v">${{p.length_km}} km</span></div>
                  <div class="pop-stat"><span class="k">Cuenca Aguas Arriba</span><span class="v">${{p.upland_skm.toLocaleString()}} km²</span></div>
                </div>
              </div>
            `);
          }}
        }}).addTo(motaguaLayerGroup);
      }}
      motaguaLayerGroup.addTo(map);

      // 2. USAC ERIS STATIONS LAYER (Calidad & Fármacos 2025)
      usacLayerGroup = L.layerGroup();
      if (DATA_BUNDLE.usac_quality_stations && DATA_BUNDLE.usac_quality_stations.features) {{
        DATA_BUNDLE.usac_quality_stations.features.forEach(feat => {{
          const p = feat.properties;
          const coords = [feat.geometry.coordinates[1], feat.geometry.coordinates[0]];
          
          let markerColor = '#a855f7'; // purple
          if (p.site_type.includes('Hospitalaria')) markerColor = '#ec4899'; // pink
          else if (p.site_type.includes('Superficial')) markerColor = '#38bdf8'; // cyan

          const marker = L.circleMarker(coords, {{
            radius: 7,
            fillColor: markerColor,
            color: '#ffffff',
            weight: 2,
            opacity: 1,
            fillOpacity: 0.85
          }});

          marker.bindPopup(`
            <div class="station-popup">
              <span class="pop-tag tag-usac">USAC ERIS 2025</span>
              <div class="pop-title">${{p.id}}: ${{p.name}}</div>
              <div style="font-size:0.75rem; color:#94a3b8; margin-bottom:4px;">${{p.site_type}} — ${{p.water_body}}</div>
              <div class="pop-grid">
                <div class="pop-stat"><span class="k">Oxígeno Disuelto</span><span class="v">${{p.od_mg_l !== null ? p.od_mg_l + ' mg/L' : 'ND'}}</span></div>
                <div class="pop-stat"><span class="k">DBO5</span><span class="v">${{p.dbo5_mg_l !== null ? p.dbo5_mg_l + ' mg/L' : 'ND'}}</span></div>
                <div class="pop-stat"><span class="k">DQO</span><span class="v">${{p.dqo_mg_l !== null ? p.dqo_mg_l + ' mg/L' : 'ND'}}</span></div>
                <div class="pop-stat"><span class="k">pH</span><span class="v">${{p.ph !== null ? p.ph : 'ND'}}</span></div>
                <div class="pop-stat"><span class="k">Sulfametoxazol</span><span class="v">${{p.sulfametoxazol_ng_l !== null ? p.sulfametoxazol_ng_l + ' ng/L' : 'ND'}}</span></div>
                <div class="pop-stat"><span class="k">Cafeína</span><span class="v">${{p.cafeina_ng_l !== null ? p.cafeina_ng_l.toLocaleString() + ' ng/L' : 'ND'}}</span></div>
              </div>
              <button onclick="openDrawerStation('${{p.id}}')" style="width:100%; margin-top:6px; background:linear-gradient(135deg,#0284c7,#0284c7); border:none; color:#fff; padding:6px; border-radius:6px; font-weight:700; cursor:pointer; font-size:0.75rem;">Ver Ficha Completa</button>
            </div>
          `);

          marker.addTo(usacLayerGroup);
        }});
      }}
      usacLayerGroup.addTo(map);

      // 3. INSIVUMEH REAL-TIME STATIONS LAYER
      insivumehLayerGroup = L.layerGroup();
      if (DATA_BUNDLE.insivumeh_realtime_stations && DATA_BUNDLE.insivumeh_realtime_stations.features) {{
        DATA_BUNDLE.insivumeh_realtime_stations.features.forEach(feat => {{
          const p = feat.properties;
          const coords = [feat.geometry.coordinates[1], feat.geometry.coordinates[0]];

          let col = '#10b981'; // green normal
          if (p.status.includes('Crecido')) col = '#f43f5e'; // red alert
          else if (p.status.includes('Bajo')) col = '#f59e0b'; // amber

          const marker = L.circleMarker(coords, {{
            radius: 9,
            fillColor: col,
            color: '#ffffff',
            weight: 2.5,
            opacity: 1,
            fillOpacity: 0.9
          }});

          marker.bindPopup(`
            <div class="station-popup">
              <span class="pop-tag tag-insivumeh">INSIVUMEH EN VIVO</span>
              <div class="pop-title">${{p.name}}</div>
              <div style="font-size:0.75rem; color:#cbd5e1; margin-bottom:4px;">${{p.location}} | ${{p.water_body}}</div>
              <div style="background:rgba(255,255,255,0.05); padding:4px 8px; border-radius:6px; font-size:0.75rem; margin-bottom:6px;">
                Estado: <strong>${{p.status}}</strong> (Boletín ${{p.date}})
              </div>
              <div class="pop-grid">
                <div class="pop-stat"><span class="k">Caudal Instantáneo</span><span class="v" style="color:${{col}}">${{p.discharge_cms !== null ? p.discharge_cms + ' m³/s' : 'N/A'}}</span></div>
                <div class="pop-stat"><span class="k">Nivel Actual</span><span class="v">${{p.level_m}} m</span></div>
                <div class="pop-stat"><span class="k">Caudal Normal Min</span><span class="v">${{p.normal_q_min || 'N/A'}} m³/s</span></div>
                <div class="pop-stat"><span class="k">Caudal Normal Max</span><span class="v">${{p.normal_q_max || 'N/A'}} m³/s</span></div>
              </div>
            </div>
          `);

          marker.addTo(insivumehLayerGroup);
        }});
      }}
      insivumehLayerGroup.addTo(map);

      // 4. THE OCEAN CLEANUP INFRASTRUCTURE LAYER
      tocLayerGroup = L.layerGroup();
      if (DATA_BUNDLE.ocean_cleanup_stations && DATA_BUNDLE.ocean_cleanup_stations.features) {{
        DATA_BUNDLE.ocean_cleanup_stations.features.forEach(feat => {{
          const p = feat.properties;
          const coords = [feat.geometry.coordinates[1], feat.geometry.coordinates[0]];

          const marker = L.circleMarker(coords, {{
            radius: 10,
            fillColor: '#f59e0b',
            color: '#fff',
            weight: 2.5,
            opacity: 1,
            fillOpacity: 0.95
          }});

          marker.bindPopup(`
            <div class="station-popup">
              <span class="pop-tag tag-toc">THE OCEAN CLEANUP</span>
              <div class="pop-title">${{p.name}}</div>
              <div style="font-size:0.75rem; color:#cbd5e1; margin-bottom:4px;">${{p.location}}</div>
              <div style="font-size:0.75rem; color:#94a3b8; margin-bottom:6px;">${{p.type}}</div>
              <div class="pop-grid">
                <div class="pop-stat" style="grid-column:span 2;"><span class="k">Métrica Principal</span><span class="v" style="color:#fbbf24">${{p.metrics}}</span></div>
                <div class="pop-stat" style="grid-column:span 2;"><span class="k">Objetivo Operativo</span><span class="v" style="font-size:0.75rem;">${{p.target}}</span></div>
              </div>
            </div>
          `);

          marker.addTo(tocLayerGroup);
        }});
      }}
      tocLayerGroup.addTo(map);
    }}

    // Layer Toggle Function
    function toggleLayer(layerKey) {{
      if (layerKey === 'motagua') {{
        const chk = document.getElementById('chk-motagua').checked;
        if (chk) map.addLayer(motaguaLayerGroup); else map.removeLayer(motaguaLayerGroup);
      }} else if (layerKey === 'usac') {{
        const chk = document.getElementById('chk-usac').checked;
        if (chk) map.addLayer(usacLayerGroup); else map.removeLayer(usacLayerGroup);
      }} else if (layerKey === 'insivumeh') {{
        const chk = document.getElementById('chk-insivumeh').checked;
        if (chk) map.addLayer(insivumehLayerGroup); else map.removeLayer(insivumehLayerGroup);
      }} else if (layerKey === 'toc') {{
        const chk = document.getElementById('chk-toc').checked;
        if (chk) map.addLayer(tocLayerGroup); else map.removeLayer(tocLayerGroup);
      }}
    }}

    function resetMapView() {{
      map.setView([14.95, -89.95], 8.5);
    }}

    function zoomToLasVacas() {{
      map.setView([14.68, -90.49], 12);
    }}

    function zoomToMotagua() {{
      map.setView([15.15, -89.45], 9.5);
    }}

    function filterMapLayer(layerName) {{
      if (layerName === 'usac') {{
        zoomToLasVacas();
      }} else if (layerName === 'insivumeh') {{
        map.setView([15.13, -89.36], 10); // Gualán
      }} else if (layerName === 'toc') {{
        map.setView([14.755, -90.50], 13); // Interceptor 006
      }} else if (layerName === 'motagua') {{
        resetMapView();
      }}
    }}

    // Detail Drawer Functions
    function openDrawer(title, desc) {{
      const drawer = document.getElementById('detail-drawer');
      const body = document.getElementById('drawer-body');
      body.innerHTML = `
        <h3 style="margin-top:10px; color:#fff;">${{title}}</h3>
        <p style="margin-top:12px; font-size:0.9rem; line-height:1.6; color:#cbd5e1;">${{desc}}</p>
        <div style="margin-top:20px; padding:16px; background:rgba(0,0,0,0.3); border-radius:10px; border:1px solid rgba(255,255,255,0.08);">
          <div style="font-size:0.75rem; text-transform:uppercase; color:var(--accent-blue); font-weight:800; margin-bottom:8px;">Archivos en tu Disco</div>
          <div style="font-size:0.8rem; font-family:'JetBrains Mono',monospace; color:#94a3b8; line-height:1.5;">
            • D:/Documentos D/BaseDatosGT H2O/Investigación Antigravity/data/processed/<br>
            • D:/Documentos D/BaseDatosGT H2O/Investigación Antigravity/inventories/
          </div>
        </div>
      `;
      drawer.classList.add('open');
    }}

    function openDrawerStation(stationId) {{
      const st = DATA_BUNDLE.usac_quality_stations.features.find(f => f.properties.id === stationId);
      if (!st) return;
      const p = st.properties;

      const drawer = document.getElementById('detail-drawer');
      const body = document.getElementById('drawer-body');
      body.innerHTML = `
        <span class="pop-tag tag-usac" style="margin-top:10px;">Estación USAC ERIS</span>
        <h3 style="color:#fff; margin-top:4px;">${{p.id}}: ${{p.name}}</h3>
        <p style="font-size:0.85rem; color:#94a3b8; margin-bottom:14px;">${{p.site_type}} — ${{p.water_body}}</p>
        
        <div style="display:grid; grid-template-columns:1fr 1fr; gap:8px; margin-bottom:16px;">
          <div class="pop-stat"><span class="k">Oxígeno Disuelto</span><span class="v" style="color:${{p.od_mg_l < 2 ? '#f43f5e' : '#38bdf8'}}">${{p.od_mg_l !== null ? p.od_mg_l + ' mg/L' : 'ND'}}</span></div>
          <div class="pop-stat"><span class="k">pH</span><span class="v">${{p.ph || 'ND'}}</span></div>
          <div class="pop-stat"><span class="k">DBO5</span><span class="v">${{p.dbo5_mg_l !== null ? p.dbo5_mg_l + ' mg/L' : 'ND'}}</span></div>
          <div class="pop-stat"><span class="k">DQO</span><span class="v">${{p.dqo_mg_l !== null ? p.dqo_mg_l + ' mg/L' : 'ND'}}</span></div>
        </div>

        <h4 style="font-size:0.85rem; color:var(--accent-purple); text-transform:uppercase; letter-spacing:0.8px; margin-bottom:8px;">Contaminantes Emergentes (HPLC-MS/MS)</h4>
        <div style="background:rgba(0,0,0,0.3); border-radius:8px; padding:10px; font-size:0.82rem; font-family:'JetBrains Mono',monospace;">
          <div style="display:flex; justify-content:space-between; padding:4px 0; border-bottom:1px solid rgba(255,255,255,0.05);">
            <span>Sulfadiazina:</span><span style="color:#c084fc;">${{p.sulfadiazina_ng_l !== null ? p.sulfadiazina_ng_l + ' ng/L' : 'ND'}}</span>
          </div>
          <div style="display:flex; justify-content:space-between; padding:4px 0; border-bottom:1px solid rgba(255,255,255,0.05);">
            <span>Sulfametoxazol:</span><span style="color:#c084fc;">${{p.sulfametoxazol_ng_l !== null ? p.sulfametoxazol_ng_l + ' ng/L' : 'ND'}}</span>
          </div>
          <div style="display:flex; justify-content:space-between; padding:4px 0;">
            <span>Cafeína:</span><span style="color:#c084fc;">${{p.cafeina_ng_l !== null ? p.cafeina_ng_l.toLocaleString() + ' ng/L' : 'ND'}}</span>
          </div>
        </div>

        <div style="margin-top:20px; font-size:0.78rem; color:#64748b;">
          <strong>Fuente:</strong> Tesis de Maestría en Ciencias en Ingeniería Sanitaria (ERIS-USAC), Paque López & Cáceres Sobalvarro, Mayo 2025.
        </div>
      `;
      drawer.classList.add('open');
    }}

    function closeDrawer() {{
      document.getElementById('detail-drawer').classList.remove('open');
    }}

    function searchStations(query) {{
      if (!query || query.length < 2) return;
      query = query.toLowerCase();

      // Search in USAC stations
      const match = DATA_BUNDLE.usac_quality_stations.features.find(f => 
        f.properties.name.toLowerCase().includes(query) ||
        f.properties.id.toLowerCase().includes(query) ||
        f.properties.water_body.toLowerCase().includes(query)
      );

      if (match) {{
        map.setView([match.geometry.coordinates[1], match.geometry.coordinates[0]], 14);
        return;
      }}

      // Search in INSIVUMEH stations
      const matchIns = DATA_BUNDLE.insivumeh_realtime_stations.features.find(f => 
        f.properties.name.toLowerCase().includes(query) ||
        f.properties.water_body.toLowerCase().includes(query)
      );

      if (matchIns) {{
        map.setView([matchIns.geometry.coordinates[1], matchIns.geometry.coordinates[0]], 13);
      }}
    }}

    function downloadMasterInventory() {{
      window.location.href = "file:///D:/Documentos%20D/BaseDatosGT%20H2O/Investigación%20Antigravity/inventories/master_data_inventory.csv";
    }}
  </script>
</body>
</html>
"""

out_html1 = os.path.join(base_dir, "mapa_interactivo_rios_abiertos.html")
out_html2 = os.path.join(base_dir, "report/mapa_interactivo_rios_abiertos.html")

with open(out_html1, 'w', encoding='utf-8') as f:
    f.write(html_code)

with open(out_html2, 'w', encoding='utf-8') as f:
    f.write(html_code)

print(f"Interactive Map Dashboard created successfully:\n  1. {out_html1}\n  2. {out_html2}")
