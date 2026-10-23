import zipfile
import struct
import json
import os
import csv

zip_path = "D:/Documentos D/BaseDatosGT H2O/Investigación Antigravity/data/raw/geospatial/HydroRIVERS_v10_na_shp.zip"
out_dir = "D:/Documentos D/BaseDatosGT H2O/Investigación Antigravity/data/processed"
os.makedirs(out_dir, exist_ok=True)

print("Opening HydroRIVERS archive...")
z = zipfile.ZipFile(zip_path)

# 1. Parse DBF Header & fields
with z.open('HydroRIVERS_v10_na_shp/HydroRIVERS_v10_na.dbf') as f_dbf:
    dbf_header = f_dbf.read(32)
    num_records, header_len, record_len = struct.unpack('<IHH', dbf_header[4:12])
    fields = []
    while True:
        b = f_dbf.read(1)
        if b == b'\r' or not b:
            break
        desc = b + f_dbf.read(31)
        name = desc[:11].replace(b'\x00', b'').decode('ascii').strip()
        ftype = chr(desc[11])
        flen = desc[16]
        fdec = desc[17]
        fields.append((name, ftype, flen, fdec))
    
    print(f"DBF has {num_records:,} records, {len(fields)} fields.")
    
# 2. Parse SHP and DBF simultaneously
# Bounding box for Guatemala
GT_XMIN, GT_XMAX = -92.5, -88.0
GT_YMIN, GT_YMAX = 13.5, 18.0

gt_reaches = []
motagua_reaches = []

with z.open('HydroRIVERS_v10_na_shp/HydroRIVERS_v10_na.shp') as f_shp, \
     z.open('HydroRIVERS_v10_na_shp/HydroRIVERS_v10_na.dbf') as f_dbf:
    
    # Skip headers
    f_shp.seek(100)
    f_dbf.seek(header_len)
    
    # Precompute field offsets
    field_specs = []
    offset = 1 # skip deletion flag
    for name, ftype, flen, fdec in fields:
        field_specs.append((name, offset, flen, ftype))
        offset += flen
        
    print("Scanning shapefile for Guatemala river reaches...")
    rec_idx = 0
    while rec_idx < num_records:
        rec_idx += 1
        
        # Read SHP record header
        hdr = f_shp.read(8)
        if not hdr:
            break
        rec_num, content_len = struct.unpack('>II', hdr)
        rec_bytes = f_shp.read(content_len * 2)
        
        # Read DBF record
        dbf_rec = f_dbf.read(record_len)
        if not dbf_rec:
            break
            
        shape_type = struct.unpack('<i', rec_bytes[:4])[0]
        if shape_type != 3: # PolyLine
            continue
            
        xmin, ymin, xmax, ymax = struct.unpack('<4d', rec_bytes[4:36])
        
        # Check if overlaps Guatemala bounding box
        if not (xmax < GT_XMIN or xmin > GT_XMAX or ymax < GT_YMIN or ymin > GT_YMAX):
            # Parse DBF attributes
            attrs = {}
            for fname, foff, flen, ftype in field_specs:
                raw_val = dbf_rec[foff:foff+flen].decode('ascii', errors='ignore').strip()
                if ftype == 'N':
                    attrs[fname] = float(raw_val) if '.' in raw_val else (int(raw_val) if raw_val else 0)
                else:
                    attrs[fname] = raw_val
            
            # Unpack PolyLine points
            num_parts, num_points = struct.unpack('<ii', rec_bytes[36:44])
            parts_offset = 44
            points_offset = parts_offset + (num_parts * 4)
            
            parts = list(struct.unpack(f'<{num_parts}i', rec_bytes[parts_offset:points_offset]))
            parts.append(num_points)
            
            coords = []
            for pt_idx in range(num_points):
                pt_bytes = rec_bytes[points_offset + (pt_idx * 16): points_offset + ((pt_idx + 1) * 16)]
                px, py = struct.unpack('<2d', pt_bytes)
                coords.append([round(px, 5), round(py, 5)])
            
            reach_info = {
                'id': attrs.get('HYRIV_ID'),
                'main_riv': attrs.get('MAIN_RIV'),
                'length_km': attrs.get('LENGTH_KM'),
                'catch_skm': attrs.get('CATCH_SKM'),
                'upland_skm': attrs.get('UPLAND_SKM'),
                'dis_av_cms': attrs.get('DIS_AV_CMS'),
                'ord_stra': attrs.get('ORD_STRA'),
                'xmin': round(xmin, 4),
                'ymin': round(ymin, 4),
                'xmax': round(xmax, 4),
                'ymax': round(ymax, 4),
                'coords': coords
            }
            gt_reaches.append(reach_info)

