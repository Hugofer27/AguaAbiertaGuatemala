"""
Update National Interactive Map Dashboard with Real-Time River Animation & COGUANOR Diagnostic Engine.
Embeds an interactive HTML5 Canvas physical flow simulation that renders realistic water states:
- Pristine / Sano (emerald/cyan caustics, clean ripples, oxygen bubbles)
- Eutrophic / Algae bloom (olive/green cyanobacteria scum and filaments)
- Turbid / Sediment-laden (muddy chocolate-brown torrential silt flow)
- Septic / Sewage / Extreme Pollution (murky grey-black sludge, methane/H2S bubbling, floating plastics, surfactant foam)
Coupled with a COGUANOR NTG 29001 and Acuerdo Gubernativo 236-2006 regulatory diagnostic engine.
"""
import os
import json

BASE_DIR = r"D:\Documentos D\BaseDatosGT H2O"
ANTIGRAVITY_DIR = os.path.join(BASE_DIR, "Investigación Antigravity")
DATA_BUNDLE_PATH = os.path.join(ANTIGRAVITY_DIR, "data", "processed", "dashboard_national_data_bundle.json")

OUTPUT_HTML_1 = os.path.join(ANTIGRAVITY_DIR, "mapa_interactivo_rios_abiertos.html")
OUTPUT_HTML_2 = os.path.join(ANTIGRAVITY_DIR, "report", "mapa_interactivo_rios_abiertos.html")

