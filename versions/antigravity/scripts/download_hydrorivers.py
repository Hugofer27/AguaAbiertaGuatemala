import os
import requests

url = "https://data.hydrosheds.org/file/HydroRIVERS/HydroRIVERS_v10_na_shp.zip"
out_dir = "D:/Documentos D/BaseDatosGT H2O/Investigación Antigravity/data/raw/geospatial"
os.makedirs(out_dir, exist_ok=True)
dest = os.path.join(out_dir, "HydroRIVERS_v10_na_shp.zip")

print(f"Downloading {url} to {dest}...")
headers = {'User-Agent': 'Mozilla/5.0'}
with requests.get(url, headers=headers, stream=True) as r:
    r.raise_for_status()
    total = 0
    with open(dest, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1048576):
            if chunk:
                f.write(chunk)
                total += len(chunk)
                print(f"  Downloaded {total / (1024*1024):.1f} MB...", end='\r')

print(f"\nFinished! Total size: {total:,} bytes")
