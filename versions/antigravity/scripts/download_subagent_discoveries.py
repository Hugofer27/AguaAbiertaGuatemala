import requests
import os

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

targets = [
    ("AMSCLAE_Monitoreo_Rios_2021.pdf", "https://www.amsclae.gob.gt/wp-content/uploads/2021/12/rios2021.pdf", "D:/Documentos D/BaseDatosGT H2O/Investigación Antigravity/data/raw/government"),
    ("AMSCLAE_Boletin_Calidad_Agua_IV.pdf", "https://www.amsclae.gob.gt/wp-content/uploads/2022/06/ivboletin.pdf", "D:/Documentos D/BaseDatosGT H2O/Investigación Antigravity/data/raw/government"),
    ("USAC_LasVacas_Bocel_Castro_2021_info.html", "http://www.repositorio.usac.edu.gt/id/eprint/21352", "D:/Documentos D/BaseDatosGT H2O/Investigación Antigravity/data/raw/academic")
]

for name, url, out_dir in targets:
    dest = os.path.join(out_dir, name)
    try:
        r = requests.get(url, headers=headers, timeout=30, verify=False)
        print(f"{name} -> HTTP {r.status_code}, {len(r.content):,} bytes")
        if r.status_code == 200:
            with open(dest, 'wb') as f:
                f.write(r.content)
            print(f"  Saved to {dest}")
    except Exception as e:
        print(f"  Error {name}: {e}")
