import zipfile
import struct
import csv
import os

zip_path = "D:/Documentos D/BaseDatosGT H2O/Investigación Antigravity/data/raw/ngos_cleanup/TheOceanCleanup_Meijer2021_Emissions_Shapefile.zip"
out_csv = "D:/Documentos D/BaseDatosGT H2O/Investigación Antigravity/data/processed/Guatemala_River_Plastic_Outlets_Meijer2021.csv"

z = zipfile.ZipFile(zip_path)
with z.open('Meijer2021_midpoint_emissions.shp') as f_shp, z.open('Meijer2021_midpoint_emissions.dbf') as f_dbf:
    f_shp.seek(100)
    f_dbf.seek(32 + 32 + 1)
    points = []
    idx = 0
    while True:
        hdr = f_shp.read(8)
        if not hdr:
            break
        idx += 1
        num, clen = struct.unpack('>II', hdr)
        b = f_shp.read(clen*2)
        stype, x, y = struct.unpack('<idd', b)
        dbf_rec = f_dbf.read(14)
        val = float(dbf_rec[1:].decode('ascii', errors='ignore').strip() or 0)
        if -92.5 <= x <= -88.0 and 13.5 <= y <= 18.0:
            coast = "Mar Caribe" if (y > 15.2 and x > -89.5) else "Océano Pacífico"
            points.append({
                'point_id': idx,
                'longitud': round(x, 5),
                'latitud': round(y, 5),
                'vertiente': coast,
                'emision_plastico_toneladas_anio': val,
                'fuente': 'The Ocean Cleanup / Meijer et al. Science Advances (2021)'
            })

points.sort(key=lambda p: p['emision_plastico_toneladas_anio'], reverse=True)
with open(out_csv, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['point_id', 'longitud', 'latitud', 'vertiente', 'emision_plastico_toneladas_anio', 'fuente'])
    writer.writeheader()
    writer.writerows(points)

print(f"Exported {len(points)} Guatemala river plastic outlets to {out_csv}")
