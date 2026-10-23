import os
import json
import pandas as pd

base_dir = "D:/Documentos D/BaseDatosGT H2O/Investigación Antigravity"
inv_csv = os.path.join(base_dir, "inventories/master_data_inventory.csv")
src_csv = os.path.join(base_dir, "inventories/source_summary.csv")
mis_csv = os.path.join(base_dir, "inventories/missing_data_register.csv")
usac_csv = os.path.join(base_dir, "data/processed/USAC_ERIS_Motagua_LasVacas_2025_Monitoring_Data.csv")
plastics_csv = os.path.join(base_dir, "data/processed/Guatemala_River_Plastic_Outlets_Meijer2021.csv")
flux_csv = os.path.join(base_dir, "data/processed/TheOceanCleanup_Motagua_Morales_2019_Flux.csv")

df_inv = pd.read_csv(inv_csv)
df_src = pd.read_csv(src_csv)
df_mis = pd.read_csv(mis_csv)
df_usac = pd.read_csv(usac_csv)
df_plastics = pd.read_csv(plastics_csv)

# Convert to JSON for embedding
inv_json = df_inv.to_json(orient='records')
src_json = df_src.to_json(orient='records')
mis_json = df_mis.to_json(orient='records')
usac_sample = df_usac.head(15).to_json(orient='records')
plastics_sample = df_plastics.head(15).to_json(orient='records')

