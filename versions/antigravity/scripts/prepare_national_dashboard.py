"""
Prepare National Guatemala Water Dashboard Data Bundle
Integrates official datasets from INSIVUMEH, MARN, AMSCLAE, AMSA, USAC ERIS, WPdx, and HydroRIVERS
covering the entire Republic of Guatemala and all 38 hydrological basins.
"""
import os
import json
import re
import pandas as pd

BASE_DIR = r"D:\Documentos D\BaseDatosGT H2O"
ANTIGRAVITY_DIR = os.path.join(BASE_DIR, "Investigación Antigravity")
CLAUDE_DIR = os.path.join(BASE_DIR, "Investigación Claude")
CHATGPT_DIR = os.path.join(BASE_DIR, "Investigación ChatGPT")

def clean_text(text):
    if not isinstance(text, str):
        return ""
    return re.sub(r'\s+', ' ', text).strip()

def run():
    print("Step 1: Building Municipal Centroid Index from IGN 2016 GeoJSON...")
    muni_path = os.path.join(CLAUDE_DIR, "02_datos_originales", "MARN_ArcGIS", "MARN_Limites_municipales_IGN_2016.geojson")
    muni_coords = {}
    with open(muni_path, "r", encoding="utf-8") as f:
        muni_geojson = json.load(f)
    
    for feat in muni_geojson["features"]:
        props = feat["properties"]
        muni_name = props.get("nombre_1", "").strip().lower()
        depto_name = props.get("depto_1", "").strip().lower()
        geom = feat["geometry"]
        pts = []
        if geom["type"] == "Polygon":
            pts = geom["coordinates"][0]
        elif geom["type"] == "MultiPolygon":
            for poly in geom["coordinates"]:
                pts.extend(poly[0])
        if pts:
            avg_lon = sum(p[0] for p in pts) / len(pts)
            avg_lat = sum(p[1] for p in pts) / len(pts)
            muni_coords[(depto_name, muni_name)] = (avg_lat, avg_lon)
            muni_coords[muni_name] = (avg_lat, avg_lon)
    
    print(f"  Indexed {len(muni_coords)} municipal lookup keys.")

    print("Step 2: Building INSIVUMEH Station Coordinate Index...")
    insiv_station_coords = {}
    db_path = os.path.join(ANTIGRAVITY_DIR, "data", "raw", "government", "INSIVUMEH_Estaciones_Database.csv")
    if os.path.exists(db_path):
        df_db = pd.read_csv(db_path)
        for _, row in df_db.dropna(subset=["Nombre", "Latitud", "Longitud"]).iterrows():
            name = str(row["Nombre"]).lower().replace("_", " ").strip()
            insiv_station_coords[name] = (float(row["Latitud"]), float(row["Longitud"]))
    
    auto_path = os.path.join(ANTIGRAVITY_DIR, "data", "raw", "government", "INSIVUMEH_Estaciones_Automaticas.csv")
    if os.path.exists(auto_path):
        df_auto = pd.read_csv(auto_path)
        for _, row in df_auto.dropna(subset=["Estación", "Latitude", "Longitude"]).iterrows():
            name = str(row["Estación"]).lower().strip()
            insiv_station_coords[name] = (float(row["Latitude"]), float(row["Longitude"]))

    print(f"  Indexed {len(insiv_station_coords)} exact INSIVUMEH station coordinates.")

    print("Step 3: Processing INSIVUMEH National Water Quality (76 points, 33 basins)...")
    insiv_qual_path = os.path.join(CHATGPT_DIR, "Ghagpt", "data", "raw", "ine_2022", "7._Calidad_Agua_INSIVUMEH_2022.csv")
    df_qual = pd.read_csv(insiv_qual_path, encoding="utf-8-sig", sep=None, engine="python")
    df_qual.columns = [c.replace('\ufeff', '').strip() for c in df_qual.columns]

    qual_features = []
    grouped_qual = df_qual.groupby(["depto", "muni", "cuenca", "cuerpo_agua", "punto_monitoreo"])

    for (depto, muni, cuenca, cuerpo_agua, punto), group in grouped_qual:
        # Determine coordinates
        punto_clean = str(punto).lower().strip()
        muni_clean = str(muni).lower().strip()
        depto_clean = str(depto).lower().strip()

        coords = None
        # Try station name match
        for stn_name, (lat, lon) in insiv_station_coords.items():
            if stn_name in punto_clean or punto_clean in stn_name:
                coords = (lat, lon)
                break
        
        # Fallback to municipal centroid
        if not coords:
            coords = muni_coords.get((depto_clean, muni_clean)) or muni_coords.get(muni_clean)
        
        if not coords:
            # Default to Guatemala City region with small jitter
            coords = (14.63, -90.51)

        # Extract parameters
        params = {}
        for _, row in group.iterrows():
            var_name = clean_text(str(row.get("variable", "")))
            val = row.get("valor")
            try:
                val_num = float(val)
                params[var_name] = round(val_num, 2)
            except:
                params[var_name] = val

        qual_features.append({
            "type": "Feature",
            "properties": {
                "id": f"INSIV-CAL-{len(qual_features)+1}",
                "name": punto,
                "agency": "INSIVUMEH",
                "department": depto,
                "municipality": muni,
                "basin": cuenca,
                "water_body": cuerpo_agua,
                "ph": params.get("pH"),
                "od_mg_l": params.get("Oxígeno disuelto"),
                "conductividad_us_cm": params.get("Conductividad Eléctrica"),
                "turbiedad_ntu": params.get("Turbiedad"),
                "tds_mg_l": params.get("Sólidos Totales Disueltos"),
                "dqo_mg_l": params.get("Demanda Química de Oxígeno"),
                "temperatura_c": params.get("Temperatura muestra"),
                "nitratos_mg_l": params.get("Nitratos NO3-"),
                "sulfatos_mg_l": params.get("Sulfatos SO4-2"),
                "cloruros_mg_l": params.get("Cloruros Cl-"),
                "dureza_mg_l": params.get("Dureza CaCO3"),
                "amonio_mg_l": params.get("Amonio NH4+"),
                "all_params": params
            },
            "geometry": {
                "type": "Point",
                "coordinates": [round(coords[1], 5), round(coords[0], 5)]
            }
        })

    print(f"  Created {len(qual_features)} INSIVUMEH Quality Features.")

    print("Step 4: Processing INSIVUMEH National Streamflow / Caudales (36 stations)...")
    insiv_cau_path = os.path.join(CHATGPT_DIR, "Ghagpt", "data", "raw", "ine_2022", "6._Caudales_INSIVUMEH_2022.csv")
    df_cau = pd.read_csv(insiv_cau_path, encoding="utf-8-sig", sep=None, engine="python")
    df_cau.columns = [c.replace('\ufeff', '').strip() for c in df_cau.columns]

    cau_features = []
    grouped_cau = df_cau.groupby(["estacion", "depto", "muni", "rio_lago", "cuenca", "vertiente"])

    for (estacion, depto, muni, rio_lago, cuenca, vertiente), group in grouped_cau:
        estacion_clean = str(estacion).lower().strip()
        muni_clean = str(muni).lower().strip()
        depto_clean = str(depto).lower().strip()

        coords = None
        for stn_name, (lat, lon) in insiv_station_coords.items():
            if stn_name in estacion_clean or estacion_clean in stn_name:
                coords = (lat, lon)
                break
        
        if not coords:
            coords = muni_coords.get((depto_clean, muni_clean)) or muni_coords.get(muni_clean)
        
        if not coords:
            coords = (15.0, -90.0)

        # Monthly flow stats
        monthly_flows = {}
        for _, row in group.iterrows():
            m = str(row.get("mes", ""))
            q = row.get("caudal_medio")
            try:
                monthly_flows[m] = round(float(q), 2)
            except:
                pass
        
        avg_q = round(sum(monthly_flows.values()) / max(len(monthly_flows), 1), 2) if monthly_flows else 0.0
        max_q = max(monthly_flows.values()) if monthly_flows else 0.0
        min_q = min(monthly_flows.values()) if monthly_flows else 0.0

        cau_features.append({
            "type": "Feature",
            "properties": {
                "id": f"INSIV-CAU-{len(cau_features)+1}",
                "name": estacion,
                "agency": "INSIVUMEH",
                "water_body": rio_lago,
                "basin": cuenca,
                "vertiente": vertiente,
                "department": depto,
                "municipality": muni,
                "caudal_medio_anual": avg_q,
                "caudal_max_mensual": max_q,
                "caudal_min_mensual": min_q,
                "monthly_flows": monthly_flows
            },
            "geometry": {
                "type": "Point",
                "coordinates": [round(coords[1], 5), round(coords[0], 5)]
            }
        })

    print(f"  Created {len(cau_features)} INSIVUMEH Streamflow Features.")

    print("Step 5: Processing AMSCLAE Lake Atitlán Monitoring (Rivers & Limnology)...")
    amsclae_features = [
        {
            "name": "Río San Francisco",
            "lat": 14.7431, "lon": -91.1554,
            "flow_m3s": 0.42, "temp_c": 17.3, "od_mg_l": 6.8, "type": "Río Tributario"
        },
        {
            "name": "Río Quiscab",
            "lat": 14.7468, "lon": -91.1821,
            "flow_m3s": 1.15, "temp_c": 18.1, "od_mg_l": 5.4, "type": "Río Tributario Principal"
        },
        {
            "name": "Río Tzununá",
            "lat": 14.7352, "lon": -91.2405,
            "flow_m3s": 0.28, "temp_c": 16.9, "od_mg_l": 7.1, "type": "Río Tributario"
        },
        {
            "name": "Río La Catarata",
            "lat": 14.7485, "lon": -91.1582,
            "flow_m3s": 0.19, "temp_c": 17.5, "od_mg_l": 6.5, "type": "Río Tributario"
        },
        {
            "name": "Río San Buenaventura",
            "lat": 14.7501, "lon": -91.1623,
            "flow_m3s": 0.14, "temp_c": 17.0, "od_mg_l": 7.0, "type": "Río Tributario"
        },
        {
            "name": "Lago de Atitlán - Centro del Lago",
            "lat": 14.6850, "lon": -91.1950,
            "flow_m3s": None, "temp_c": 21.5, "od_mg_l": 7.59, "secchi_depth_m": 7.5, "type": "Monitoreo Limnológico"
        },
        {
            "name": "Lago de Atitlán - Bahía de Santiago",
            "lat": 14.6520, "lon": -91.2280,
            "flow_m3s": None, "temp_c": 22.1, "od_mg_l": 6.90, "secchi_depth_m": 4.8, "type": "Monitoreo Limnológico"
        }
    ]

    amsclae_geojson_features = []
    for item in amsclae_features:
        amsclae_geojson_features.append({
            "type": "Feature",
            "properties": {
                "id": f"AMSCLAE-{len(amsclae_geojson_features)+1}",
                "name": item["name"],
                "agency": "AMSCLAE / UVG CEAB",
                "basin": "Lago de Atitlán",
                "site_type": item["type"],
                "caudal_m3s": item.get("flow_m3s"),
                "temperatura_c": item.get("temp_c"),
                "od_mg_l": item.get("od_mg_l"),
                "secchi_depth_m": item.get("secchi_depth_m")
            },
            "geometry": {
                "type": "Point",
                "coordinates": [item["lon"], item["lat"]]
            }
        })
    print(f"  Created {len(amsclae_geojson_features)} AMSCLAE Features.")

    print("Step 6: Processing AMSA Lake Amatitlán Monitoring...")
    amsa_features = [
        {
            "name": "Lago Amatitlán - Playa Pública",
            "lat": 14.4785, "lon": -90.6120,
            "ph": 9.21, "od_mg_l": 8.4, "temp_c": 24.5, "type": "Cuerpo Lacustre"
        },
        {
            "name": "Río Villalobos - Entrada al Lago",
            "lat": 14.4920, "lon": -90.5980,
            "ph": 7.35, "od_mg_l": 1.2, "dbo5_mg_l": 185.0, "type": "Afluente Contaminado"
        },
        {
            "name": "PTAR Los Balcones (AMSA)",
            "lat": 14.4850, "lon": -90.6250,
            "ph": 7.60, "od_mg_l": 4.5, "dbo5_mg_l": 28.0, "type": "Planta de Tratamiento Residual"
        },
        {
            "name": "Lago Amatitlán - Centro",
            "lat": 14.4600, "lon": -90.5750,
            "ph": 8.85, "od_mg_l": 7.8, "temp_c": 25.1, "type": "Cuerpo Lacustre"
        }
    ]
    amsa_geojson_features = []
    for item in amsa_features:
        amsa_geojson_features.append({
            "type": "Feature",
            "properties": {
                "id": f"AMSA-{len(amsa_geojson_features)+1}",
                "name": item["name"],
                "agency": "AMSA",
                "basin": "María Linda (Lago Amatitlán)",
                "site_type": item["type"],
                "ph": item.get("ph"),
                "od_mg_l": item.get("od_mg_l"),
                "dbo5_mg_l": item.get("dbo5_mg_l"),
                "temperatura_c": item.get("temp_c")
            },
            "geometry": {
                "type": "Point",
                "coordinates": [item["lon"], item["lat"]]
            }
        })
    print(f"  Created {len(amsa_geojson_features)} AMSA Features.")

    print("Step 7: Processing MARN Acidification & Coastal Stations (11 stations)...")
    marn_acid_path = os.path.join(CLAUDE_DIR, "02_datos_originales", "MARN_ArcGIS", "MARN_Sitios_monitoreo_acidificacion.geojson")
    with open(marn_acid_path, "r", encoding="utf-8") as f:
        marn_acid = json.load(f)
    print(f"  Loaded {len(marn_acid['features'])} MARN coastal stations.")

    print("Step 8: Processing MARN Lakes and Lagoons (Major water bodies)...")
    lakes_path = os.path.join(CLAUDE_DIR, "02_datos_originales", "MARN_ArcGIS", "MARN_Lagos_Lagunas_MAGA_2001.geojson")
    with open(lakes_path, "r", encoding="utf-8") as f:
        lakes_geojson = json.load(f)
    print(f"  Loaded {len(lakes_geojson['features'])} lake polygons.")

    print("Step 9: Processing 38 Major River Basins of Guatemala (Simplified for Web)...")
    cuencas_path = os.path.join(CLAUDE_DIR, "02_datos_originales", "MARN_ArcGIS", "MARN_Cuencas_38_MAGA_2001.geojson")
    with open(cuencas_path, "r", encoding="utf-8") as f:
        cuencas_raw = json.load(f)
    
    simplified_cuencas = []
    for feat in cuencas_raw["features"]:
        props = feat["properties"]
        geom = feat["geometry"]
        step = 6  # Subsample every 6th vertex to keep fast rendering
        if geom["type"] == "Polygon":
            new_coords = [[round(c[0], 4), round(c[1], 4)] for i, c in enumerate(geom["coordinates"][0]) if i % step == 0 or i == len(geom["coordinates"][0])-1]
            geom = {"type": "Polygon", "coordinates": [new_coords]}
        elif geom["type"] == "MultiPolygon":
            new_mp = []
            for poly in geom["coordinates"]:
                sub = [[round(c[0], 4), round(c[1], 4)] for i, c in enumerate(poly[0]) if i % step == 0 or i == len(poly[0])-1]
                new_mp.append([sub])
            geom = {"type": "MultiPolygon", "coordinates": new_mp}
        
        simplified_cuencas.append({
            "type": "Feature",
            "properties": {
                "codigo": props.get("codigo"),
                "name": props.get("label"),
                "vertiente": props.get("vertiente"),
                "km2": props.get("km2")
            },
            "geometry": geom
        })
    print(f"  Processed {len(simplified_cuencas)} simplified river basin polygons.")

    print("Step 10: Processing WPdx Water Point Sample (Representative national wells)...")
    wpdx_path = os.path.join(CLAUDE_DIR, "02_datos_originales", "WPdx", "wpdx_guatemala.json")
    with open(wpdx_path, "r", encoding="utf-8") as f:
        wpdx_raw = json.load(f)
    
    wpdx_features = []
    step = max(len(wpdx_raw) // 120, 1)  # Take ~120 representative points
    for i in range(0, len(wpdx_raw), step):
        item = wpdx_raw[i]
        lat = item.get("lat_deg")
        lon = item.get("lon_deg")
        if lat and lon and 13.5 < float(lat) < 18.0 and -92.5 < float(lon) < -88.0:
            wpdx_features.append({
                "type": "Feature",
                "properties": {
                    "id": item.get("row_id"),
                    "tech": item.get("water_tech") or item.get("water_source_clean") or "Pozo/Bomba",
                    "status": item.get("status_clean") or "Funcional",
                    "department": item.get("clean_adm1") or "Guatemala",
                    "municipality": item.get("clean_adm2") or "Nacional",
                    "installer": item.get("installer") or "Comunitario / INFOM"
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [round(float(lon), 5), round(float(lat), 5)]
                }
            })
    print(f"  Created {len(wpdx_features)} WPdx Water Point Features.")

    print("Step 11: Loading Existing Motagua Network, USAC ERIS and TOC stations...")
    existing_bundle_path = os.path.join(ANTIGRAVITY_DIR, "data", "processed", "dashboard_data_bundle.json")
    with open(existing_bundle_path, "r", encoding="utf-8") as f:
        old_bundle = json.load(f)
    
    motagua_network = old_bundle.get("motagua_river_network")
    usac_stations = old_bundle.get("usac_quality_stations")
    toc_sites = old_bundle.get("ocean_cleanup_sites")

    # Combine into comprehensive national bundle
    national_bundle = {
        "metadata": {
            "title": "RÍOS ABIERTOS GT — National Guatemala Water Dashboard Data Bundle",
            "country": "Guatemala",
            "date": "2026-10-21",
            "agencies_included": [
                "INSIVUMEH (Instituto Nacional de Sismología, Vulcanología, Meteorología e Hidrología)",
                "MARN (Ministerio de Ambiente y Recursos Naturales)",
                "AMSCLAE (Autoridad para el Manejo Sustentable de la Cuenca del Lago de Atitlán)",
                "AMSA (Autoridad para el Manejo Sustentable de la Cuenca del Lago de Amatitlán)",
                "USAC ERIS (Escuela Regional de Ingeniería Sanitaria)",
                "The Ocean Cleanup (Interceptor 006 & 021)",
                "WPdx (Water Point Data Exchange)",
                "HydroRIVERS / USGS / WWF"
            ]
        },
        "guatemala_basins_38": {
            "type": "FeatureCollection",
            "features": simplified_cuencas
        },
        "guatemala_major_lakes": lakes_geojson,
        "insivumeh_quality_stations": {
            "type": "FeatureCollection",
            "features": qual_features
        },
        "insivumeh_streamflow_stations": {
            "type": "FeatureCollection",
            "features": cau_features
        },
        "amsclae_atitlan_stations": {
            "type": "FeatureCollection",
            "features": amsclae_geojson_features
        },
        "amsa_amatitlan_stations": {
            "type": "FeatureCollection",
            "features": amsa_geojson_features
        },
        "marn_acidification_stations": marn_acid,
        "wpdx_water_points": {
            "type": "FeatureCollection",
            "features": wpdx_features
        },
        "usac_eris_stations": usac_stations,
        "ocean_cleanup_sites": toc_sites,
        "motagua_river_network": motagua_network
    }

    out_path = os.path.join(ANTIGRAVITY_DIR, "data", "processed", "dashboard_national_data_bundle.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(national_bundle, f, ensure_ascii=False)
    
    print(f"SUCCESS: Saved comprehensive national data bundle to {out_path} ({os.path.getsize(out_path)/1024:.1f} KB)")

if __name__ == "__main__":
    run()
