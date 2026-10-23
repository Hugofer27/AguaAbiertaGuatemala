import requests
import os

base_url = "https://raw.githubusercontent.com/carlossoto362/Hidrologia/main/data/"
gov_dir = "D:/Documentos D/BaseDatosGT H2O/Investigación Antigravity/data/raw/government"
geo_dir = "D:/Documentos D/BaseDatosGT H2O/Investigación Antigravity/data/raw/geospatial"
os.makedirs(gov_dir, exist_ok=True)
os.makedirs(geo_dir, exist_ok=True)

files = [
    ("INSIVUMEH_Estaciones_Automaticas.csv", "automaticas.csv", gov_dir),
    ("INSIVUMEH_Estaciones_Convencionales.csv", "convencionales.csv", gov_dir),
    ("INSIVUMEH_Estaciones_Sinopticas.csv", "sinopticas.csv", gov_dir),
    ("Guatemala_Vertiente_Mar_Caribe_Motagua.geojson", "VMarCaribe.geojson", geo_dir),
    ("Guatemala_Vertiente_Pacifico.geojson", "VPacifico.geojson", geo_dir),
    ("Guatemala_Vertiente_Golfo_Mexico.geojson", "VGolfoMexico.geojson", geo_dir),
    ("Guatemala_Tres_Grandes_Vertientes.geojson", "Vertientes.geojson", geo_dir),
    ("Guatemala_Macrocuencas_Hidrograficas.geojson", "macrocuencasUTF.geojson", geo_dir)
]

headers = {'User-Agent': 'Mozilla/5.0'}
for local_name, remote_name, target_dir in files:
    url = base_url + remote_name
    dest = os.path.join(target_dir, local_name)
    try:
        r = requests.get(url, headers=headers, stream=True, timeout=60)
        if r.status_code == 200:
            with open(dest, 'wb') as f:
                for chunk in r.iter_content(chunk_size=1048576):
                    f.write(chunk)
            print(f"Downloaded {local_name} ({os.path.getsize(dest):,} bytes)")
        else:
            print(f"Failed {local_name}: HTTP {r.status_code}")
    except Exception as e:
        print(f"Error {local_name}: {e}")