html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>RÍOS ABIERTOS GT — Doomscrolling de Resultados | Antigravity vs ChatGPT vs Claude</title>
  <style>
    :root {{
      --bg: #090d16;
      --bg-card: rgba(16, 24, 40, 0.85);
      --bg-card-hover: rgba(23, 34, 57, 0.95);
      --border: rgba(56, 189, 248, 0.2);
      --border-glow: rgba(56, 189, 248, 0.5);
      --text: #f1f5f9;
      --text-muted: #94a3b8;
      --accent: #38bdf8;
      --accent-teal: #2dd4bf;
      --accent-emerald: #34d399;
      --accent-purple: #c084fc;
      --accent-amber: #fbbf24;
      --accent-rose: #fb7185;
      --badge-bg: rgba(56, 189, 248, 0.12);
      --shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.7);
    }}

    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}

    html {{
      scroll-behavior: smooth;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      background-color: var(--bg);
      color: var(--text);
    }}

    /* Scroll progress bar */
    #progress-container {{
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 5px;
      background: rgba(255, 255, 255, 0.05);
      z-index: 1000;
    }}
    #progress-bar {{
      height: 100%;
      width: 0%;
      background: linear-gradient(90deg, #38bdf8, #2dd4bf, #c084fc);
      box-shadow: 0 0 10px #38bdf8;
      transition: width 0.1s ease-out;
    }}

    /* Sticky Navigation HUD */
    nav.hud {{
      position: sticky;
      top: 5px;
      z-index: 999;
      backdrop-filter: blur(16px);
      -webkit-backdrop-filter: blur(16px);
      background: rgba(9, 13, 22, 0.8);
      border-bottom: 1px solid var(--border);
      padding: 12px 24px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
    }}
    .hud-brand {{
      display: flex;
      align-items: center;
      gap: 10px;
      font-weight: 800;
      font-size: 1.1rem;
      letter-spacing: -0.5px;
      color: #fff;
    }}
    .hud-brand span.tag {{
      background: linear-gradient(135deg, #0284c7, #0d9488);
      padding: 3px 8px;
      border-radius: 6px;
      font-size: 0.75rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }}
    .hud-links {{
      display: flex;
      gap: 8px;
      overflow-x: auto;
      padding-bottom: 2px;
      scrollbar-width: none;
    }}
    .hud-links::-webkit-scrollbar {{ display: none; }}
    .hud-btn {{
      padding: 6px 14px;
      border-radius: 20px;
      background: rgba(255, 255, 255, 0.06);
      color: var(--text-muted);
      text-decoration: none;
      font-size: 0.85rem;
      font-weight: 600;
      white-space: nowrap;
      transition: all 0.2s ease;
      border: 1px solid transparent;
    }}
    .hud-btn:hover, .hud-btn.active {{
      background: rgba(56, 189, 248, 0.15);
      color: var(--accent);
      border-color: var(--border);
    }}

    /* Container */
    .container {{
      max-width: 1200px;
      margin: 0 auto;
      padding: 40px 20px 100px 20px;
    }}

    /* Hero Section */
    .hero {{
      text-align: center;
      padding: 60px 20px 40px 20px;
      position: relative;
    }}
    .hero-badge {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 6px 16px;
      background: rgba(56, 189, 248, 0.1);
      border: 1px solid var(--border);
      border-radius: 30px;
      font-size: 0.85rem;
      font-weight: 600;
      color: var(--accent);
      margin-bottom: 20px;
    }}
    .hero h1 {{
      font-size: clamp(2.2rem, 5vw, 3.6rem);
      font-weight: 900;
      letter-spacing: -1.5px;
      line-height: 1.15;
      margin-bottom: 20px;
      background: linear-gradient(135deg, #ffffff 40%, #94a3b8 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }}
    .hero p.lead {{
      font-size: 1.2rem;
      color: var(--text-muted);
      max-width: 780px;
      margin: 0 auto 35px auto;
      line-height: 1.6;
    }}

    /* Stat Cards Banner */
    .stats-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 16px;
      margin-bottom: 50px;
    }}
    .stat-card {{
      background: var(--bg-card);
      border: 1px solid var(--border);
      padding: 22px;
      border-radius: 16px;
      text-align: center;
      box-shadow: var(--shadow);
      position: relative;
      overflow: hidden;
      transition: transform 0.2s, border-color 0.2s;
    }}
    .stat-card:hover {{
      transform: translateY(-4px);
      border-color: var(--accent);
    }}
    .stat-card .val {{
      font-size: 2.4rem;
      font-weight: 900;
      letter-spacing: -1px;
      margin-bottom: 4px;
      background: linear-gradient(135deg, #38bdf8, #2dd4bf);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }}
    .stat-card .lbl {{
      font-size: 0.85rem;
      font-weight: 600;
      color: var(--text-muted);
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }}
    .stat-card .sub {{
      font-size: 0.75rem;
      color: #64748b;
      margin-top: 4px;
    }}

    /* Section Headings */
    .section-header {{
      margin: 60px 0 25px 0;
      display: flex;
      flex-direction: column;
      gap: 6px;
    }}
    .section-tag {{
      color: var(--accent);
      font-size: 0.8rem;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 1.5px;
    }}
    .section-title {{
      font-size: clamp(1.6rem, 3vw, 2.2rem);
      font-weight: 800;
      letter-spacing: -0.8px;
    }}
    .section-desc {{
      color: var(--text-muted);
      font-size: 1rem;
      max-width: 800px;
      line-height: 1.5;
    }}

    /* Comparison Matrix Hero (Antigravity vs ChatGPT vs Claude) */
    .comp-table-card {{
      background: var(--bg-card);
      border: 1px solid var(--border);
      border-radius: 18px;
      padding: 25px;
      box-shadow: var(--shadow);
      margin-bottom: 40px;
      overflow-x: auto;
    }}
    table.comp-table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 0.92rem;
      text-align: left;
    }}
    table.comp-table th, table.comp-table td {{
      padding: 14px 16px;
      border-bottom: 1px solid rgba(255, 255, 255, 0.08);
      vertical-align: top;
    }}
    table.comp-table th {{
      color: var(--text-muted);
      font-size: 0.8rem;
      text-transform: uppercase;
      letter-spacing: 1px;
      background: rgba(255, 255, 255, 0.02);
    }}
    table.comp-table tr.highlight {{
      background: rgba(56, 189, 248, 0.04);
    }}
    .agent-pill {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 4px 10px;
      border-radius: 12px;
      font-size: 0.8rem;
      font-weight: 700;
    }}
    .pill-antigravity {{ background: rgba(56, 189, 248, 0.2); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.4); }}
    .pill-chatgpt {{ background: rgba(16, 185, 129, 0.2); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.4); }}
    .pill-claude {{ background: rgba(217, 119, 6, 0.2); color: #fbbf24; border: 1px solid rgba(217, 119, 6, 0.4); }}

    /* Doomscroll Feed Filter */
    .filter-bar {{
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
      margin-bottom: 25px;
      position: sticky;
      top: 60px;
      z-index: 900;
      background: var(--bg);
      padding: 10px 0;
    }}
    .filter-chip {{
      padding: 7px 16px;
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-radius: 20px;
      color: var(--text-muted);
      cursor: pointer;
      font-size: 0.85rem;
      font-weight: 600;
      transition: all 0.2s;
    }}
    .filter-chip:hover, .filter-chip.active {{
      background: var(--accent);
      color: #000;
      border-color: var(--accent);
    }}

    /* Card Feed Items */
    .feed {{
      display: flex;
      flex-direction: column;
      gap: 20px;
    }}
    .feed-card {{
      background: var(--bg-card);
      border: 1px solid var(--border);
      border-radius: 16px;
      padding: 24px;
      box-shadow: var(--shadow);
      transition: all 0.25s ease;
      display: flex;
      flex-direction: column;
      gap: 14px;
      position: relative;
    }}
    .feed-card:hover {{
      border-color: var(--border-glow);
      background: var(--bg-card-hover);
      transform: translateY(-2px);
    }}
    .card-top {{
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      gap: 12px;
      flex-wrap: wrap;
    }}
    .card-id {{
      font-family: monospace;
      font-size: 0.8rem;
      color: var(--accent);
      background: rgba(56, 189, 248, 0.1);
      padding: 3px 8px;
      border-radius: 6px;
      border: 1px solid rgba(56, 189, 248, 0.2);
    }}
    .card-org {{
      font-weight: 700;
      color: #e2e8f0;
      font-size: 0.95rem;
    }}
    .card-badges {{
      display: flex;
      gap: 6px;
      flex-wrap: wrap;
    }}
    .badge {{
      font-size: 0.72rem;
      font-weight: 700;
      padding: 3px 8px;
      border-radius: 10px;
      text-transform: uppercase;
      letter-spacing: 0.4px;
    }}
    .badge-downloaded {{ background: rgba(52, 211, 153, 0.18); color: #34d399; border: 1px solid rgba(52, 211, 153, 0.3); }}
    .badge-exclusive {{ background: rgba(192, 132, 252, 0.2); color: #c084fc; border: 1px solid rgba(192, 132, 252, 0.4); }}
    .badge-geo {{ background: rgba(56, 189, 248, 0.18); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.3); }}
    .badge-verified {{ background: rgba(45, 212, 191, 0.18); color: #2dd4bf; border: 1px solid rgba(45, 212, 191, 0.3); }}
    .badge-restricted {{ background: rgba(251, 113, 133, 0.18); color: #fb7185; border: 1px solid rgba(251, 113, 133, 0.3); }}

    .card-title {{
      font-size: 1.25rem;
      font-weight: 800;
      line-height: 1.35;
      color: #fff;
    }}
    .card-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 12px;
      background: rgba(0, 0, 0, 0.25);
      padding: 14px;
      border-radius: 10px;
      font-size: 0.88rem;
    }}
    .grid-item span.lbl {{
      display: block;
      color: var(--text-muted);
      font-size: 0.75rem;
      text-transform: uppercase;
      font-weight: 700;
      margin-bottom: 2px;
    }}
    .grid-item span.val {{
      color: #cbd5e1;
      font-weight: 500;
    }}

    .card-notes {{
      font-size: 0.9rem;
      color: #94a3b8;
      line-height: 1.5;
      border-left: 3px solid var(--accent);
      padding-left: 12px;
    }}
    .card-actions {{
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
      margin-top: 4px;
    }}
    .btn-action {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 8px 14px;
      border-radius: 8px;
      font-size: 0.82rem;
      font-weight: 700;
      text-decoration: none;
      transition: all 0.2s;
    }}
    .btn-primary {{
      background: linear-gradient(135deg, #0284c7, #0284c7);
      color: #fff;
    }}
    .btn-primary:hover {{
      background: #0ea5e9;
    }}
    .btn-secondary {{
      background: rgba(255, 255, 255, 0.08);
      color: #cbd5e1;
      border: 1px solid rgba(255, 255, 255, 0.12);
    }}
    .btn-secondary:hover {{
      background: rgba(255, 255, 255, 0.14);
      color: #fff;
    }}

    /* Interactive Comparison Checklist */
    .checklist-card {{
      background: var(--bg-card);
      border: 1px solid var(--border);
      border-radius: 18px;
      padding: 28px;
      box-shadow: var(--shadow);
      margin-bottom: 40px;
    }}
    .check-item {{
      display: flex;
      align-items: flex-start;
      gap: 14px;
      padding: 14px;
      border-bottom: 1px solid rgba(255, 255, 255, 0.06);
      transition: background 0.2s;
    }}
    .check-item:hover {{
      background: rgba(255, 255, 255, 0.02);
    }}
    .check-item input[type="checkbox"] {{
      margin-top: 4px;
      width: 18px;
      height: 18px;
      accent-color: var(--accent);
      cursor: pointer;
    }}
    .check-content {{
      flex: 1;
    }}
    .check-title {{
      font-weight: 700;
      font-size: 1rem;
      color: #fff;
      margin-bottom: 4px;
    }}
    .check-desc {{
      font-size: 0.88rem;
      color: var(--text-muted);
      line-height: 1.45;
    }}
    .check-tags {{
      display: flex;
      gap: 6px;
      margin-top: 6px;
    }}

    /* Data Table Preview */
    .preview-box {{
      background: rgba(0, 0, 0, 0.4);
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: 10px;
      overflow-x: auto;
      margin-top: 10px;
    }}
    table.data-preview {{
      width: 100%;
      border-collapse: collapse;
      font-size: 0.8rem;
      font-family: monospace;
    }}
    table.data-preview th, table.data-preview td {{
      padding: 8px 12px;
      border-bottom: 1px solid rgba(255, 255, 255, 0.05);
      white-space: nowrap;
    }}
    table.data-preview th {{
      background: rgba(255, 255, 255, 0.05);
      color: var(--accent);
      text-align: left;
    }}

    /* Footer */
    footer {{
      text-align: center;
      padding: 60px 20px;
      color: #64748b;
      font-size: 0.85rem;
      border-top: 1px solid rgba(255, 255, 255, 0.06);
    }}
  </style>
</head>
<body>

  <!-- Scroll Progress -->
  <div id="progress-container"><div id="progress-bar"></div></div>

  <!-- Sticky HUD -->
  <nav class="hud">
    <div class="hud-brand">
      <span>RÍOS ABIERTOS GT</span>
      <span class="tag">Antigravity</span>
    </div>
    <div class="hud-links">
      <a href="#stats" class="hud-btn">Métricas</a>
      <a href="#versus" class="hud-btn">Antigravity vs ChatGPT vs Claude</a>
      <a href="#checklist" class="hud-btn">Checklist de Comparación</a>
      <a href="#motagua" class="hud-btn">Motagua & Las Vacas</a>
      <a href="#feed" class="hud-btn">Feed de Datasets (30)</a>
      <a href="#missing" class="hud-btn">Datos Faltantes</a>
    </div>
  </nav>

  <div class="container">

    <!-- HERO -->
    <header class="hero">
      <div class="hero-badge">⚡ DOOMSCROLLING FEED DE INVESTIGACIÓN & ADQUISICIÓN</div>
      <h1>Descubrimiento y Adquisición de Datos de Agua en Guatemala</h1>
      <p class="lead">
        Relevamiento exhaustivo, adquisición física y verificación empírica de <strong>155.59 MB</strong> de datos hídricos, químicos, geoespaciales y de macroplásticos para la plataforma <strong>RÍOS ABIERTOS GT</strong>.
      </p>
    </header>

    <!-- STATS GRID -->
    <section id="stats" class="stats-grid">
      <div class="stat-card">
        <div class="val">30</div>
        <div class="lbl">Datasets Maestros</div>
        <div class="sub">Catalogados en CSV & XLSX</div>
      </div>
      <div class="stat-card">
        <div class="val">155.6 MB</div>
        <div class="lbl">Datos Preservados</div>
        <div class="sub">66 archivos con SHA-256</div>
      </div>
      <div class="stat-card">
        <div class="val">23,057</div>
        <div class="lbl">Tramos Fluviales GT</div>
        <div class="sub">HydroRIVERS vectoriales</div>
      </div>
      <div class="stat-card">
        <div class="val">1,626</div>
        <div class="lbl">Tramos Río Motagua</div>
        <div class="sub">Red completa en GeoJSON</div>
      </div>
      <div class="stat-card">
        <div class="val">6,617</div>
        <div class="lbl">Registros INSIVUMEH</div>
        <div class="sub">64 estaciones meteorológicas</div>
      </div>
      <div class="stat-card">
        <div class="val">248</div>
        <div class="lbl">Publicaciones Indexadas</div>
        <div class="sub">OpenAlex DOIs & OA</div>
      </div>
    </section>

    <!-- COMPARISON SECTION: ANTIGRAVITY VS CHATGPT VS CLAUDE -->
    <section id="versus">
      <div class="section-header">
        <div class="section-tag">Análisis Comparativo</div>
        <h2 class="section-title">Antigravity vs. ChatGPT vs. Claude: ¿Qué descubrió cada uno?</h2>
        <p class="section-desc">
          Evaluación directa de los tres paquetes de investigación entregados en tu espacio de trabajo. Aquí puedes ver claramente en qué destaca cada agente y qué debes comparar.
        </p>
      </div>

      <div class="comp-table-card">
        <table class="comp-table">
          <thead>
            <tr>
              <th style="width: 22%;">Área / Eje Científico</th>
              <th style="width: 26%; color: #38bdf8;">Antigravity (Nuestra Investigación)</th>
              <th style="width: 26%; color: #34d399;">ChatGPT (Ghagpt)</th>
              <th style="width: 26%; color: #fbbf24;">Claude (01_inventario)</th>
            </tr>
          </thead>
          <tbody>
            <tr class="highlight">
              <td><strong>Cuenca Motagua y Río Las Vacas (Fármacos & DBO)</strong></td>
              <td>
                <span class="agent-pill pill-antigravity">EXCLUSIVO</span><br>
                <strong>Tesis USAC ERIS (Mayo 2025):</strong> 32 estaciones con GPS en Motagua, Las Vacas y descargas hospitalarias. Datos de laboratorio de HPLC-MS/MS con 15 contaminantes emergentes (sulfamidas, cafeína, trimetoprima). Extraído a CSV.
              </td>
              <td>Menciona antecedentes generales de Las Vacas y proyectos de saneamiento, pero no localizó la tesis analítica de 2025 con datos de contaminantes emergentes en laboratorio.</td>
              <td>Mapea artículos históricos de CYTED (Pérez Sabino 2002) y referencias de biblioteca sin descarga estructurada de tablas analíticas recientes.</td>
            </tr>
            <tr>
              <td><strong>Macroplásticos Fluviales (The Ocean Cleanup)</strong></td>
              <td>
                <span class="agent-pill pill-antigravity">DATOS DESCARGADOS</span><br>
                Descargó y convirtió el archivo Excel original de <strong>Meijer et al. 2019</strong> en Morales, Izabal (tasas de hasta 44,968 ítems/h) y la capa shapefile de <strong>140 desembocaduras</strong> de plástico en GT.
              </td>
              <td>Resume los informes anuales del Interceptor 006 y estimaciones agregadas de toneladas anuales (20,000 t/año) sin tablas de campo mensuales.</td>
              <td>Menciona los hitos de prensa del Interceptor 006 y el fallo del Trashfence 2022 sin adquirir el dataset cuantitativo de Figshare.</td>
            </tr>
            <tr class="highlight">
              <td><strong>Red Hidrográfica Vectorial (SIG & Caudales)</strong></td>
              <td>
                <span class="agent-pill pill-antigravity">VECTORIZADO</span><br>
                Descargó el shapefile continental de <strong>HydroRIVERS</strong> (66 MB), extrajo <strong>23,057 tramos</strong> de Guatemala en CSV y generó el GeoJSON de <strong>1,626 tramos de la Cuenca del Motagua</strong> con caudales modelados.
              </td>
              <td>Documentó enlaces a mapas web y delimitaciones generales de cuencas en GeoJSON (17 MB).</td>
              <td>Descargó capas de vías fluviales de HDX / Humanitarian OpenStreetMap (líneas básicas sin atributos de caudal modelado ni orden Strahler).</td>
            </tr>
            <tr>
              <td><strong>Estadísticas Ambientales Nacionales (INE)</strong></td>
              <td>Mapeó el portal del INE y documentó bloqueos perimetrales WAF en datos.gob.gt.</td>
              <td>
                <span class="agent-pill pill-chatgpt">DESTACADO CHATGPT</span><br>
                <strong>Gran recuperación de tablas INE (2022–2024):</strong> 37 archivos descargados con 122,000+ registros agregados de cloro, niveles de río y acueductos.
              </td>
              <td>Listó enlaces de búsqueda en INE sin extracción masiva de las tablas anuales.</td>
            </tr>
            <tr class="highlight">
              <td><strong>Serie Limnológica Lago de Atitlán</strong></td>
              <td>Descargó los informes oficiales anuales DICA 2024 (perfiles 0-300m), Ríos 2021 y Ciano-Semáforo.</td>
              <td>
                <span class="agent-pill pill-chatgpt">DESTACADO CHATGPT</span><br>
                Localizó y descargó el dataset de Zenodo de la UVG con <strong>30,826 observaciones</strong> (2010–2024) y scripts en R.
              </td>
              <td>Descargó boletines informativos de AMSCLAE y enlaces de publicaciones sobre cianobacterias.</td>
            </tr>
            <tr>
              <td><strong>Auditoría Global UNEP GEMStat (GFQA v3)</strong></td>
              <td>
                <span class="agent-pill pill-antigravity">VERIFICADO EN ARCHIVO</span><br>
                Inspeccionó el archivo de 201 MB: demostró empíricamente que Guatemala tiene <strong>0 estaciones registradas</strong> (las 129 de la caja geográfica son de México).
              </td>
              <td>Reportó la misma brecha de 0 estaciones en su auditoría JSON.</td>
              <td>Mencionó datos transfronterizos sin verificar la ausencia total de estaciones oficiales guatemaltecas en el catálogo global.</td>
            </tr>
            <tr class="highlight">
              <td><strong>Boletines Hidrológicos Operativos (INSIVUMEH 2026)</strong></td>
              <td>
                <span class="agent-pill pill-antigravity">TIEMPO REAL</span><br>
                Descargó y parseó los boletines oficiales diarios (Caribe `BHVC.pdf`, Pacífico `BHVP.pdf`, Golfo `BHVGM.pdf`) con caudales del 20 de octubre de 2026 (Panajax, Gualán, Concuá II).
              </td>
              <td>Identificó las URLs maestras de los boletines pero no extrajo las tablas de caudal instantáneo a nivel de estación individual.</td>
              <td>Listó enlaces de la web de INSIVUMEH en archivos CSV de búsqueda.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <!-- INTERACTIVE CHECKLIST FOR THE USER -->
    <section id="checklist">
      <div class="section-header">
        <div class="section-tag">Tu Hoja de Ruta</div>
        <h2 class="section-title">Checklist de Comparación: Qué contrastar entre las 3 carpetas</h2>
        <p class="section-desc">
          Utiliza estas casillas para guiar tu revisión entre las tres carpetas de agentes en tu disco. Tus marcas se guardan automáticamente en tu navegador.
        </p>
      </div>

      <div class="checklist-card">
        <div class="check-item">
          <input type="checkbox" id="c1" onchange="saveCheck('c1')">
          <div class="check-content">
            <div class="check-title">1. Contrastar Contaminantes Emergentes en Cuenca Motagua / Las Vacas</div>
            <div class="check-desc">
              Compara el archivo exclusivo de Antigravity <code>USAC_ERIS_Motagua_LasVacas_2025_Monitoring_Data.csv</code> (32 estaciones con coordenadas, sulfamidas, cafeína y DBO) contra lo que tengan ChatGPT y Claude en sus carpetas de datos.
            </div>
            <div class="check-tags">
              <span class="badge badge-exclusive">Exclusivo Antigravity</span>
              <span class="badge badge-verified">HPLC-MS/MS 2025</span>
            </div>
          </div>
        </div>

        <div class="check-item">
          <input type="checkbox" id="c2" onchange="saveCheck('c2')">
          <div class="check-content">
            <div class="check-title">2. Evaluar la Red Vectorial de Ríos (HydroRIVERS vs HDX)</div>
            <div class="check-desc">
              Abre en QGIS el archivo <code>Motagua_River_Basin_Network.geojson</code> de Antigravity (1,626 tramos con orden de Strahler y caudal medio modelado) y compáralo con las capas de agua de Claude (HDX/OSM) y los polígonos de ChatGPT.
            </div>
            <div class="check-tags">
              <span class="badge badge-geo">Modelado Hidrológico</span>
              <span class="badge badge-downloaded">1,626 Tramos Motagua</span>
            </div>
          </div>
        </div>

        <div class="check-item">
          <input type="checkbox" id="c3" onchange="saveCheck('c3')">
          <div class="check-content">
            <div class="check-title">3. Comparar Datos de Macroplásticos (The Ocean Cleanup)</div>
            <div class="check-desc">
              Revisa si ChatGPT o Claude descargaron el dataset numérico de <code>TheOceanCleanup_Motagua_Morales_2019_Flux.csv</code> (tasas mensuales en kg y tons) o los 140 puntos de vertido en <code>Guatemala_River_Plastic_Outlets_Meijer2021.csv</code>.
            </div>
            <div class="check-tags">
              <span class="badge badge-verified">Medición de Campo</span>
              <span class="badge badge-downloaded">Figshare 2019/2021</span>
            </div>
          </div>
        </div>

        <div class="check-item">
          <input type="checkbox" id="c4" onchange="saveCheck('c4')">
          <div class="check-content">
            <div class="check-title">4. Revisar la Fortaleza de ChatGPT en Tablas INE (2022–2024)</div>
            <div class="check-desc">
              Examina en <code>Investigación ChatGPT/Ghagpt/data/raw/ine</code> los 37 archivos de estadísticas ambientales recuperados. Son un excelente complemento para series institucionales agregadas.
            </div>
            <div class="check-tags">
              <span class="badge badge-verified">Fuerte de ChatGPT</span>
              <span class="badge badge-geo">122k Registros</span>
            </div>
          </div>
        </div>

        <div class="check-item">
          <input type="checkbox" id="c5" onchange="saveCheck('c5')">
          <div class="check-content">
            <div class="check-title">5. Revisar la Serie Histórica de Atitlán (UVG en Zenodo de ChatGPT)</div>
            <div class="check-desc">
              Comprueba el archivo de 30,826 observaciones limnológicas de Atitlán (2010–2024) recuperado por ChatGPT y compáralo con los informes anuales DICA 2024 de AMSCLAE descargados por Antigravity.
            </div>
            <div class="check-tags">
              <span class="badge badge-verified">Zenodo UVG</span>
              <span class="badge badge-downloaded">DICA 2024 AMSCLAE</span>
            </div>
          </div>
        </div>

        <div class="check-item">
          <input type="checkbox" id="c6" onchange="saveCheck('c6')">
          <div class="check-content">
            <div class="check-title">6. Verificar la Integridad del Manifiesto Criptográfico (SHA-256)</div>
            <div class="check-desc">
              Comprueba en <code>manifests/data_manifest.json</code> que cada archivo descargado por Antigravity cuenta con su tamaño exacto en bytes y su hash SHA-256 para total reproducibilidad científica.
            </div>
            <div class="check-tags">
              <span class="badge badge-verified">SHA-256</span>
              <span class="badge badge-geo">155.59 MB Verificados</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- MOTAGUA & LAS VACAS HIGHLIGHT SECTION -->
    <section id="motagua">
      <div class="section-header">
        <div class="section-tag">Foco Prioritario 1 & 2</div>
        <h2 class="section-title">Evidencia Directa: Cuenca del Río Motagua y Río Las Vacas</h2>
        <p class="section-desc">
          Datos de muestreo in-situ, contaminantes emergentes farmacéuticos y mediciones de transporte de plásticos adquiridos y procesados por Antigravity.
        </p>
      </div>

      <!-- Preview 1: USAC ERIS 2025 Data -->
      <div class="feed-card">
        <div class="card-top">
          <div>
            <span class="card-id">GT-H2O-007 / DATASET PROCESADO</span>
            <div class="card-org">Universidad de San Carlos de Guatemala — ERIS (Mayo 2025)</div>
          </div>
          <div class="card-badges">
            <span class="badge badge-exclusive">Exclusivo Antigravity</span>
            <span class="badge badge-verified">HPLC-MS/MS</span>
            <span class="badge badge-downloaded">CSV + PDF</span>
          </div>
        </div>
        <div class="card-title">Monitoreo de Contaminantes Emergentes Farmacéuticos, DBO y DQO en Río Motagua y Las Vacas</div>
        <div class="card-notes">
          Muestreo en 32 puntos con GPS de alta precisión en el cauce del Río Las Vacas, drenajes pluviales metropolitanos, descargas hospitalarias (IGSS Zona 6, San Juan de Dios, Centro Médico) y afluentes del Motagua. Incluye cuantificación en ng/L de sulfamidas, cafeína, ibuprofeno y antibióticos.
        </div>

        <div class="preview-box">
          <table class="data-preview">
            <thead>
              <tr>
                <th>Estación ID</th>
                <th>Cuerpo de Agua</th>
                <th>Descripción</th>
                <th>Latitud</th>
                <th>Longitud</th>
                <th>OD (mg/L)</th>
                <th>DBO5 (mg/L)</th>
                <th>DQO (mg/L)</th>
                <th>Cafeína (ng/L)</th>
                <th>Sulfametoxazol (ng/L)</th>
              </tr>
            </thead>
            <tbody>
              <tr><td>CAV-1</td><td>Río Las Vacas</td><td>Calzada la Paz</td><td>14.63773</td><td>-90.48884</td><td>1.57</td><td>87.80</td><td>157.0</td><td>15,398.7</td><td>44.01</td></tr>
              <tr><td>CAV-2</td><td>Río Las Vacas</td><td>Cerca Camposanto Cipreses</td><td>14.64776</td><td>-90.48664</td><td>0.54</td><td>191.00</td><td>377.0</td><td>45,100.5</td><td>108.68</td></tr>
              <tr><td>CAV-4</td><td>Río Las Vacas</td><td>Cerca Represa Las Vacas</td><td>14.75509</td><td>-90.50059</td><td>1.68</td><td>376.50</td><td>473.0</td><td>11,621.1</td><td>ND</td></tr>
              <tr><td>CAV-5</td><td>Río Las Vacas</td><td>Cantón Pila Seca 2</td><td>14.71277</td><td>-90.49435</td><td>0.33</td><td>426.50</td><td>743.0</td><td>ND</td><td>ND</td></tr>
              <tr><td>DNH-6</td><td>Alcantarillado</td><td>Frente Edificio Galerías</td><td>14.60484</td><td>-90.51618</td><td>4.01</td><td>691.63</td><td>797.0</td><td>56,433.7</td><td>62.52</td></tr>
              <tr><td>DH-4</td><td>Descarga Hosp.</td><td>IGSS Enf. Zona 9</td><td>14.60497</td><td>-90.51706</td><td>2.64</td><td>104.00</td><td>416.0</td><td>ND</td><td>7,481.7</td></tr>
              <tr><td>CAM-1</td><td>Río Motagua</td><td>Cauce Principal Motagua</td><td>14.98500</td><td>-89.85000</td><td>3.47</td><td>82.40</td><td>119.0</td><td>ND</td><td>ND</td></tr>
            </tbody>
          </table>
        </div>

        <div class="card-actions">
          <a href="file:///D:/Documentos%20D/BaseDatosGT%20H2O/Investigación%20Antigravity/data/processed/USAC_ERIS_Motagua_LasVacas_2025_Monitoring_Data.csv" class="btn-action btn-primary">Abrir CSV Procesado (32 estaciones)</a>
          <a href="file:///D:/Documentos%20D/BaseDatosGT%20H2O/Investigación%20Antigravity/data/raw/academic/USAC_Motagua_Contaminantes_Emergentes_DBO_DQO.pdf" class="btn-action btn-secondary">Abrir Tesis Completa PDF (172 págs)</a>
        </div>
      </div>

      <!-- Preview 2: The Ocean Cleanup Motagua Flux -->
      <div class="feed-card" style="margin-top: 20px;">
        <div class="card-top">
          <div>
            <span class="card-id">GT-H2O-015 / CAMPAÑA DE CAMPO</span>
            <div class="card-org">The Ocean Cleanup / USAC CEMA (Meijer et al.)</div>
          </div>
          <div class="card-badges">
            <span class="badge badge-verified">Datos de Campo</span>
            <span class="badge badge-downloaded">Excel XML & CSV</span>
          </div>
        </div>
        <div class="card-title">Transporte Fluvial de Macroplásticos en Morales, Río Motagua (2019)</div>
        <div class="card-notes">
          Mediciones visuales estandarizadas de conteo de plástico por sección transversal en puentes de Morales, Zacapa y Las Vacas. Demuestra el incremento estacional de plásticos durante la época lluviosa hasta superar las 250 toneladas mensuales.
        </div>

        <div class="preview-box">
          <table class="data-preview">
            <thead>
              <tr>
                <th>Mes (2019)</th>
                <th>Flujo Medio (# ítems/hora)</th>
                <th>Total Mensual (# ítems)</th>
                <th>Peso Medio (g)</th>
                <th>Factor Corrección Columna</th>
                <th>Flujo Plástico (toneladas/mes)</th>
              </tr>
            </thead>
            <tbody>
              <tr><td>Mayo</td><td>431</td><td>320,664</td><td>5.0 g</td><td>1.5</td><td><strong>2.40 tons</strong></td></tr>
              <tr><td>Junio</td><td>3,168</td><td>2,356,992</td><td>5.0 g</td><td>1.5</td><td><strong>17.68 tons</strong></td></tr>
              <tr><td>Julio</td><td>1,092</td><td>812,448</td><td>5.0 g</td><td>1.5</td><td><strong>6.09 tons</strong></td></tr>
              <tr><td>Agosto</td><td>16,707</td><td>12,430,008</td><td>5.0 g</td><td>1.5</td><td><strong>93.23 tons</strong></td></tr>
              <tr><td>Septiembre</td><td>38,699</td><td>28,792,056</td><td>5.0 g</td><td>1.5</td><td><strong>215.94 tons</strong></td></tr>
              <tr><td>Octubre</td><td>44,968</td><td>33,456,192</td><td>5.0 g</td><td>1.5</td><td><strong>250.92 tons</strong></td></tr>
            </tbody>
          </table>
        </div>

        <div class="card-actions">
          <a href="file:///D:/Documentos%20D/BaseDatosGT%20H2O/Investigación%20Antigravity/data/processed/TheOceanCleanup_Motagua_Morales_2019_Flux.csv" class="btn-action btn-primary">Abrir CSV Flujo Mensual</a>
          <a href="file:///D:/Documentos%20D/BaseDatosGT%20H2O/Investigación%20Antigravity/data/processed/Guatemala_River_Plastic_Outlets_Meijer2021.csv" class="btn-action btn-secondary">Abrir 140 Desembocaduras Plásticas CSV</a>
        </div>
      </div>
    </section>

    <!-- FEED DE TODOS LOS DATASETS (DOOMSCROLLING FEED) -->
    <section id="feed">
      <div class="section-header">
        <div class="section-tag">Inventario Completo</div>
        <h2 class="section-title">Feed Continuo de Datasets Adquiridos y Verificados (30)</h2>
        <p class="section-desc">
          Haz scroll continuo por todas las fuentes catalogadas. Puedes filtrar dinámicamente según la categoría de tu interés.
        </p>
      </div>

      <!-- Filter Chips -->
      <div class="filter-bar">
        <button class="filter-chip active" onclick="filterFeed('all')">Todos (30)</button>
        <button class="filter-chip" onclick="filterFeed('motagua')">Cuenca Motagua & Las Vacas (10)</button>
        <button class="filter-chip" onclick="filterFeed('insivumeh')">INSIVUMEH (6)</button>
        <button class="filter-chip" onclick="filterFeed('geo')">Geoespacial & Cuencas (7)</button>
        <button class="filter-chip" onclick="filterFeed('lakes')">Lagos Atitlán & Amatitlán (6)</button>
        <button class="filter-chip" onclick="filterFeed('intl')">Internacional & Brechas (5)</button>
      </div>

      <!-- Feed Container -->
      <div class="feed" id="feed-container">
        <!-- Rendered by JS -->
      </div>
    </section>

    <!-- MISSING DATA & ROADMAP -->
    <section id="missing">
      <div class="section-header">
        <div class="section-tag">Registro de Brechas</div>
        <h2 class="section-title">Registro de Datos Faltantes, Restringidos y Próximas Acciones</h2>
        <p class="section-desc">
          Fuentes institucionales que generan datos pero presentan barreras perimetrales o falta de publicación proactiva, y el protocolo legal para solicitarlos bajo el Decreto 57-2008.
        </p>
      </div>

      <div class="feed" id="missing-container">
        <!-- Rendered by JS -->
      </div>
    </section>

    <!-- FOOTER -->
    <footer>
      <p><strong>RÍOS ABIERTOS GT</strong> — Guatemala Open Water Data Observatory</p>
      <p style="margin-top: 6px;">Investigación desarrollada y compilada con rigor empírico por Antigravity Research Engineering.</p>
      <p style="margin-top: 6px; font-family: monospace; font-size: 0.8rem;">Repositorio: D:\Documentos D\BaseDatosGT H2O\Investigación Antigravity</p>
    </footer>

  </div>

  <!-- SCRIPT FOR INTERACTIVITY -->
  <script>
    // Embedded Data
    const INVENTORY = {inv_json};
    const MISSING = {mis_json};

    // Scroll progress bar
    window.addEventListener('scroll', () => {{
      const winScroll = document.documentElement.scrollTop || document.body.scrollTop;
      const height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
      const scrolled = (winScroll / height) * 100;
      document.getElementById('progress-bar').style.width = scrolled + '%';
    }});

    // Render Feed Cards
    function renderFeed(items) {{
      const container = document.getElementById('feed-container');
      container.innerHTML = '';
      items.forEach(item => {{
        const card = document.createElement('div');
        card.className = 'feed-card';
        card.setAttribute('data-id', item['Resource ID']);

        // Determine badges
        let badgesHtml = '';
        if (item['Download status'].includes('Downloaded')) {{
          badgesHtml += '<span class="badge badge-downloaded">DESCARGADO & VERIFICADO</span>';
        }} else if (item['Download status'].includes('Verified')) {{
          badgesHtml += '<span class="badge badge-verified">VERIFICADO</span>';
        }} else {{
          badgesHtml += '<span class="badge badge-restricted">ACCESO RESTRINGIDO</span>';
        }}

        if (item['File format'].includes('Shapefile') || item['File format'].includes('GeoJSON')) {{
          badgesHtml += '<span class="badge badge-geo">GEOESPACIAL / GIS</span>';
        }}
        if (item['Organisation'].includes('ERIS') || item['Organisation'].includes('The Ocean Cleanup')) {{
          badgesHtml += '<span class="badge badge-exclusive">DESTACADO</span>';
        }}

        card.innerHTML = `
          <div class="card-top">
            <div>
              <span class="card-id">${{item['Resource ID']}}</span>
              <span class="card-org" style="margin-left: 8px;">${{item['Organisation']}}</span>
            </div>
            <div class="card-badges">${{badgesHtml}}</div>
          </div>
          <h3 class="card-title">${{item['Resource title']}}</h3>
          <div class="card-grid">
            <div class="grid-item">
              <span class="lbl">Tipo / Formato</span>
              <span class="val">${{item['Resource type']}} (${{item['File format']}})</span>
            </div>
            <div class="grid-item">
              <span class="lbl">Años Cubiertos</span>
              <span class="val">${{item['Years covered']}}</span>
            </div>
            <div class="grid-item">
              <span class="lbl">Cobertura Geográfica</span>
              <span class="val">${{item['Geographic coverage']}}</span>
            </div>
            <div class="grid-item">
              <span class="lbl">Registros Verificados</span>
              <span class="val">${{item['Number of records, if verified']}}</span>
            </div>
          </div>
          <div class="card-notes">
            <strong>Parámetros:</strong> ${{item['Parameters']}}<br>
            <span style="color: #64748b; font-size: 0.85rem; display: block; margin-top: 4px;"><strong>Nota Técnica:</strong> ${{item['Notes']}}</span>
          </div>
          <div class="card-actions">
            ${{item['Download URL'].startsWith('http') ? `<a href="${{item['Download URL']}}" target="_blank" class="btn-action btn-primary">Enlace de Descarga / Fuente</a>` : ''}}
            <span class="badge" style="background: rgba(255,255,255,0.06); color: #94a3b8;">Licencia: ${{item['Licence']}}</span>
          </div>
        `;
        container.appendChild(card);
      }});
    }}

    // Filter logic
    function filterFeed(category) {{
      document.querySelectorAll('.filter-chip').forEach(c => c.classList.remove('active'));
      event.target.classList.add('active');

      if (category === 'all') {{
        renderFeed(INVENTORY);
      }} else if (category === 'motagua') {{
        const filtered = INVENTORY.filter(i => 
          i['Geographic coverage'].toLowerCase().includes('motagua') || 
          i['Geographic coverage'].toLowerCase().includes('vacas') ||
          i['Resource title'].toLowerCase().includes('motagua') ||
          i['Resource title'].toLowerCase().includes('vacas')
        );
        renderFeed(filtered);
      }} else if (category === 'insivumeh') {{
        const filtered = INVENTORY.filter(i => i['Organisation'].includes('INSIVUMEH'));
        renderFeed(filtered);
      }} else if (category === 'geo') {{
        const filtered = INVENTORY.filter(i => 
          i['File format'].includes('Shapefile') || 
          i['File format'].includes('GeoJSON') || 
          i['File format'].includes('GeoTIFF') ||
          i['Resource type'].toLowerCase().includes('geospatial')
        );
        renderFeed(filtered);
      }} else if (category === 'lakes') {{
        const filtered = INVENTORY.filter(i => 
          i['Geographic coverage'].toLowerCase().includes('atitl') || 
          i['Geographic coverage'].toLowerCase().includes('amatitl') ||
          i['Organisation'].includes('AMS')
        );
        renderFeed(filtered);
      }} else if (category === 'intl') {{
        const filtered = INVENTORY.filter(i => 
          i['Organisation'].includes('Bank') || 
          i['Organisation'].includes('UNEP') || 
          i['Organisation'].includes('WMO') ||
          i['Organisation'].includes('Copernicus') ||
          i['Organisation'].includes('NASA')
        );
        renderFeed(filtered);
      }}
    }}

    // Render Missing Data
    function renderMissing() {{
      const container = document.getElementById('missing-container');
      container.innerHTML = '';
      MISSING.forEach(m => {{
        const card = document.createElement('div');
        card.className = 'feed-card';
        card.innerHTML = `
          <div class="card-top">
            <span class="card-org">${{m['Organisation']}}</span>
            <span class="badge badge-restricted">${{m['Status']}}</span>
          </div>
          <h3 class="card-title" style="font-size: 1.1rem; color: #f43f5e;">Dato Esperado: ${{m['Expected type of data']}}</h3>
          <div class="card-notes" style="border-left-color: #f43f5e;">
            <strong>Evidencia de Monitoreo:</strong> ${{m['Evidence of monitoring']}}<br>
            <strong>Causa de Falla de Acceso:</strong> ${{m['Specific reason access failed']}}
          </div>
          <div style="background: rgba(15, 23, 42, 0.6); padding: 12px; border-radius: 8px; font-size: 0.85rem;">
            <strong style="color: var(--accent-teal);">Acción Recomendada:</strong> ${{m['Recommended next action']}}<br>
            <span style="color: var(--text-muted); font-size: 0.78rem;">¿Solicitud de Información Pública viable?: <strong>${{m['Formal request feasible?']}}</strong></span>
          </div>
        `;
        container.appendChild(card);
      }});
    }}

    // LocalStorage for checklist
    function saveCheck(id) {{
      const cb = document.getElementById(id);
      localStorage.setItem('rios_gt_' + id, cb.checked);
    }}
    function loadChecks() {{
      ['c1', 'c2', 'c3', 'c4', 'c5', 'c6'].forEach(id => {{
        const saved = localStorage.getItem('rios_gt_' + id);
        if (saved !== null) {{
          const cb = document.getElementById(id);
          if (cb) cb.checked = (saved === 'true');
        }}
      }});
    }}

    // Initial render
    renderFeed(INVENTORY);
    renderMissing();
    loadChecks();
  </script>
</body>
</html>
"""

out_html1 = os.path.join(base_dir, "report/presentacion_doomscrolling_resultados.html")
out_html2 = os.path.join(base_dir, "index.html")

with open(out_html1, 'w', encoding='utf-8') as f:
    f.write(html_content)

with open(out_html2, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"Doomscrolling Presentation successfully created at:\n  - {out_html1}\n  - {out_html2}")