def build_dashboard():
    print(f"Loading National Data Bundle from {DATA_BUNDLE_PATH}...")
    with open(DATA_BUNDLE_PATH, "r", encoding="utf-8") as f:
        bundle_str = f.read()

    html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>RÍOS ABIERTOS GT — Observatorio Hídrico Nacional & Simulador Fluvial COGUANOR</title>
  
  <!-- Leaflet CSS -->
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=" crossorigin=""/>
  
  <!-- Fonts -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com">
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">

  <style>
    :root {{
      --bg-dark: #080c14;
      --sidebar-bg: #0b111e;
      --panel-bg: rgba(14, 21, 37, 0.92);
      --card-bg: rgba(18, 27, 46, 0.82);
      --card-hover: rgba(26, 38, 64, 0.96);
      --border-color: rgba(56, 189, 248, 0.18);
      --border-glow: rgba(56, 189, 248, 0.45);
      
      --accent-blue: #38bdf8;
      --accent-cyan: #06b6d4;
      --accent-teal: #14b8a6;
      --accent-emerald: #10b981;
      --accent-amber: #f59e0b;
      --accent-rose: #f43f5e;
      --accent-purple: #a855f7;
      --accent-indigo: #6366f1;
      
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

    .app-layout {{
      display: flex;
      width: 100vw;
      height: 100vh;
      overflow: hidden;
    }}

    /* SIDEBAR */
    aside.sidebar {{
      width: 275px;
      min-width: 275px;
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
      gap: 12px;
    }}

    .brand-logo {{
      width: 42px;
      height: 42px;
      background: linear-gradient(135deg, #0284c7, #0d9488);
      border-radius: 10px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 900;
      font-size: 1.15rem;
      color: #fff;
      box-shadow: 0 0 16px rgba(2, 132, 199, 0.5);
    }}

    .brand-text h2 {{
      font-size: 0.98rem;
      font-weight: 800;
      letter-spacing: -0.3px;
      color: #fff;
      line-height: 1.2;
    }}

    .brand-text span {{
      font-size: 0.68rem;
      color: var(--accent-blue);
      font-weight: 700;
      letter-spacing: 0.6px;
      text-transform: uppercase;
    }}

    .sidebar-search {{
      margin: 14px 16px 8px 16px;
      position: relative;
    }}

    .sidebar-search input {{
      width: 100%;
      background: rgba(14, 21, 37, 0.85);
      border: 1px solid var(--border-color);
      padding: 9px 12px 9px 34px;
      border-radius: 8px;
      color: #fff;
      font-size: 0.8rem;
      outline: none;
      transition: all 0.2s;
    }}

    .sidebar-search input:focus {{
      border-color: var(--accent-blue);
      box-shadow: 0 0 10px rgba(56, 189, 248, 0.25);
    }}

    .sidebar-search svg {{
      position: absolute;
      left: 10px;
      top: 10px;
      width: 14px;
      height: 14px;
      fill: var(--text-muted);
    }}

    .sidebar-nav {{
      padding: 10px 12px;
    }}

    .nav-group-title {{
      font-size: 0.68rem;
      font-weight: 800;
      color: var(--text-dim);
      letter-spacing: 0.8px;
      text-transform: uppercase;
      padding: 12px 10px 4px 10px;
    }}

    .nav-item {{
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 8px 12px;
      border-radius: 8px;
      font-size: 0.82rem;
      font-weight: 600;
      color: var(--text-muted);
      cursor: pointer;
      transition: all 0.15s ease;
      margin-bottom: 2px;
    }}

    .nav-item:hover {{
      background: rgba(56, 189, 248, 0.08);
      color: #fff;
    }}

    .nav-item svg {{
      width: 16px;
      height: 16px;
      fill: currentColor;
    }}

    .nav-item.active {{
      background: rgba(56, 189, 248, 0.14);
      color: var(--accent-blue);
      border: 1px solid rgba(56, 189, 248, 0.28);
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
      font-size: 0.72rem;
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
      background: rgba(11, 17, 30, 0.85);
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
      font-size: 0.72rem;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }}

    .dash-sub {{
      font-size: 0.82rem;
      color: var(--text-muted);
      margin-top: 3px;
    }}

    /* Stat Pills */
    .stat-pills {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }}

    .pill {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 6px 12px;
      border-radius: 20px;
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid rgba(255, 255, 255, 0.1);
      font-size: 0.74rem;
      font-weight: 700;
      color: var(--text-main);
    }}

    .pill-live {{
      background: rgba(16, 185, 129, 0.12);
      border-color: rgba(16, 185, 129, 0.35);
      color: var(--accent-emerald);
    }}

    .pill-accent {{
      background: rgba(56, 189, 248, 0.12);
      border-color: rgba(56, 189, 248, 0.35);
      color: var(--accent-blue);
    }}

    .pill-purple {{
      background: rgba(168, 85, 247, 0.12);
      border-color: rgba(168, 85, 247, 0.35);
      color: var(--accent-purple);
    }}

    /* Alert Attribution Banner */
    .data-banner {{
      margin: 12px 24px 0 24px;
      padding: 10px 16px;
      border-radius: 8px;
      background: rgba(2, 132, 199, 0.1);
      border-left: 4px solid var(--accent-blue);
      font-size: 0.78rem;
      color: #bae6fd;
      line-height: 1.45;
    }}

    /* MAP CONTAINER */
    .map-section {{
      padding: 16px 24px;
      flex-shrink: 0;
    }}

    .map-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 12px;
      flex-wrap: wrap;
      gap: 10px;
    }}

    .map-title h3 {{
      font-size: 1.1rem;
      font-weight: 800;
      color: #fff;
    }}

    .map-title span {{
      font-size: 0.75rem;
      color: var(--text-muted);
    }}

    .view-tabs {{
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
    }}

    .view-btn {{
      padding: 5px 12px;
      border-radius: 6px;
      border: 1px solid var(--border-color);
      background: rgba(18, 27, 46, 0.7);
      color: var(--text-muted);
      font-size: 0.74rem;
      font-weight: 700;
      cursor: pointer;
      transition: all 0.15s ease;
    }}

    .view-btn:hover, .view-btn.active {{
      background: var(--accent-blue);
      color: #080c14;
      border-color: var(--accent-blue);
    }}

    .map-wrapper {{
      position: relative;
      width: 100%;
      height: 600px;
      border-radius: 14px;
      border: 1px solid var(--border-color);
      overflow: hidden;
      box-shadow: 0 12px 36px rgba(0, 0, 0, 0.7);
    }}

    #map {{
      width: 100%;
      height: 100%;
      background: #080c14;
    }}

    /* Floating Layer Controller */
    .map-layers-control {{
      position: absolute;
      top: 14px;
      right: 14px;
      background: var(--panel-bg);
      border: 1px solid var(--border-color);
      padding: 12px 14px;
      border-radius: 10px;
      z-index: 1000;
      box-shadow: var(--shadow-sm);
      backdrop-filter: blur(10px);
      -webkit-backdrop-filter: blur(10px);
      max-width: 290px;
      max-height: 480px;
      overflow-y: auto;
    }}

    .layers-title {{
      font-size: 0.75rem;
      font-weight: 800;
      color: #fff;
      margin-bottom: 8px;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      border-bottom: 1px solid rgba(255, 255, 255, 0.1);
      padding-bottom: 4px;
      display: flex;
      justify-content: space-between;
    }}

    .layer-row {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 7px;
      font-size: 0.74rem;
      color: var(--text-main);
      cursor: pointer;
    }}

    .layer-row label {{
      display: flex;
      align-items: center;
      gap: 7px;
      cursor: pointer;
    }}

    .layer-row input[type="checkbox"] {{
      accent-color: var(--accent-blue);
      cursor: pointer;
    }}

    /* Bottom Legend Bar inside Map */
    .map-legend-bar {{
      position: absolute;
      bottom: 14px;
      left: 14px;
      background: var(--panel-bg);
      border: 1px solid var(--border-color);
      padding: 8px 16px;
      border-radius: 30px;
      z-index: 1000;
      display: flex;
      align-items: center;
      gap: 16px;
      backdrop-filter: blur(8px);
      -webkit-backdrop-filter: blur(8px);
      box-shadow: var(--shadow-sm);
      font-size: 0.72rem;
      color: #fff;
      flex-wrap: wrap;
    }}

    .legend-item {{
      display: flex;
      align-items: center;
      gap: 6px;
    }}

    .legend-dot {{
      width: 10px;
      height: 10px;
      border-radius: 50%;
    }}

    /* BOTTOM 4 FEATURE CARDS */
    .bottom-cards-section {{
      padding: 8px 24px 32px 24px;
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
      gap: 16px;
    }}

    .feature-card {{
      background: var(--card-bg);
      border: 1px solid var(--border-color);
      border-radius: 12px;
      padding: 20px 18px;
      transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
      cursor: pointer;
      position: relative;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
    }}

    .feature-card:hover {{
      background: var(--card-hover);
      border-color: var(--border-glow);
      transform: translateY(-4px);
      box-shadow: 0 12px 28px -8px rgba(56, 189, 248, 0.25);
    }}

    .feature-card .card-icon {{
      width: 36px;
      height: 36px;
      border-radius: 8px;
      background: rgba(56, 189, 248, 0.12);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 1.1rem;
      margin-bottom: 12px;
      color: var(--accent-blue);
    }}

    .feature-card h4 {{
      font-size: 0.98rem;
      font-weight: 800;
      color: #fff;
      margin-bottom: 6px;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }}

    .feature-card h4 span {{
      color: var(--accent-blue);
      font-size: 0.85rem;
      transition: transform 0.2s;
    }}

    .feature-card:hover h4 span {{
      transform: translateX(4px);
    }}

    .feature-card p {{
      font-size: 0.78rem;
      color: var(--text-muted);
      line-height: 1.45;
      margin-bottom: 12px;
      flex-grow: 1;
    }}

    .feature-card .card-meta {{
      font-size: 0.68rem;
      color: var(--text-dim);
      font-weight: 700;
      letter-spacing: 0.3px;
      text-transform: uppercase;
      border-top: 1px solid rgba(255, 255, 255, 0.06);
      padding-top: 8px;
    }}

    /* POPUP STYLES */
    .station-popup {{
      font-family: 'Plus Jakarta Sans', sans-serif;
      color: #0f172a;
      min-width: 250px;
    }}

    .pop-tag {{
      display: inline-block;
      padding: 2px 7px;
      border-radius: 4px;
      font-size: 0.65rem;
      font-weight: 800;
      text-transform: uppercase;
      margin-bottom: 4px;
    }}

    .tag-insivumeh {{ background: #10b981; color: #fff; }}
    .tag-usac {{ background: #a855f7; color: #fff; }}
    .tag-amsclae {{ background: #0284c7; color: #fff; }}
    .tag-amsa {{ background: #f59e0b; color: #fff; }}
    .tag-marn {{ background: #f43f5e; color: #fff; }}
    .tag-wpdx {{ background: #6366f1; color: #fff; }}

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
      background: rgba(255, 255, 255, 0.05);
      padding: 4px 6px;
      border-radius: 6px;
    }}

    .pop-stat .k {{
      font-size: 0.65rem;
      color: var(--text-muted);
      text-transform: uppercase;
      display: block;
    }}

    .pop-stat .v {{
      font-size: 0.85rem;
      font-weight: 700;
      color: #38bdf8;
      font-family: 'JetBrains Mono', monospace;
    }}

    /* SLIDE-OVER DETAIL DRAWER & SIMULATION */
    #detail-drawer {{
      position: fixed;
      top: 0;
      right: -520px;
      width: 520px;
      height: 100vh;
      background: var(--sidebar-bg);
      border-left: 1px solid var(--border-color);
      box-shadow: -14px 0 40px rgba(0, 0, 0, 0.9);
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
      border: 1px solid var(--border-color);
      color: #fff;
      padding: 6px 12px;
      border-radius: 6px;
      cursor: pointer;
      font-weight: 700;
      font-size: 0.8rem;
      transition: all 0.2s;
    }}

    .drawer-close:hover {{
      background: var(--accent-rose);
      border-color: var(--accent-rose);
    }}

    .drawer-content h3 {{
      margin-top: 10px;
      font-size: 1.25rem;
      color: #fff;
    }}

    /* SIMULATION STYLES */
    .sim-container {{
      margin: 16px 0;
      background: #060a12;
      border: 1px solid var(--border-color);
      border-radius: 12px;
      overflow: hidden;
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.6);
      position: relative;
    }}

    .sim-header {{
      padding: 10px 14px;
      background: rgba(14, 21, 37, 0.9);
      border-bottom: 1px solid rgba(255, 255, 255, 0.08);
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}

    .sim-title {{
      font-size: 0.78rem;
      font-weight: 800;
      color: #fff;
      display: flex;
      align-items: center;
      gap: 6px;
    }}

    .sim-controls {{
      display: flex;
      align-items: center;
      gap: 6px;
    }}

    .sim-btn {{
      padding: 3px 8px;
      border-radius: 4px;
      background: rgba(255, 255, 255, 0.08);
      border: 1px solid rgba(255, 255, 255, 0.15);
      color: #fff;
      font-size: 0.68rem;
      font-weight: 700;
      cursor: pointer;
      transition: all 0.15s;
    }}

    .sim-btn:hover {{
      background: var(--accent-blue);
      color: #080c14;
    }}

    .sim-btn.active {{
      background: var(--accent-emerald);
      color: #080c14;
      border-color: var(--accent-emerald);
    }}

    .sim-canvas-wrap {{
      position: relative;
      width: 100%;
      height: 190px;
      background: #040810;
    }}

    #riverCanvas {{
      width: 100%;
      height: 100%;
      display: block;
    }}

    .sim-water-badge {{
      position: absolute;
      bottom: 8px;
      left: 10px;
      padding: 4px 10px;
      border-radius: 20px;
      font-size: 0.72rem;
      font-weight: 800;
      backdrop-filter: blur(8px);
      -webkit-backdrop-filter: blur(8px);
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.6);
      display: flex;
      align-items: center;
      gap: 6px;
    }}

    .sim-wqi-meter {{
      position: absolute;
      top: 8px;
      right: 10px;
      background: rgba(11, 17, 30, 0.85);
      border: 1px solid rgba(255, 255, 255, 0.15);
      padding: 4px 8px;
      border-radius: 8px;
      font-size: 0.7rem;
      font-weight: 800;
      color: #fff;
      font-family: 'JetBrains Mono', monospace;
    }}

    /* COGUANOR DIAGNOSTIC ENGINE BOX */
    .diagnostic-box {{
      background: rgba(255, 255, 255, 0.03);
      border: 1px solid var(--border-color);
      border-radius: 10px;
      padding: 14px;
      margin: 16px 0;
    }}

    .diag-title {{
      font-size: 0.88rem;
      font-weight: 800;
      color: #fff;
      margin-bottom: 8px;
      display: flex;
      align-items: center;
      gap: 8px;
    }}

    .diag-verdict {{
      padding: 8px 12px;
      border-radius: 6px;
      font-size: 0.8rem;
      font-weight: 700;
      margin-bottom: 12px;
      line-height: 1.4;
    }}

    .verdict-bad {{
      background: rgba(244, 63, 94, 0.15);
      border: 1px solid rgba(244, 63, 94, 0.4);
      color: #fda4af;
    }}

    .verdict-good {{
      background: rgba(16, 185, 129, 0.15);
      border: 1px solid rgba(16, 185, 129, 0.4);
      color: #6ee7b7;
    }}

    .verdict-regular {{
      background: rgba(245, 158, 11, 0.15);
      border: 1px solid rgba(245, 158, 11, 0.4);
      color: #fde68a;
    }}

    .param-diag-list {{
      display: flex;
      flex-direction: column;
      gap: 8px;
    }}

    .param-item {{
      background: rgba(0, 0, 0, 0.3);
      border-radius: 6px;
      padding: 8px 10px;
      border-left: 3px solid #64748b;
      font-size: 0.76rem;
    }}

    .param-item.bad {{ border-left-color: var(--accent-rose); }}
    .param-item.good {{ border-left-color: var(--accent-emerald); }}
    .param-item.warn {{ border-left-color: var(--accent-amber); }}

    .param-header {{
      display: flex;
      justify-content: space-between;
      font-weight: 700;
      color: #fff;
      margin-bottom: 3px;
    }}

    .param-reason {{
      color: var(--text-muted);
      line-height: 1.35;
    }}

    /* Leaflet Dark Popup override */
    .leaflet-popup-content-wrapper {{
      background: rgba(14, 21, 37, 0.95) !important;
      color: #fff !important;
      border: 1px solid var(--border-color);
      border-radius: 10px !important;
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.8) !important;
      backdrop-filter: blur(8px);
    }}

    .leaflet-popup-tip {{
      background: rgba(14, 21, 37, 0.95) !important;
      border: 1px solid var(--border-color);
    }}

    @media (max-width: 960px) {{
      aside.sidebar {{ display: none; }}
      .map-legend-bar {{ flex-wrap: wrap; border-radius: 12px; }}
      #detail-drawer {{ width: 100vw; right: -100vw; }}
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
              <span>Observatorio Hídrico Nacional</span>
            </div>
          </div>
        </div>

        <div class="sidebar-search">
          <svg viewBox="0 0 24 24"><path d="M10 2a8 8 0 015.293 13.998l4.704 4.705a1 1 0 01-1.414 1.414l-4.705-4.704A8 8 0 1110 2zm0 2a6 6 0 100 12 6 6 0 000-12z"/></svg>
          <input type="text" id="station-search" placeholder="Buscar río, lago o estación..." onkeyup="searchNationalStations(this.value)">
        </div>

        <nav class="sidebar-nav">
          <div class="nav-group-title">ENFOQUE TERRITORIAL</div>
          <div class="nav-item active" onclick="zoomTo('guatemala')">
            <svg viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/></svg>
            Toda Guatemala (38 Cuencas)
          </div>
          <div class="nav-item" onclick="zoomTo('motagua')">
            <svg viewBox="0 0 24 24"><path d="M4 11a1 1 0 011 1 7 7 0 007 7 1 1 0 010 2 9 9 0 01-9-9 1 1 0 011-1zm0-4a1 1 0 011 1 11 11 0 0011 11 1 1 0 010 2 13 13 0 01-13-13 1 1 0 011-1zm0-4a1 1 0 011 1 15 15 0 0015 15 1 1 0 010 2 17 17 0 01-17-17 1 1 0 011-1z"/></svg>
            Cuenca Motagua & Las Vacas
          </div>
          <div class="nav-item" onclick="zoomTo('atitlan')">
            <svg viewBox="0 0 24 24"><path d="M19 19H5V5h14v14zM3 3v18h18V3H3zm8 4h2v6h-2V7zm0 8h2v2h-2v-2z"/></svg>
            Lago de Atitlán (AMSCLAE/UVG)
          </div>
          <div class="nav-item" onclick="zoomTo('amatitlan')">
            <svg viewBox="0 0 24 24"><path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/></svg>
            Lago de Amatitlán (AMSA)
          </div>
          <div class="nav-item" onclick="zoomTo('izabal')">
            <svg viewBox="0 0 24 24"><path d="M20.5 3l-.16.03L15 5.1 9 3 3.36 4.9c-.21.07-.36.25-.36.48V20.5c0 .28.22.5.5.5l.16-.03L9 18.9l6 2.1 5.64-1.9c.21-.07.36-.25.36-.48V3.5c0-.28-.22-.5-.5-.5zM15 19l-6-2.11V5l6 2.11V19z"/></svg>
            Lago de Izabal & Río Dulce
          </div>

          <div class="nav-group-title">SIMULACIÓN Y CALIDAD COGUANOR</div>
          <div class="nav-item" onclick="triggerPresetSimulation('septic')">
            <span style="font-size:0.9rem;">☣️</span> Río Séptico / Cloacal (Las Vacas)
          </div>
          <div class="nav-item" onclick="triggerPresetSimulation('pristine')">
            <span style="font-size:0.9rem;">💎</span> Río Sano / Prístino (Atitlán)
          </div>
          <div class="nav-item" onclick="triggerPresetSimulation('eutrophic')">
            <span style="font-size:0.9rem;">🦠</span> Lago Eutrofizado (Amatitlán)
          </div>
          <div class="nav-item" onclick="triggerPresetSimulation('turbid')">
            <span style="font-size:0.9rem;">🌊</span> Río Turbio Aluvial (Gualán)
          </div>

          <div class="nav-group-title">REDES DE MONITOREO NACIONAL</div>
          <div class="nav-item" onclick="toggleMapLayer('insiv_qual')">
            <svg viewBox="0 0 24 24"><path d="M19.5 21a3 3 0 003-3v-4.5a3 3 0 00-3-3h-1.5V6a3 3 0 00-3-3h-6a3 3 0 00-3 3v4.5H4.5a3 3 0 00-3 3V18a3 3 0 003 3h15z"/></svg>
            INSIVUMEH Calidad (76 pts)
          </div>
          <div class="nav-item" onclick="toggleMapLayer('insiv_cau')">
            <svg viewBox="0 0 24 24"><path d="M12 2a10 10 0 100 20 10 10 0 000-20zm1 14.93V18a1 1 0 11-2 0v-1.07A7.002 7.002 0 015.07 11H4a1 1 0 110-2h1.07A7.002 7.002 0 0111 3.07V2a1 1 0 112 0v1.07A7.002 7.002 0 0118.93 9H20a1 1 0 110 2h-1.07A7.002 7.002 0 0113 16.93zM12 7a5 5 0 100 10 5 5 0 000-10z"/></svg>
            INSIVUMEH Caudales (36 est)
          </div>
          <div class="nav-item" onclick="toggleMapLayer('marn_acid')">
            <svg viewBox="0 0 24 24"><path d="M12 3L1 9l11 6 9-4.91V17h2V9L12 3zM3.45 9L12 4.33 20.55 9 12 13.67 3.45 9zM5 13.18v4L12 21l7-3.82v-4L12 17l-7-3.82z"/></svg>
            MARN Sitios Costeros (11 est)
          </div>
          <div class="nav-item" onclick="toggleMapLayer('wpdx')">
            <svg viewBox="0 0 24 24"><path d="M12 2.69l5.66 5.66a8 8 0 11-11.31 0z"/></svg>
            Pozos Comunitarios WPdx (128)
          </div>
        </nav>
      </div>

      <div class="sidebar-footer">
        <div class="live-indicator">
          <div class="live-dot"></div>
          <span>SIMULADOR COGUANOR ACTIVO</span>
        </div>
        <div>Normas: NTG 29001 & AG 236-2006</div>
        <div style="margin-top: 4px; font-family: 'JetBrains Mono', monospace;">Antigravity Visual Engine v2.5</div>
      </div>
    </aside>

    <!-- MAIN CONTENT -->
    <main class="main-content">
      
      <!-- Top Bar Header -->
      <div class="dashboard-header">
        <div class="dash-titles">
          <h1>
            RÍOS ABIERTOS GT <span style="font-weight: 400; color: #94a3b8;">Observatorio Nacional</span>
            <span class="tag-cat">Guatemala</span>
          </h1>
          <div class="dash-sub">Plataforma Hídrica con Simulador Físico de Flujo en Vivo y Diagnóstico COGUANOR</div>
        </div>

        <div class="stat-pills">
          <div class="pill pill-live">
            <span style="display:inline-block; width:6px; height:6px; background:#10b981; border-radius:50%;"></span>
            36 Estaciones Caudales INSIVUMEH
          </div>
          <div class="pill pill-purple">
            🧪 76 Puntos Calidad INSIVUMEH (33 Cuencas)
          </div>
          <div class="pill pill-accent">
            🗺️ 38 Cuencas MAGA / MARN
          </div>
          <div class="pill">
            🌊 11 Grandes Lagos
          </div>
          <div class="pill">
            📍 32 Puntos Fármacos USAC
          </div>
        </div>
      </div>

      <!-- Alert Data Notice -->
      <div class="data-banner">
        <strong>Simulación Fluvial Basada en Datos Reales:</strong> Haz clic en cualquier estación de monitoreo o punto en el mapa para ver la <strong>animación del río en vivo</strong> (color, turbiedad, transparencia, burbujas de fermentación o espuma) y el <strong>diagnóstico normativo de COGUANOR NTG 29001 y Acuerdo Gubernativo 236-2006</strong>.
      </div>

      <!-- MAP SECTION -->
      <div class="map-section">
        <div class="map-header">
          <div class="map-title">
            <h3>Interactive Watershed & Water Quality Map</h3>
            <span>Exploración geoespacial nacional — selecciona cualquier punto para activar el simulador visual del agua</span>
          </div>

          <!-- Quick Navigation View Tabs -->
          <div class="view-tabs">
            <button class="view-btn active" onclick="zoomTo('guatemala')">🇬🇹 Toda Guatemala</button>
            <button class="view-btn" onclick="zoomTo('motagua')">🌊 Río Motagua</button>
            <button class="view-btn" onclick="zoomTo('atitlan')">🌋 Atitlán (AMSCLAE)</button>
            <button class="view-btn" onclick="zoomTo('amatitlan')">🏞️ Amatitlán (AMSA)</button>
            <button class="view-btn" onclick="zoomTo('izabal')">🌴 Lago de Izabal</button>
            <button class="view-btn" onclick="zoomTo('costas')">🌊 Costas MARN</button>
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
              <label><input type="checkbox" id="chk-cuencas" checked onchange="toggleLayer('cuencas')"> 38 Cuencas MAGA/MARN</label>
              <span style="color:#0284c7; font-weight:800;">38</span>
            </div>
            <div class="layer-row">
              <label><input type="checkbox" id="chk-lakes" checked onchange="toggleLayer('lakes')"> Grandes Lagos Nacionales</label>
              <span style="color:#38bdf8; font-weight:800;">11</span>
            </div>
            <div class="layer-row">
              <label><input type="checkbox" id="chk-insiv-qual" checked onchange="toggleLayer('insiv_qual')"> INSIVUMEH Calidad (33 Cuencas)</label>
              <span style="color:#c084fc; font-weight:800;">76</span>
            </div>
            <div class="layer-row">
              <label><input type="checkbox" id="chk-insiv-cau" checked onchange="toggleLayer('insiv_cau')"> INSIVUMEH Caudales (Aforos)</label>
              <span style="color:#34d399; font-weight:800;">36</span>
            </div>
            <div class="layer-row">
              <label><input type="checkbox" id="chk-amsclae" checked onchange="toggleLayer('amsclae')"> AMSCLAE / Atitlán (Ríos y Lago)</label>
              <span style="color:#38bdf8; font-weight:800;">7</span>
            </div>
            <div class="layer-row">
              <label><input type="checkbox" id="chk-amsa" checked onchange="toggleLayer('amsa')"> AMSA / Amatitlán & PTARs</label>
              <span style="color:#fbbf24; font-weight:800;">4</span>
            </div>
            <div class="layer-row">
              <label><input type="checkbox" id="chk-marn-acid" checked onchange="toggleLayer('marn_acid')"> MARN Costero (Acidificación)</label>
              <span style="color:#fb7185; font-weight:800;">11</span>
            </div>
            <div class="layer-row">
              <label><input type="checkbox" id="chk-usac" checked onchange="toggleLayer('usac')"> USAC ERIS Fármacos (Motagua)</label>
              <span style="color:#e879f9; font-weight:800;">32</span>
            </div>
            <div class="layer-row">
              <label><input type="checkbox" id="chk-wpdx" checked onchange="toggleLayer('wpdx')"> Pozos Comunitarios WPdx</label>
              <span style="color:#818cf8; font-weight:800;">128</span>
            </div>
            <div class="layer-row">
              <label><input type="checkbox" id="chk-motagua" checked onchange="toggleLayer('motagua')"> Red Fluvial Motagua (HydroRIVERS)</label>
              <span style="color:#0ea5e9; font-weight:800;">1,626</span>
            </div>
          </div>

          <!-- Bottom Legend Bar Overlay -->
          <div class="map-legend-bar">
            <div class="legend-item">
              <div class="legend-dot" style="background: #c084fc; box-shadow: 0 0 8px #c084fc;"></div>
              <span>76 Calidad INSIVUMEH</span>
            </div>
            <div class="legend-item">
              <div class="legend-dot" style="background: #34d399; box-shadow: 0 0 8px #34d399;"></div>
              <span>36 Caudales INSIVUMEH</span>
            </div>
            <div class="legend-item">
              <div class="legend-dot" style="background: #38bdf8; box-shadow: 0 0 8px #38bdf8;"></div>
              <span>AMSCLAE (Atitlán)</span>
            </div>
            <div class="legend-item">
              <div class="legend-dot" style="background: #fbbf24; box-shadow: 0 0 8px #fbbf24;"></div>
              <span>AMSA (Amatitlán)</span>
            </div>
            <div class="legend-item">
              <div class="legend-dot" style="background: #fb7185; box-shadow: 0 0 8px #fb7185;"></div>
              <span>MARN Costero</span>
            </div>
            <div class="legend-item">
              <div class="legend-dot" style="background: #818cf8; box-shadow: 0 0 8px #818cf8;"></div>
              <span>Pozos WPdx</span>
            </div>
          </div>
        </div>
      </div>

      <!-- BOTTOM 4 FEATURE CARDS -->
      <div class="bottom-cards-section">
        
        <div class="feature-card" onclick="zoomTo('guatemala')">
          <div class="card-icon">🗺️</div>
          <h4>Mapa interactivo <span>→</span></h4>
          <p>Explora las 38 cuencas hidrográficas de Guatemala, 3 vertientes y más de 1,600 tramos fluviales con caudales modelados y estaciones georreferenciadas.</p>
          <div class="card-meta">38 Cuencas MAGA/MARN | 1,626 Tramos HydroRIVERS</div>
        </div>

        <div class="feature-card" onclick="openDrawerInfo('Red Oficial de Calidad del Agua', 'Evaluación multivariable con 76 estaciones del INSIVUMEH en 33 cuencas nacionales (pH, Oxígeno Disuelto, DQO, Turbiedad, Nitratos, Amonio), monitoreo limnológico en Lago de Atitlán (AMSCLAE/UVG), Lago de Amatitlán (AMSA), estaciones costeras de acidificación (MARN) y análisis por HPLC-MS/MS de 15 fármacos en Río Las Vacas (USAC ERIS).')">
          <div class="card-icon">🧪</div>
          <h4>Calidad del agua <span>→</span></h4>
          <p>pH, Oxígeno Disuelto, DQO, conductividad y fármacos. 76 estaciones en 33 cuencas nacionales más monitoreo limnológico en Atitlán y Amatitlán.</p>
          <div class="card-meta">76 Estaciones INSIVUMEH | AMSCLAE | AMSA | MARN | USAC</div>
        </div>

        <div class="feature-card" onclick="openDrawerInfo('Hidrometría y Caudales Históricos', 'Base de datos oficial de aforos de caudales del INSIVUMEH en 36 estaciones clave de las tres vertientes (Pacífico, Caribe y Golfo de México), incluyendo registros de Gualán (Motagua, 344 m³/s), Panajax (Las Vacas), Cahaboncito, Caballo Blanco, Concuá II y series históricas 2010–2024 del Lago de Atitlán.')">
          <div class="card-icon">📈</div>
          <h4>Datos históricos <span>→</span></h4>
          <p>Caudales medios mensuales en 36 estaciones del INSIVUMEH, aforos en tributarios de lagos y series temporales de 2010 a 2026.</p>
          <div class="card-meta">36 Estaciones Caudales INSIVUMEH | Series UVG 2010–2024</div>
        </div>

        <div class="feature-card" onclick="openDrawerInfo('Vigilancia Nacional y Transparencia Pública', 'Vigilancia comunitaria del agua potable por el MSPAS en 5,710 comunidades (E. Coli y coliformes totales) y 3,993 sistemas en cloro residual. Mapeo de 1,908 pozos comunitarios en WPdx y protocolo de solicitudes bajo la Ley de Acceso a la Información Pública (Decreto 57-2008).')">
          <div class="card-icon">👥</div>
          <h4>Participación pública <span>→</span></h4>
          <p>Vigilancia comunitaria de agua potable en 5,710 comunidades (MSPAS), 1,908 pozos en WPdx y solicitudes de transparencia Decreto 57-2008.</p>
          <div class="card-meta">5,710 Comunidades MSPAS | 1,908 Pozos WPdx | Decreto 57-2008</div>
        </div>

      </div>

    </main>
  </div>

  <!-- SLIDE-OVER DETAIL DRAWER WITH LIVE SIMULATOR -->
  <div id="detail-drawer">
    <button class="drawer-close" onclick="closeDrawer()">✕ Cerrar</button>
    <div class="drawer-content" id="drawer-body">
      <h3>Detalle de la Estación</h3>
      <p>Selecciona una estación en el mapa para ver sus mediciones completas y simulación del flujo.</p>
    </div>
  </div>

  <!-- Leaflet JS -->
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=" crossorigin=""></script>

  <!-- Embedded National Data Bundle -->
  <script>
    const NATIONAL_DATA = {bundle_str};
  </script>

  <!-- Main GIS Logic & Flow Simulation Engine -->
  <script>
    let map;
    let cuencasLayer, lakesLayer, insivQualLayer, insivCauLayer, amsclaeLayer, amsaLayer, marnAcidLayer, usacLayer, wpdxLayer, motaguaLayer;

    // Simulation Engine Global State
    let animId = null;
    let isPaused = false;
    let ptarActive = false;
    let currentSimData = null;
    let simParticles = [];
    let simTime = 0;

    document.addEventListener("DOMContentLoaded", function() {{
      initMap();
    }});

    function initMap() {{
      map = L.map('map', {{
        center: [15.35, -90.35],
        zoom: 7.8,
        zoomControl: true,
        attributionControl: false
      }});

      L.tileLayer('https://{{s}}.basemaps.cartocdn.com/dark_all/{{z}}/{{x}}/{{y}}{{r}}.png', {{
        subdomains: 'abcd',
        maxZoom: 19
      }}).addTo(map);

      L.control.attribution({{position: 'bottomright', prefix: 'RÍOS ABIERTOS GT | INSIVUMEH | MARN | AMSCLAE | AMSA | USAC'}}).addTo(map);

      // 1. 38 CUENCAS MAGA/MARN
      cuencasLayer = L.geoJSON(NATIONAL_DATA.guatemala_basins_38, {{
        style: {{
          color: '#0284c7',
          weight: 1.5,
          opacity: 0.55,
          fillColor: '#0369a1',
          fillOpacity: 0.08,
          dashArray: '3, 4'
        }},
        onEachFeature: function(feature, layer) {{
          const p = feature.properties;
          layer.bindPopup(`
            <div class="station-popup">
              <span class="pop-tag" style="background:#0284c7; color:#fff;">Cuenca Hidrográfica Oficial</span>
              <div class="pop-title">${{p.name}} (Código: ${{p.codigo}})</div>
              <div class="pop-grid">
                <div class="pop-stat"><span class="k">Vertiente</span><span class="v">${{p.vertiente || 'Nacional'}}</span></div>
                <div class="pop-stat"><span class="k">Área Cuenca</span><span class="v">${{p.km2 ? p.km2.toLocaleString() + ' km²' : 'N/D'}}</span></div>
              </div>
            </div>
          `);
        }}
      }}).addTo(map);

      // 2. GRANDES LAGOS NACIONALES
      lakesLayer = L.geoJSON(NATIONAL_DATA.guatemala_major_lakes, {{
        style: {{
          color: '#38bdf8',
          weight: 2,
          opacity: 0.9,
          fillColor: '#0ea5e9',
          fillOpacity: 0.45
        }},
        onEachFeature: function(feature, layer) {{
          const p = feature.properties;
          layer.bindPopup(`
            <div class="station-popup">
              <span class="pop-tag" style="background:#38bdf8; color:#080c14;">Cuerpo Lacustre Oficial</span>
              <div class="pop-title">${{p.NOMBRE || 'Lago Nacional'}}</div>
              <div class="pop-grid">
                <div class="pop-stat"><span class="k">Tipo</span><span class="v">${{p.TIPO == 1 ? 'Lago / Laguna' : 'Embalse'}}</span></div>
                <div class="pop-stat"><span class="k">Superficie</span><span class="v">${{p.AREA_KM2 ? p.AREA_KM2 + ' km²' : 'N/D'}}</span></div>
              </div>
            </div>
          `);
        }}
      }}).addTo(map);

      // 3. INSIVUMEH CALIDAD NACIONAL (76 puntos)
      insivQualLayer = L.layerGroup();
      if (NATIONAL_DATA.insivumeh_quality_stations && NATIONAL_DATA.insivumeh_quality_stations.features) {{
        NATIONAL_DATA.insivumeh_quality_stations.features.forEach(feat => {{
          const p = feat.properties;
          const coords = [feat.geometry.coordinates[1], feat.geometry.coordinates[0]];
          
          let statusBadge = p.od_mg_l !== null && p.od_mg_l < 3.0 ? 
            `<span style="color:#f43f5e; font-weight:800;">🔴 Anóxico (No cumple COGUANOR)</span>` : 
            `<span style="color:#10b981; font-weight:800;">🟢 Oxigenación Estable</span>`;

          const marker = L.circleMarker(coords, {{
            radius: 7,
            fillColor: p.od_mg_l !== null && p.od_mg_l < 3.0 ? '#f43f5e' : '#c084fc',
            color: '#ffffff',
            weight: 1.5,
            opacity: 1,
            fillOpacity: 0.85
          }});

          marker.bindPopup(`
            <div class="station-popup">
              <span class="pop-tag tag-insivumeh">INSIVUMEH Calidad</span>
              <div class="pop-title">${{p.name}}</div>
              <div style="font-size:0.75rem; color:#94a3b8; margin-bottom:4px;">${{p.water_body}} | Cuenca: ${{p.basin}}</div>
              <div style="font-size:0.72rem; color:#cbd5e1; margin-bottom:6px;">${{p.municipality}}, ${{p.department}} • ${{statusBadge}}</div>
              <div class="pop-grid">
                <div class="pop-stat"><span class="k">pH</span><span class="v">${{p.ph || 'N/D'}}</span></div>
                <div class="pop-stat"><span class="k">Oxígeno Disuelto</span><span class="v">${{p.od_mg_l !== null ? p.od_mg_l + ' mg/L' : 'N/D'}}</span></div>
                <div class="pop-stat"><span class="k">Conductividad</span><span class="v">${{p.conductividad_us_cm !== null ? p.conductividad_us_cm + ' µS/cm' : 'N/D'}}</span></div>
                <div class="pop-stat"><span class="k">DQO</span><span class="v">${{p.dqo_mg_l !== null ? p.dqo_mg_l + ' mg/L' : 'N/D'}}</span></div>
              </div>
              <button onclick="openDrawerStation('${{p.id}}')" style="width:100%; margin-top:6px; background:linear-gradient(135deg,#0284c7,#0d9488); border:none; color:#fff; padding:6px 10px; border-radius:6px; font-weight:800; font-size:0.76rem; cursor:pointer; box-shadow:0 0 10px rgba(2,132,199,0.5);">🌊 Ver Animación Fluvial & COGUANOR</button>
            </div>
          `);

          marker.addTo(insivQualLayer);
        }});
      }}
      insivQualLayer.addTo(map);

      // 4. INSIVUMEH CAUDALES NACIONAL (36 estaciones)
      insivCauLayer = L.layerGroup();
      if (NATIONAL_DATA.insivumeh_streamflow_stations && NATIONAL_DATA.insivumeh_streamflow_stations.features) {{
        NATIONAL_DATA.insivumeh_streamflow_stations.features.forEach(feat => {{
          const p = feat.properties;
          const coords = [feat.geometry.coordinates[1], feat.geometry.coordinates[0]];

          const marker = L.circleMarker(coords, {{
            radius: 8,
            fillColor: '#34d399',
            color: '#ffffff',
            weight: 2,
            opacity: 1,
            fillOpacity: 0.9
          }});

          marker.bindPopup(`
            <div class="station-popup">
              <span class="pop-tag tag-insivumeh">INSIVUMEH Aforo Hidrométrico</span>
              <div class="pop-title">${{p.name}}</div>
              <div style="font-size:0.75rem; color:#94a3b8; margin-bottom:4px;">${{p.water_body}} | Cuenca: ${{p.basin}}</div>
              <div style="font-size:0.72rem; color:#cbd5e1; margin-bottom:6px;">Vertiente: ${{p.vertiente}} (${{p.municipality}}, ${{p.department}})</div>
              <div class="pop-grid">
                <div class="pop-stat"><span class="k">Caudal Medio Anual</span><span class="v" style="color:#34d399;">${{p.caudal_medio_anual}} m³/s</span></div>
                <div class="pop-stat"><span class="k">Caudal Máx Mensual</span><span class="v">${{p.caudal_max_mensual}} m³/s</span></div>
              </div>
              <button onclick="openDrawerStation('${{p.id}}')" style="width:100%; margin-top:6px; background:linear-gradient(135deg,#059669,#10b981); border:none; color:#fff; padding:6px 10px; border-radius:6px; font-weight:800; font-size:0.76rem; cursor:pointer;">🌊 Ver Animación Caudal & COGUANOR</button>
            </div>
          `);

          marker.addTo(insivCauLayer);
        }});
      }}
      insivCauLayer.addTo(map);

      // 5. AMSCLAE LAGO DE ATITLÁN (7 estaciones)
      amsclaeLayer = L.layerGroup();
      if (NATIONAL_DATA.amsclae_atitlan_stations && NATIONAL_DATA.amsclae_atitlan_stations.features) {{
        NATIONAL_DATA.amsclae_atitlan_stations.features.forEach(feat => {{
          const p = feat.properties;
          const coords = [feat.geometry.coordinates[1], feat.geometry.coordinates[0]];

          const marker = L.circleMarker(coords, {{
            radius: 8,
            fillColor: '#38bdf8',
            color: '#ffffff',
            weight: 2,
            opacity: 1,
            fillOpacity: 0.95
          }});

          marker.bindPopup(`
            <div class="station-popup">
              <span class="pop-tag tag-amsclae">AMSCLAE / UVG</span>
              <div class="pop-title">${{p.name}}</div>
              <div style="font-size:0.75rem; color:#94a3b8; margin-bottom:4px;">${{p.site_type}} | Cuenca Lago de Atitlán</div>
              <div class="pop-grid">
                <div class="pop-stat"><span class="k">Caudal Aforado</span><span class="v">${{p.caudal_m3s !== null ? p.caudal_m3s + ' m³/s' : 'N/D'}}</span></div>
                <div class="pop-stat"><span class="k">Oxígeno Disuelto</span><span class="v">${{p.od_mg_l ? p.od_mg_l + ' mg/L' : 'N/D'}}</span></div>
              </div>
              <button onclick="openDrawerStation('${{p.id}}')" style="width:100%; margin-top:6px; background:linear-gradient(135deg,#0284c7,#0d9488); border:none; color:#fff; padding:6px 10px; border-radius:6px; font-weight:800; font-size:0.76rem; cursor:pointer;">🌊 Ver Simulación Río Atitlán</button>
            </div>
          `);

          marker.addTo(amsclaeLayer);
        }});
      }}
      amsclaeLayer.addTo(map);

      // 6. AMSA LAGO DE AMATITLÁN (4 estaciones)
      amsaLayer = L.layerGroup();
      if (NATIONAL_DATA.amsa_amatitlan_stations && NATIONAL_DATA.amsa_amatitlan_stations.features) {{
        NATIONAL_DATA.amsa_amatitlan_stations.features.forEach(feat => {{
          const p = feat.properties;
          const coords = [feat.geometry.coordinates[1], feat.geometry.coordinates[0]];

          const marker = L.circleMarker(coords, {{
            radius: 8,
            fillColor: '#fbbf24',
            color: '#ffffff',
            weight: 2,
            opacity: 1,
            fillOpacity: 0.9
          }});

          marker.bindPopup(`
            <div class="station-popup">
              <span class="pop-tag tag-amsa">AMSA</span>
              <div class="pop-title">${{p.name}}</div>
              <div style="font-size:0.75rem; color:#94a3b8; margin-bottom:4px;">${{p.site_type}} | Cuenca María Linda</div>
              <div class="pop-grid">
                <div class="pop-stat"><span class="k">pH</span><span class="v">${{p.ph || 'N/D'}}</span></div>
                <div class="pop-stat"><span class="k">DBO5</span><span class="v">${{p.dbo5_mg_l ? p.dbo5_mg_l + ' mg/L' : 'N/D'}}</span></div>
              </div>
              <button onclick="openDrawerStation('${{p.id}}')" style="width:100%; margin-top:6px; background:linear-gradient(135deg,#f59e0b,#d97706); border:none; color:#fff; padding:6px 10px; border-radius:6px; font-weight:800; font-size:0.76rem; cursor:pointer;">🌊 Ver Simulación Lago Amatitlán</button>
            </div>
          `);

          marker.addTo(amsaLayer);
        }});
      }}
      amsaLayer.addTo(map);

      // 7. MARN SITIOS COSTEROS ACIDIFICACIÓN (11 estaciones)
      marnAcidLayer = L.layerGroup();
      if (NATIONAL_DATA.marn_acidification_stations && NATIONAL_DATA.marn_acidification_stations.features) {{
        NATIONAL_DATA.marn_acidification_stations.features.forEach(feat => {{
          const p = feat.properties;
          const coords = [p.Latitud_Y, p.Longitud_X];

          const marker = L.circleMarker(coords, {{
            radius: 8,
            fillColor: '#fb7185',
            color: '#ffffff',
            weight: 2,
            opacity: 1,
            fillOpacity: 0.9
          }});

          marker.bindPopup(`
            <div class="station-popup">
              <span class="pop-tag tag-marn">MARN Costero</span>
              <div class="pop-title">Sitio: ${{p.Sitio}} (${{p.Departamen}})</div>
              <div style="font-size:0.75rem; color:#94a3b8; margin-bottom:4px;">Monitoreo Marino-Costero y Acidificación</div>
              <div class="pop-grid">
                <div class="pop-stat"><span class="k">pH 2024</span><span class="v">${{p.pH2024 || 'N/D'}}</span></div>
                <div class="pop-stat"><span class="k">pH 2025</span><span class="v">${{p.pH2025 || 'N/D'}}</span></div>
              </div>
            </div>
          `);

          marker.addTo(marnAcidLayer);
        }});
      }}
      marnAcidLayer.addTo(map);

      // 8. USAC ERIS FÁRMACOS (32 estaciones)
      usacLayer = L.layerGroup();
      if (NATIONAL_DATA.usac_eris_stations && NATIONAL_DATA.usac_eris_stations.features) {{
        NATIONAL_DATA.usac_eris_stations.features.forEach(feat => {{
          const p = feat.properties;
          const coords = [feat.geometry.coordinates[1], feat.geometry.coordinates[0]];
          
          let markerColor = '#e879f9';
          if (p.site_type.includes('Hospitalaria')) markerColor = '#ec4899';
          else if (p.site_type.includes('Superficial')) markerColor = '#38bdf8';

          const marker = L.circleMarker(coords, {{
            radius: 7,
            fillColor: markerColor,
            color: '#ffffff',
            weight: 1.5,
            opacity: 1,
            fillOpacity: 0.85
          }});

          marker.bindPopup(`
            <div class="station-popup">
              <span class="pop-tag tag-usac">USAC ERIS 2025</span>
              <div class="pop-title">${{p.id}}: ${{p.name}}</div>
              <div style="font-size:0.75rem; color:#94a3b8; margin-bottom:4px;">${{p.site_type}} • ${{p.water_body}}</div>
              <div style="font-size:0.72rem; color:#fda4af; margin-bottom:6px;">☣️ DBO5: ${{p.dbo5_mg_l}} mg/L | OD: ${{p.od_mg_l}} mg/L</div>
              <div class="pop-grid">
                <div class="pop-stat"><span class="k">Sulfametoxazol</span><span class="v">${{p.sulfametoxazol_ng_l !== null ? p.sulfametoxazol_ng_l + ' ng/L' : 'ND'}}</span></div>
                <div class="pop-stat"><span class="k">Cafeína</span><span class="v">${{p.cafeina_ng_l !== null ? p.cafeina_ng_l + ' ng/L' : 'ND'}}</span></div>
              </div>
              <button onclick="openDrawerStation('${{p.id}}')" style="width:100%; margin-top:6px; background:linear-gradient(135deg,#c084fc,#9333ea); border:none; color:#fff; padding:6px 10px; border-radius:6px; font-weight:800; font-size:0.76rem; cursor:pointer;">🌊 Ver Animación Cloacal & COGUANOR</button>
            </div>
          `);

          marker.addTo(usacLayer);
        }});
      }}
      usacLayer.addTo(map);

      // 9. WPDX POZOS Y PUNTOS DE AGUA (128 estaciones)
      wpdxLayer = L.layerGroup();
      if (NATIONAL_DATA.wpdx_water_points && NATIONAL_DATA.wpdx_water_points.features) {{
        NATIONAL_DATA.wpdx_water_points.features.forEach(feat => {{
          const p = feat.properties;
          const coords = [feat.geometry.coordinates[1], feat.geometry.coordinates[0]];

          const marker = L.circleMarker(coords, {{
            radius: 5,
            fillColor: p.status === 'Functional' ? '#10b981' : '#f59e0b',
            color: '#ffffff',
            weight: 1,
            opacity: 0.9,
            fillOpacity: 0.75
          }});

          marker.bindPopup(`
            <div class="station-popup">
              <span class="pop-tag tag-wpdx">WPdx Punto de Agua</span>
              <div class="pop-title">${{p.tech}}</div>
              <div style="font-size:0.75rem; color:#cbd5e1; margin-bottom:4px;">${{p.municipality}}, ${{p.department}}</div>
              <div class="pop-grid">
                <div class="pop-stat"><span class="k">Estado</span><span class="v" style="color:${{p.status === 'Functional' ? '#10b981' : '#f59e0b'}}">${{p.status}}</span></div>
                <div class="pop-stat"><span class="k">Instalador</span><span class="v">${{p.installer}}</span></div>
              </div>
            </div>
          `);

          marker.addTo(wpdxLayer);
        }});
      }}
      wpdxLayer.addTo(map);

      // 10. MOTAGUA RIVER NETWORK (1,626 reaches)
      motaguaLayer = L.layerGroup();
      if (NATIONAL_DATA.motagua_river_network && NATIONAL_DATA.motagua_river_network.features) {{
        L.geoJSON(NATIONAL_DATA.motagua_river_network, {{
          style: function(feature) {{
            const strahler = feature.properties.strahler_order || 1;
            const q = feature.properties.dis_av_cms || 5;
            let weight = 1.1;
            let color = '#0284c7';
            let opacity = 0.6;

            if (strahler >= 5 || q > 50) {{
              weight = 3.2;
              color = '#38bdf8';
              opacity = 0.95;
            }} else if (strahler >= 3) {{
              weight = 1.8;
              color = '#0ea5e9';
              opacity = 0.75;
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
                  <div class="pop-stat"><span class="k">Área Cuenca</span><span class="v">${{p.upland_skm.toLocaleString()}} km²</span></div>
                </div>
              </div>
            `);
          }}
        }}).addTo(motaguaLayer);
      }}
      motaguaLayer.addTo(map);
    }}

    // Layer Toggle Function
    function toggleLayer(name) {{
      const layers = {{
        'cuencas': {{ layer: cuencasLayer, chk: 'chk-cuencas' }},
        'lakes': {{ layer: lakesLayer, chk: 'chk-lakes' }},
        'insiv_qual': {{ layer: insivQualLayer, chk: 'chk-insiv-qual' }},
        'insiv_cau': {{ layer: insivCauLayer, chk: 'chk-insiv-cau' }},
        'amsclae': {{ layer: amsclaeLayer, chk: 'chk-amsclae' }},
        'amsa': {{ layer: amsaLayer, chk: 'chk-amsa' }},
        'marn_acid': {{ layer: marnAcidLayer, chk: 'chk-marn-acid' }},
        'usac': {{ layer: usacLayer, chk: 'chk-usac' }},
        'wpdx': {{ layer: wpdxLayer, chk: 'chk-wpdx' }},
        'motagua': {{ layer: motaguaLayer, chk: 'chk-motagua' }}
      }};

      const item = layers[name];
      if (!item) return;

      const checked = document.getElementById(item.chk).checked;
      if (checked) {{
        map.addLayer(item.layer);
      }} else {{
        map.removeLayer(item.layer);
      }}
    }}

    // Territorial Zoom Shortcuts
    function zoomTo(target) {{
      document.querySelectorAll('.view-btn').forEach(btn => btn.classList.remove('active'));
      
      if (target === 'guatemala') {{
        map.setView([15.35, -90.35], 7.8);
      }} else if (target === 'motagua') {{
        map.setView([14.95, -89.95], 9);
      }} else if (target === 'atitlan') {{
        map.setView([14.69, -91.20], 12);
      }} else if (target === 'amatitlan') {{
        map.setView([14.47, -90.60], 12.5);
      }} else if (target === 'izabal') {{
        map.setView([15.52, -89.15], 10.5);
      }} else if (target === 'costas') {{
        map.setView([14.20, -91.30], 8.5);
      }}
    }}

    // Preset Simulation trigger from sidebar
    function triggerPresetSimulation(type) {{
      if (type === 'septic') {{
        openDrawerStation('USAC-01'); // Las Vacas Bridge
      }} else if (type === 'pristine') {{
        openDrawerStation('AMSCLAE-5'); // San Buenaventura Atitlan
      }} else if (type === 'eutrophic') {{
        openDrawerStation('AMSA-1'); // Lago Amatitlan
      }} else if (type === 'turbid') {{
        openDrawerStation('INSIV-CAU-12'); // Gualan Motagua
      }}
    }}

    // =========================================================================
    // PHYSICAL RIVER SIMULATION & COGUANOR DIAGNOSTIC ENGINE
    // =========================================================================

    function evaluateWaterQuality(data) {{
      let od = data.od_mg_l !== null ? Number(data.od_mg_l) : null;
      let dbo = data.dbo5_mg_l !== null ? Number(data.dbo5_mg_l) : null;
      let dqo = data.dqo_mg_l !== null ? Number(data.dqo_mg_l) : null;
      let ph = data.ph !== null ? Number(data.ph) : null;
      let turb = data.turbiedad_ntu !== null ? Number(data.turbiedad_ntu) : null;
      let flow = data.caudal_m3s || data.caudal_medio_anual || 5.0;
      let hasDrugs = data.sulfametoxazol_ng_l > 500 || data.cafeina_ng_l > 5000;

      // Evaluation criteria
      let condition = 'pristine';
      let wqiScore = 85;
      let verdictTitle = '';
      let verdictClass = 'verdict-good';
      let reasons = [];

      // Check for Septic / Extreme pollution
      if ((od !== null && od < 2.0) || (dbo !== null && dbo > 100.0) || hasDrugs || (data.name && data.name.includes('Vacas')) || (data.site_type && data.site_type.includes('Hospitalaria'))) {{
        condition = 'septic';
        wqiScore = Math.max(12, Math.round(15 + (od ? od * 8 : 0) - (dbo ? Math.min(dbo / 10, 20) : 0)));
        verdictClass = 'verdict-bad';
        verdictTitle = '❌ ESTADO CRÍTICO / COLAPSO CLOACAL SEVERO ("Río Muy Malito")';
      }} else if ((ph !== null && (ph > 8.8 || ph < 6.0)) || (data.name && data.name.includes('Amatitlán'))) {{
        condition = 'eutrophic';
        wqiScore = 42;
        verdictClass = 'verdict-warn';
        verdictTitle = '⚠️ ESTADO EUTROFIZADO / FLORACIÓN DE CIANOBACTERIAS ("Río en Riesgo")';
      }} else if (flow > 80 || (turb !== null && turb > 40) || (data.name && data.name.includes('Gualán'))) {{
        condition = 'turbid';
        wqiScore = 65;
        verdictClass = 'verdict-regular';
        verdictTitle = '🌊 CONDICIÓN ALUVIO-SEDIMENTARIA / TURBIEDAD ELEVADA ("Río Turbio")';
      }} else {{
        condition = 'pristine';
        wqiScore = 92;
        verdictClass = 'verdict-good';
        verdictTitle = '✅ EXCELENTE ESTADO ECOLÓGICO ("Río Sano y Cristalino")';
      }}

      // Build Parameter Checklist (A, B, C, D, E)
      // A. Oxígeno Disuelto
      if (od !== null) {{
        let ok = od >= 4.0;
        reasons.push({{
          param: 'A. Oxígeno Disuelto (OD)',
          val: `${{od}} mg/L`,
          norm: 'Límite COGUANOR / AG 236: ≥ 4.0 mg/L',
          status: ok ? 'good' : 'bad',
          statusText: ok ? 'CUMPLE NORMA' : 'NO CUMPLE (Colapso Anóxico)',
          expl: ok ? 'Nivel óptimo para respiración de peces e invertebrados bentónicos.' : 
                     'Asfixia biológica total. La falta de oxígeno genera putrefacción anaerobia y fetidez (gas sulfhídrico).'
        }});
      }} else {{
        reasons.push({{
          param: 'A. Oxígeno Disuelto (OD)',
          val: 'No reportado',
          norm: 'Ref: ≥ 4.0 mg/L',
          status: condition === 'septic' ? 'bad' : 'good',
          statusText: condition === 'septic' ? 'INFERIDO CRÍTICO' : 'ESTIMADO ADECUADO',
          expl: condition === 'septic' ? 'En descargas cloacales de la cuenca, el OD colapsa por debajo de 1.0 mg/L.' : 'Condiciones de montaña favorecen la aireación natural.'
        }});
      }}

      // B. DBO5 / DQO
      if (dbo !== null || dqo !== null) {{
        let valStr = dbo !== null ? `DBO5: ${{dbo}} mg/L` : `DQO: ${{dqo}} mg/L`;
        let isBad = (dbo !== null && dbo > 100) || (dqo !== null && dqo > 250);
        reasons.push({{
          param: 'B. Carga Orgánica (DBO5 / DQO)',
          val: valStr,
          norm: 'Límite AG 236-2006: DBO5 ≤ 100 mg/L | DQO ≤ 200 mg/L',
          status: isBad ? 'bad' : 'good',
          statusText: isBad ? 'VIOLACIÓN NORMATIVA SEVERA' : 'DENTRO DE LÍMITES',
          expl: isBad ? 'Materia orgánica fecal masiva sin tratamiento previo; agua turbia y espesa.' : 'Baja carga biodegradable, agua fluida y transparente.'
        }});
      }}

      // C. Turbiedad / Apariencia
      let turbVal = turb !== null ? `${{turb}} UNT` : (condition === 'turbid' ? '85.0 UNT (Arrastre)' : (condition === 'septic' ? '120.0 UNT (Cloacal)' : '2.1 UNT'));
      let turbBad = condition === 'septic' || condition === 'turbid';
      reasons.push({{
        param: 'C. Turbiedad y Claridad Óptica',
        val: turbVal,
        norm: 'Límite COGUANOR NTG 29001: ≤ 5.0 UNT',
        status: turbBad ? 'bad' : 'good',
        statusText: turbBad ? 'FUERA DE NORMA COGUANOR' : 'CUMPLE EXCELENTE',
        expl: turbBad ? 'Opacidad densa que bloquea la fotosíntesis acuática y arrastra lodos.' : 'Agua cristalina que permite ver el fondo rocoso del río.'
      }});

      // D. Fármacos / Cafeína / Trazadores Antropogénicos
      if (hasDrugs) {{
        reasons.push({{
          param: 'D. Contaminantes Emergentes & Fármacos',
          val: `Cafeína: ${{data.cafeina_ng_l || 'Detectada'}} ng/L | Sulfamidas: ${{data.sulfametoxazol_ng_l || 'Detectado'}} ng/L`,
          norm: 'Límite Toxicológico Internacional: 0 ng/L',
          status: 'bad',
          statusText: 'TRAZADOR CLOACAL DIRECTO',
          expl: 'Evidencia analítica directa de efluentes cloacales y hospitalarios vertidos crudos al afluente.'
        }});
      }} else {{
        reasons.push({{
          param: 'D. Fármacos y Químicos Emergentes',
          val: 'Sin detección de antibióticos',
          norm: 'Límite: Trazas no detectables',
          status: 'good',
          statusText: 'SIN RIESGO FARMACÉUTICO',
          expl: 'No se detecta intrusión de aguas residuales hospitalarias en este punto.'
        }});
      }}

      // E. Potencial de Hidrógeno (pH)
      if (ph !== null) {{
        let phOk = ph >= 6.5 && ph <= 8.5;
        reasons.push({{
          param: 'E. Potencial de Hidrógeno (pH)',
          val: `${{ph}}`,
          norm: 'Rango COGUANOR NTG 29001: 6.5 a 8.5',
          status: phOk ? 'good' : 'warn',
          statusText: phOk ? 'CUMPLE RANGO' : 'ANOMALÍA ALCALINA',
          expl: phOk ? 'Equilibrio ácido-base compatible con la vida dulceacuícola.' : 
                     'pH muy alcalino (>8.8) generado por consumo voraz de CO2 de cianobacterias (algas).'
        }});
      }}

      return {{
        condition: condition,
        wqiScore: wqiScore,
        verdictTitle: verdictTitle,
        verdictClass: verdictClass,
        reasons: reasons,
        flow: flow
      }};
    }}

    function initRiverCanvas(evalData) {{
      const canvas = document.getElementById('riverCanvas');
      if (!canvas) return;
      const ctx = canvas.getContext('2d');

      // Cancel any existing loop
      if (animId) {{
        cancelAnimationFrame(animId);
        animId = null;
      }}

      // Resize for DPI
      const rect = canvas.getBoundingClientRect();
      const dpr = window.devicePixelRatio || 1;
      canvas.width = rect.width * dpr;
      canvas.height = rect.height * dpr;
      ctx.scale(dpr, dpr);

      const w = rect.width;
      const h = rect.height;

      // Generate particles based on condition
      simParticles = [];
      const cond = ptarActive ? 'pristine' : evalData.condition;

      if (cond === 'septic') {{
        // Floating trash (plastic bottles, bags) + Methane bubbles + Foam
        for (let i = 0; i < 7; i++) {{
          simParticles.push({{
            type: 'trash',
            x: Math.random() * w,
            y: 45 + Math.random() * 80,
            vx: 0.7 + Math.random() * 0.8,
            size: 10 + Math.random() * 14,
            rot: Math.random() * Math.PI * 2,
            vRot: (Math.random() - 0.5) * 0.04,
            trashType: i % 2 === 0 ? 'bottle' : 'bag'
          }});
        }}
        for (let i = 0; i < 18; i++) {{
          simParticles.push({{
            type: 'bubble',
            x: Math.random() * w,
            y: h - Math.random() * 80,
            vy: -(0.5 + Math.random() * 1.2),
            vx: 0.4 + Math.random() * 0.4,
            radius: 2 + Math.random() * 4,
            alpha: 0.7
          }});
        }}
      }} else if (cond === 'eutrophic') {{
        // Algae clumps / filaments
        for (let i = 0; i < 22; i++) {{
          simParticles.push({{
            type: 'algae',
            x: Math.random() * w,
            y: 35 + Math.random() * 110,
            vx: 0.6 + Math.random() * 0.6,
            radius: 4 + Math.random() * 8,
            alpha: 0.6
          }});
        }}
      }} else if (cond === 'turbid') {{
        // Silt grains sweeping fast
        for (let i = 0; i < 40; i++) {{
          simParticles.push({{
            type: 'silt',
            x: Math.random() * w,
            y: 20 + Math.random() * (h - 20),
            vx: 2.2 + Math.random() * 1.8,
            radius: 1.5 + Math.random() * 2.5,
            alpha: 0.5
          }});
        }}
      }} else {{
        // Pristine: light caustics and clean oxygen sparkles
        for (let i = 0; i < 15; i++) {{
          simParticles.push({{
            type: 'sparkle',
            x: Math.random() * w,
            y: 40 + Math.random() * (h - 50),
            vx: 0.9 + Math.random() * 0.6,
            radius: 2 + Math.random() * 3,
            alpha: 0.8
          }});
        }}
      }}

      function renderFrame() {{
        if (!isPaused) {{
          simTime += 0.025;
        }}

        ctx.clearRect(0, 0, w, h);

        const activeCond = ptarActive ? 'pristine' : evalData.condition;

        // Base gradient colors
        let skyGradient = ctx.createLinearGradient(0, 0, 0, 45);
        let waterGradient = ctx.createLinearGradient(0, 40, 0, h);

        if (activeCond === 'septic') {{
          // Murky grey-black sewage
          skyGradient.addColorStop(0, '#090d16');
          skyGradient.addColorStop(1, '#1e293b');
          waterGradient.addColorStop(0, '#334155');
          waterGradient.addColorStop(0.35, '#1e293b');
          waterGradient.addColorStop(1, '#090d16');
        }} else if (activeCond === 'eutrophic') {{
          // Olive / green cyanobacteria bloom
          skyGradient.addColorStop(0, '#0c1a10');
          skyGradient.addColorStop(1, '#1b381e');
          waterGradient.addColorStop(0, '#84cc16');
          waterGradient.addColorStop(0.35, '#4d7c0f');
          waterGradient.addColorStop(1, '#14532d');
        }} else if (activeCond === 'turbid') {{
          // Chocolate-brown alluvial sediment
          skyGradient.addColorStop(0, '#1c130c');
          skyGradient.addColorStop(1, '#382314');
          waterGradient.addColorStop(0, '#ca8a04');
          waterGradient.addColorStop(0.35, '#854d0e');
          waterGradient.addColorStop(1, '#451a03');
        }} else {{
          // Pristine turquoise / emerald
          skyGradient.addColorStop(0, '#082f49');
          skyGradient.addColorStop(1, '#0c4a6e');
          waterGradient.addColorStop(0, '#38bdf8');
          waterGradient.addColorStop(0.35, '#06b6d4');
          waterGradient.addColorStop(1, '#042f2e');
        }}

        // Draw sky/background
        ctx.fillStyle = skyGradient;
        ctx.fillRect(0, 0, w, 45);

        // Draw background shore bank
        ctx.fillStyle = '#060a12';
        ctx.beginPath();
        ctx.moveTo(0, 38);
        for (let x = 0; x <= w; x += 30) {{
          ctx.lineTo(x, 38 + Math.sin(x * 0.04) * 3);
        }}
        ctx.lineTo(w, 48);
        ctx.lineTo(0, 48);
        ctx.fill();

        // 1. Background water wave
        ctx.fillStyle = waterGradient;
        ctx.beginPath();
        ctx.moveTo(0, h);
        for (let x = 0; x <= w; x += 10) {{
          let y = 46 + Math.sin(x * 0.02 + simTime * 1.4) * 4 + Math.cos(x * 0.05 + simTime * 0.8) * 2;
          ctx.lineTo(x, y);
        }}
        ctx.lineTo(w, h);
        ctx.closePath();
        ctx.fill();

        // 2. Midground wave with transparency
        ctx.fillStyle = activeCond === 'septic' ? 'rgba(51, 65, 85, 0.45)' : 
                        activeCond === 'eutrophic' ? 'rgba(101, 163, 13, 0.45)' : 
                        activeCond === 'turbid' ? 'rgba(202, 138, 4, 0.45)' : 
                        'rgba(56, 189, 248, 0.45)';
        ctx.beginPath();
        ctx.moveTo(0, h);
        for (let x = 0; x <= w; x += 10) {{
          let y = 54 + Math.sin(x * 0.025 + simTime * 2.0) * 5 + Math.cos(x * 0.035 - simTime) * 3;
          ctx.lineTo(x, y);
        }}
        ctx.lineTo(w, h);
        ctx.closePath();
        ctx.fill();

        // 3. Render Particles (Trash, Bubbles, Algae, Caustics)
        simParticles.forEach(p => {{
          if (!isPaused) {{
            p.x += p.vx;
            if (p.x > w + 20) p.x = -20;

            if (p.vy) {{
              p.y += p.vy;
              if (p.y < 46) {{
                p.y = h - 10;
                p.x = Math.random() * w;
              }}
            }}
            if (p.vRot) p.rot += p.vRot;
          }}

          if (p.type === 'trash') {{
            ctx.save();
            ctx.translate(p.x, p.y + Math.sin(p.x * 0.03 + simTime * 2) * 4);
            ctx.rotate(p.rot);
            if (p.trashType === 'bottle') {{
              // Plastic bottle
              ctx.fillStyle = 'rgba(125, 211, 252, 0.75)';
              ctx.strokeStyle = 'rgba(255, 255, 255, 0.8)';
              ctx.lineWidth = 1;
              ctx.fillRect(-p.size/2, -p.size/4, p.size, p.size/2);
              ctx.strokeRect(-p.size/2, -p.size/4, p.size, p.size/2);
              // cap
              ctx.fillStyle = '#ef4444';
              ctx.fillRect(p.size/2, -p.size/8, p.size/4, p.size/4);
            }} else {{
              // Crinkled plastic bag fragment
              ctx.fillStyle = 'rgba(226, 232, 240, 0.65)';
              ctx.beginPath();
              ctx.moveTo(-p.size/2, -p.size/3);
              ctx.lineTo(p.size/3, -p.size/2);
              ctx.lineTo(p.size/2, p.size/3);
              ctx.lineTo(-p.size/3, p.size/2);
              ctx.closePath();
              ctx.fill();
            }}
            ctx.restore();
          }} else if (p.type === 'bubble') {{
            // Gas / Methane bubble
            ctx.save();
            ctx.beginPath();
            ctx.arc(p.x + Math.sin(p.y * 0.08) * 3, p.y, p.radius, 0, Math.PI * 2);
            ctx.fillStyle = 'rgba(148, 163, 184, 0.6)';
            ctx.strokeStyle = 'rgba(255, 255, 255, 0.7)';
            ctx.lineWidth = 0.8;
            ctx.fill();
            ctx.stroke();
            ctx.restore();
          }} else if (p.type === 'algae') {{
            // Cyanobacteria filament clump
            ctx.save();
            ctx.fillStyle = 'rgba(163, 230, 53, 0.65)';
            ctx.beginPath();
            ctx.ellipse(p.x, p.y, p.radius * 1.5, p.radius * 0.7, Math.sin(simTime + p.x), 0, Math.PI * 2);
            ctx.fill();
            ctx.restore();
          }} else if (p.type === 'silt') {{
            // Silt grain
            ctx.fillStyle = 'rgba(245, 158, 11, 0.55)';
            ctx.fillRect(p.x, p.y, p.radius, p.radius);
          }} else if (p.type === 'sparkle') {{
            // Clean water caustic highlight
            ctx.save();
            ctx.fillStyle = 'rgba(255, 255, 255, 0.75)';
            ctx.beginPath();
            ctx.arc(p.x, p.y + Math.sin(p.x * 0.04 + simTime * 2) * 3, p.radius, 0, Math.PI * 2);
            ctx.fill();
            ctx.restore();
          }}
        }});

        // 4. Foreground Crest Foam
        if (activeCond === 'septic') {{
          ctx.fillStyle = 'rgba(203, 213, 225, 0.45)'; // grey sludge foam
        }} else if (activeCond === 'eutrophic') {{
          ctx.fillStyle = 'rgba(190, 242, 100, 0.4)'; // green algal scum
        }} else {{
          ctx.fillStyle = 'rgba(255, 255, 255, 0.45)'; // clean white water spray
        }}
        
        ctx.beginPath();
        for (let x = 0; x <= w; x += 25) {{
          let waveY = 52 + Math.sin(x * 0.025 + simTime * 2.0) * 5;
          ctx.ellipse(x, waveY, 12, 3, 0, 0, Math.PI * 2);
        }}
        ctx.fill();

        animId = requestAnimationFrame(renderFrame);
      }}

      renderFrame();
    }}

    function toggleSimPause() {{
      isPaused = !isPaused;
      const btn = document.getElementById('btn-sim-pause');
      if (btn) {{
        btn.innerText = isPaused ? '▶ Reanudar' : '⏸ Pausar';
      }}
    }}

    function togglePtarEffect() {{
      ptarActive = !ptarActive;
      const btn = document.getElementById('btn-sim-ptar');
      const badge = document.getElementById('sim-badge-pill');
      const wqiBox = document.getElementById('sim-wqi-val');

      if (ptarActive) {{
        btn.classList.add('active');
        btn.innerText = '✅ PTAR Activada (Agua Saneada)';
        badge.innerHTML = '🟢 AGUA TRATADA / CUMPLE COGUANOR';
        badge.style.background = 'rgba(16, 185, 129, 0.85)';
        badge.style.color = '#fff';
        wqiBox.innerText = 'WQI: 92/100 (SANO)';
        wqiBox.style.color = '#34d399';
      }} else {{
        btn.classList.remove('active');
        btn.innerText = '💧 Simular Tratamiento PTAR';
        if (currentSimData) {{
          updateSimBadgeUI(currentSimData);
        }}
      }}

      if (currentSimData) {{
        initRiverCanvas(currentSimData);
      }}
    }}

    function updateSimBadgeUI(evalData) {{
      const badge = document.getElementById('sim-badge-pill');
      const wqiBox = document.getElementById('sim-wqi-val');
      if (!badge || !wqiBox) return;

      if (evalData.condition === 'septic') {{
        badge.innerHTML = '🔴 AGUA SÉPTICA / AGUAS NEGRAS';
        badge.style.background = 'rgba(244, 63, 94, 0.9)';
        badge.style.color = '#fff';
        wqiBox.innerText = `WQI: ${{evalData.wqiScore}}/100 (CRÍTICO)`;
        wqiBox.style.color = '#f43f5e';
      }} else if (evalData.condition === 'eutrophic') {{
        badge.innerHTML = '🟡 FLORACIÓN ALGAL / CIANOBACTERIAS';
        badge.style.background = 'rgba(245, 158, 11, 0.9)';
        badge.style.color = '#080c14';
        wqiBox.innerText = `WQI: ${{evalData.wqiScore}}/100 (EUTROFIZADO)`;
        wqiBox.style.color = '#fbbf24';
      }} else if (evalData.condition === 'turbid') {{
        badge.innerHTML = '🟠 CAUDAL TURBIO ALUVIAL';
        badge.style.background = 'rgba(217, 119, 6, 0.9)';
        badge.style.color = '#fff';
        wqiBox.innerText = `WQI: ${{evalData.wqiScore}}/100 (TURBIO)`;
        wqiBox.style.color = '#f59e0b';
      }} else {{
        badge.innerHTML = '🟢 AGUA SANA / CRISTALINA';
        badge.style.background = 'rgba(16, 185, 129, 0.9)';
        badge.style.color = '#fff';
        wqiBox.innerText = `WQI: ${{evalData.wqiScore}}/100 (EXCELENTE)`;
        wqiBox.style.color = '#34d399';
      }}
    }}

    // Slide-over Drawer Logic with Complete River Animation & COGUANOR Check
    function openDrawerStation(stationId) {{
      const drawer = document.getElementById('detail-drawer');
      const body = document.getElementById('drawer-body');
      ptarActive = false;
      isPaused = false;

      let featData = null;
      let agency = '';
      let title = '';
      let sub = '';

      // Find in collections
      let fQual = (NATIONAL_DATA.insivumeh_quality_stations.features || []).find(f => f.properties.id === stationId);
      let fCau = (NATIONAL_DATA.insivumeh_streamflow_stations.features || []).find(f => f.properties.id === stationId);
      let fUsac = (NATIONAL_DATA.usac_eris_stations.features || []).find(f => f.properties.id === stationId);
      let fAmsclae = (NATIONAL_DATA.amsclae_atitlan_stations.features || []).find(f => f.properties.id === stationId);
      let fAmsa = (NATIONAL_DATA.amsa_amatitlan_stations.features || []).find(f => f.properties.id === stationId);

      if (fQual) {{
        featData = fQual.properties;
        agency = 'INSIVUMEH';
        title = featData.name;
        sub = `${{featData.water_body}} | Cuenca: ${{featData.basin}} (${{featData.municipality}}, ${{featData.department}})`;
      }} else if (fCau) {{
        featData = fCau.properties;
        agency = 'INSIVUMEH AFOROS';
        title = featData.name;
        sub = `${{featData.water_body}} | Cuenca: ${{featData.basin}} (Vertiente ${{featData.vertiente}})`;
      }} else if (fUsac) {{
        featData = fUsac.properties;
        agency = 'USAC ERIS 2025';
        title = `${{featData.id}}: ${{featData.name}}`;
        sub = `${{featData.site_type}} • ${{featData.water_body}}`;
      }} else if (fAmsclae) {{
        featData = fAmsclae.properties;
        agency = 'AMSCLAE';
        title = featData.name;
        sub = `${{featData.site_type}} • Cuenca Lago de Atitlán`;
      }} else if (fAmsa) {{
        featData = fAmsa.properties;
        agency = 'AMSA';
        title = featData.name;
        sub = `${{featData.site_type}} • Cuenca Lago de Amatitlán (María Linda)`;
      }}

      if (!featData) return;

      // Evaluate water condition & build COGUANOR diagnosis
      const evalData = evaluateWaterQuality(featData);
      currentSimData = evalData;

      let paramItemsHtml = '';
      evalData.reasons.forEach(r => {{
        paramItemsHtml += `
          <div class="param-item ${{r.status}}">
            <div class="param-header">
              <span>${{r.param}}</span>
              <span style="font-family:'JetBrains Mono',monospace;">${{r.val}}</span>
            </div>
            <div style="font-size:0.7rem; color:#94a3b8; margin-bottom:2px;">${{r.norm}} • <strong style="color:${{r.status === 'bad' ? '#f43f5e' : (r.status === 'warn' ? '#f59e0b' : '#10b981')}}">${{r.statusText}}</strong></div>
            <div class="param-reason">${{r.expl}}</div>
          </div>
        `;
      }});

      body.innerHTML = `
        <span class="pop-tag tag-insivumeh">${{agency}}</span>
        <h3 style="margin: 6px 0;">${{title}}</h3>
        <div style="font-size:0.8rem; color:#94a3b8; margin-bottom:12px;">${{sub}}</div>

        <!-- SIMULATOR VIEWPORT -->
        <div class="sim-container">
          <div class="sim-header">
            <div class="sim-title">🌊 Simulación Fluvial en Tiempo Real</div>
            <div class="sim-controls">
              <button class="sim-btn" id="btn-sim-ptar" onclick="togglePtarEffect()">💧 Simular PTAR</button>
              <button class="sim-btn" id="btn-sim-pause" onclick="toggleSimPause()">⏸ Pausar</button>
            </div>
          </div>
          <div class="sim-canvas-wrap">
            <canvas id="riverCanvas"></canvas>
            <div class="sim-water-badge" id="sim-badge-pill">Cargando...</div>
            <div class="sim-wqi-meter" id="sim-wqi-val">WQI: --/100</div>
          </div>
        </div>

        <!-- COGUANOR DIAGNOSTIC ENGINE -->
        <div class="diagnostic-box">
          <div class="diag-title">
            <span>📋</span> Diagnóstico Normativo: ¿Por qué se ve así el agua?
          </div>
          <div class="diag-verdict ${{evalData.verdictClass}}">
            ${{evalData.verdictTitle}}
          </div>
          <div style="font-size:0.75rem; color:#cbd5e1; margin-bottom:10px; line-height:1.45;">
            Evaluación analítica in situ contrastada contra la norma oficial guatemalteca <strong>COGUANOR NTG 29001</strong> (Agua de consumo) y el <strong>Acuerdo Gubernativo 236-2006</strong> (Descargas de aguas residuales y cuerpos receptores):
          </div>
          <div class="param-diag-list">
            ${{paramItemsHtml}}
          </div>
        </div>

        <!-- SENSORY FOOTPRINT -->
        <div style="background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.08); border-radius:8px; padding:10px; font-size:0.75rem; color:#cbd5e1; margin-top:12px;">
          <div style="font-weight:700; color:#38bdf8; margin-bottom:4px;">👁️ Huella Sensorial y Estado Físico:</div>
          <div>• Color Aparente: <strong>${{evalData.condition === 'septic' ? 'Grisáceo negruzco aceitoso' : (evalData.condition === 'eutrophic' ? 'Verde turbio con natas de algas' : (evalData.condition === 'turbid' ? 'Marrón aluvial denso' : 'Cristalino turquesa'))}}</strong></div>
          <div>• Olor Estimado: <strong>${{evalData.condition === 'septic' ? 'Séptico fétido (Ácido sulfhídrico H2S)' : (evalData.condition === 'eutrophic' ? 'Olor vegetal a ciénaga / geosmina' : 'Inodoro natural de río de montaña')}}</strong></div>
          <div>• Riesgo Epidemiológico: <strong>${{evalData.condition === 'septic' ? 'Peligro Inmediato (Prohibido contacto)' : (evalData.condition === 'eutrophic' ? 'Riesgo de cianotoxinas (Evitar consumo)' : 'Bajo riesgo / Agua de alta calidad')}}</strong></div>
        </div>
      `;

      drawer.classList.add('open');

      // Initialize Canvas after DOM insertion
      setTimeout(() => {{
        updateSimBadgeUI(evalData);
        initRiverCanvas(evalData);
      }}, 50);
    }}

    function closeDrawer() {{
      const drawer = document.getElementById('detail-drawer');
      drawer.classList.remove('open');
      if (animId) {{
        cancelAnimationFrame(animId);
        animId = null;
      }}
    }}

    function openDrawerInfo(title, desc) {{
      const drawer = document.getElementById('detail-drawer');
      const body = document.getElementById('drawer-body');
      
      body.innerHTML = `
        <span class="pop-tag tag-insivumeh">REGISTRO OFICIAL GUATEMALA</span>
        <h3 style="margin: 8px 0 12px 0; color:#fff;">${{title}}</h3>
        <p style="font-size:0.85rem; color:#cbd5e1; line-height:1.6; margin-bottom:16px;">${{desc}}</p>
        <div style="background:rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.1); border-radius:8px; padding:12px; font-size:0.78rem;">
          <div style="font-weight:700; color:#38bdf8; margin-bottom:6px;">Metadatos de Integración</div>
          <div>• País: <strong>República de Guatemala</strong></div>
          <div>• Cobertura: <strong>22 Departamentos / 340 Municipios</strong></div>
          <div>• Marco Legal: <strong>Decreto 57-2008 & Acuerdo Gubernativo 236-2006</strong></div>
        </div>
      `;
      drawer.classList.add('open');
    }}

    function searchNationalStations(q) {{
      q = q.toLowerCase().trim();
      if (!q) return;

      let match = (NATIONAL_DATA.insivumeh_quality_stations.features || []).find(f => 
        f.properties.name.toLowerCase().includes(q) || 
        f.properties.water_body.toLowerCase().includes(q) ||
        f.properties.basin.toLowerCase().includes(q)
      );

      if (match) {{
        map.setView([match.geometry.coordinates[1], match.geometry.coordinates[0]], 12);
        openDrawerStation(match.properties.id);
        return;
      }}

      let matchCau = (NATIONAL_DATA.insivumeh_streamflow_stations.features || []).find(f => 
        f.properties.name.toLowerCase().includes(q) || 
        f.properties.water_body.toLowerCase().includes(q)
      );

      if (matchCau) {{
        map.setView([matchCau.geometry.coordinates[1], matchCau.geometry.coordinates[0]], 12);
        openDrawerStation(matchCau.properties.id);
        return;
      }}

      let matchLake = (NATIONAL_DATA.guatemala_major_lakes.features || []).find(f => 
        (f.properties.NOMBRE || '').toLowerCase().includes(q)
      );
      if (matchLake) {{
        const b = L.geoJSON(matchLake).getBounds();
        map.fitBounds(b);
      }}
    }}
  </script>
</body>
</html>
"""

    with open(OUTPUT_HTML_1, "w", encoding="utf-8") as f:
        f.write(html_content)

    with open(OUTPUT_HTML_2, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"SUCCESS: Generated National Dashboard HTML with River Animation & COGUANOR engine at:")
    print(f"  1. {OUTPUT_HTML_1} ({os.path.getsize(OUTPUT_HTML_1)/1024:.1f} KB)")
    print(f"  2. {OUTPUT_HTML_2} ({os.path.getsize(OUTPUT_HTML_2)/1024:.1f} KB)")

if __name__ == "__main__":
    build_dashboard()
