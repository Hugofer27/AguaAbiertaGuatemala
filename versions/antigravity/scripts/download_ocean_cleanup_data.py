import requests
import os

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

targets = [
    ("TheOceanCleanup_Motagua_Field_Data_2019.xlsx", "https://ndownloader.figshare.com/files/25764734", "D:/Documentos D/BaseDatosGT H2O/Investigación Antigravity/data/raw/ngos_cleanup"),
    ("TheOceanCleanup_Meijer2021_Emissions_Shapefile.zip", "https://ndownloader.figshare.com/files/27807774", "D:/Documentos D/BaseDatosGT H2O/Investigación Antigravity/data/raw/ngos_cleanup")
]

for name, url, out_dir in targets:
    os.makedirs(out_dir, exist_ok=True)
    dest = os.path.join(out_dir, name)
    try:
        r = requests.get(url, headers=headers, timeout=45, stream=True)
        print(f"{name} -> HTTP {r.status_code}")
        if r.status_code == 200:
            with open(dest, 'wb') as f:
                for chunk in r.iter_content(chunk_size=65536):
                    f.write(chunk)
            print(f"  SAVED {dest} ({os.path.getsize(dest):,} bytes)")
        else:
            print(f"  FAILED: {r.status_code}")
    except Exception as e:
        print(f"  ERROR {name}: {e}")
