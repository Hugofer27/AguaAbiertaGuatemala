with open(r"D:\Documentos D\BaseDatosGT H2O\Investigación Antigravity\index.html", "r", encoding="utf-8") as f:
    c = f.read()

target = '<a href="#stats" class="hud-btn">Métricas</a>'
replacement = '<a href="mapa_interactivo_rios_abiertos.html" class="hud-btn" style="background: linear-gradient(135deg, #0284c7, #0d9488); color: #fff; font-weight: 800; border: 1px solid #38bdf8;">🗺️ Ver Mapa Nacional WQIS</a>\n      <a href="#stats" class="hud-btn">Métricas</a>'

if target in c:
    c = c.replace(target, replacement, 1)
    with open(r"D:\Documentos D\BaseDatosGT H2O\Investigación Antigravity\index.html", "w", encoding="utf-8") as f:
        f.write(c)
    print("index.html updated successfully with link to mapa_interactivo_rios_abiertos.html")
else:
    print("Target not found")