print(f"Found {len(gt_reaches):,} river reaches inside Guatemala bounding box.")

# Find main rivers by total upstream catchment area
main_riv_counts = {}
for r in gt_reaches:
    m = r['main_riv']
    main_riv_counts[m] = main_riv_counts.get(m, 0) + 1

sorted_mains = sorted(main_riv_counts.items(), key=lambda x: x[1], reverse=True)
print("Top main river systems (by segment count):")
for mid, count in sorted_mains[:5]:
    # sample reach
    sample = [r for r in gt_reaches if r['main_riv'] == mid and r['dis_av_cms'] > 50]
    max_dis = max([r['dis_av_cms'] for r in gt_reaches if r['main_riv'] == mid])
    print(f"  MAIN_RIV {mid}: {count} reaches, Max discharge: {max_dis} m³/s")

# Identify Motagua: Motagua flows into Caribbean around lat 15.72, lon -88.23 with discharge ~200-300 m³/s
motagua_id = None
for r in gt_reaches:
    if 15.5 <= r['ymax'] <= 15.8 and -88.4 <= r['xmax'] <= -88.1 and r['dis_av_cms'] > 150:
        motagua_id = r['main_riv']
        print(f"--> Identified Motagua Basin MAIN_RIV ID: {motagua_id} (Discharge at mouth: {r['dis_av_cms']} m³/s)")
        break

# Export all Guatemala river reaches to CSV
csv_out = os.path.join(out_dir, "Guatemala_HydroRIVERS_Reaches.csv")
with open(csv_out, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['HYRIV_ID', 'MAIN_RIV', 'LENGTH_KM', 'CATCH_SKM', 'UPLAND_SKM', 'DIS_AV_CMS', 'ORD_STRA', 'XMIN', 'YMIN', 'XMAX', 'YMAX', 'IS_MOTAGUA'])
    for r in gt_reaches:
        is_mot = 1 if (motagua_id and r['main_riv'] == motagua_id) else 0
        writer.writerow([r['id'], r['main_riv'], r['length_km'], r['catch_skm'], r['upland_skm'], r['dis_av_cms'], r['ord_stra'], r['xmin'], r['ymin'], r['xmax'], r['ymax'], is_mot])
print(f"Exported {len(gt_reaches):,} records to {csv_out}")

# Export Motagua River network to GeoJSON
if motagua_id:
    motagua_features = []
    for r in gt_reaches:
        if r['main_riv'] == motagua_id:
            feat = {
                "type": "Feature",
                "properties": {
                    "hyriv_id": r['id'],
                    "length_km": r['length_km'],
                    "upland_skm": r['upland_skm'],
                    "dis_av_cms": r['dis_av_cms'],
                    "strahler_order": r['ord_stra']
                },
                "geometry": {
                    "type": "LineString",
                    "coordinates": r['coords']
                }
            }
            motagua_features.append(feat)
            
    geojson_out = os.path.join(out_dir, "Motagua_River_Basin_Network.geojson")
    with open(geojson_out, 'w', encoding='utf-8') as f:
        json.dump({"type": "FeatureCollection", "features": motagua_features}, f)
    print(f"Exported {len(motagua_features):,} Motagua reach lines to GeoJSON: {geojson_out}")
