import json
import csv
import os
import pandas as pd

base_dir = "D:/Documentos D/BaseDatosGT H2O/Investigación Antigravity"

# 1. Load Motagua River reaches GeoJSON
motagua_geojson_path = os.path.join(base_dir, "data/processed/Motagua_River_Basin_Network.geojson")
with open(motagua_geojson_path, 'r', encoding='utf-8') as f:
    motagua_network = json.load(f)

print(f"Loaded {len(motagua_network.get('features', []))} Motagua river reaches.")

# 2. Load USAC ERIS 2025 Stations
usac_csv_path = os.path.join(base_dir, "data/processed/USAC_ERIS_Motagua_LasVacas_2025_Monitoring_Data.csv")
df_usac = pd.read_csv(usac_csv_path)

usac_features = []
for idx, row in df_usac.iterrows():
    feat = {
        "type": "Feature",
        "geometry": {
            "type": "Point",
            "coordinates": [float(row["longitud"]), float(row["latitud"])]
        },
        "properties": {
            "id": row["estacion_id"],
            "name": row["descripcion"],
            "category": "USAC ERIS Calidad & Fármacos (2025)",
            "water_body": row["cuerpo_agua"],
            "site_type": row["tipo_sitio"],
            "od_mg_l": row["oxigeno_disuelto_mg_l"] if pd.notnull(row["oxigeno_disuelto_mg_l"]) else None,
            "ph": row["ph"] if pd.notnull(row["ph"]) else None,
            "temp_c": row["temperatura_c"] if pd.notnull(row["temperatura_c"]) else None,
            "dbo5_mg_l": row["dbo5_mg_l"] if pd.notnull(row["dbo5_mg_l"]) else None,
            "dqo_mg_l": row["dqo_mg_l"] if pd.notnull(row["dqo_mg_l"]) else None,
            "sulfadiazina_ng_l": row["sulfadiazina_ng_l"] if pd.notnull(row["sulfadiazina_ng_l"]) else None,
            "sulfametoxazol_ng_l": row["sulfametoxazol_ng_l"] if pd.notnull(row["sulfametoxazol_ng_l"]) else None,
            "cafeina_ng_l": row["cafeina_ng_l"] if pd.notnull(row["cafeina_ng_l"]) else None,
            "source": "USAC ERIS (Paque López & Cáceres Sobalvarro 2025)"
        }
    }
    usac_features.append(feat)

print(f"Prepared {len(usac_features)} USAC ERIS station features.")

# 3. Load INSIVUMEH Real-Time Hydrometric Stations (Caribe & Motagua)
# From Bulletin BHVC-880-2026 and station database
insivumeh_stations = [
    {
        "id": "INS-CAR-01",
        "name": "Panajax — Río Las Vacas",
        "river": "Río Las Vacas",
        "location": "Sanarate, El Progreso",
        "coords": [-90.1983, 14.7892],
        "level_m": -0.14,
        "discharge_cms": 10.56,
        "normal_level_min": -0.35,
        "normal_level_max": 1.10,
        "normal_q_min": 7.29,
        "normal_q_max": 64.20,
        "status": "Río Normal (Tendencia Estable)",
        "basin": "Cuenca del Río Motagua",
        "date": "20/10/2026 20:00"
    },
    {
        "id": "INS-CAR-02",
        "name": "Gualán — Río Motagua",
        "river": "Río Motagua",
        "location": "Gualán, Zacapa",
        "coords": [-89.3586, 15.1328],
        "level_m": 2.20,
        "discharge_cms": 344.54,
        "normal_level_min": 0.80,
        "normal_level_max": 2.70,
        "normal_q_min": 34.26,
        "normal_q_max": 558.97,
        "status": "Río Normal (Caudal Alto)",
        "basin": "Cuenca del Río Motagua",
        "date": "20/10/2026 20:00"
    },
    {
        "id": "INS-CAR-03",
        "name": "Concuá II — Río Motagua",
        "river": "Río Motagua",
        "location": "Granados, Baja Verapaz",
        "coords": [-90.5217, 14.9122],
        "level_m": -0.09,
        "discharge_cms": 5.24,
        "normal_level_min": 0.01,
        "normal_level_max": 1.36,
        "normal_q_min": 7.26,
        "normal_q_max": 132.50,
        "status": "Río Bajo",
        "basin": "Cuenca del Río Motagua",
        "date": "20/10/2026 20:00"
    },
    {
        "id": "INS-CAR-04",
        "name": "Camotán — Río Camotán",
        "river": "Río Camotán (Afluente Motagua)",
        "location": "Camotán, Chiquimula",
        "coords": [-89.3736, 14.8214],
        "level_m": 1.00,
        "discharge_cms": 11.72,
        "normal_level_min": 0.79,
        "normal_level_max": 1.81,
        "normal_q_min": 6.18,
        "normal_q_max": 64.47,
        "status": "Río Normal",
        "basin": "Cuenca del Río Motagua",
        "date": "20/10/2026 20:00"
    },
    {
        "id": "INS-CAR-05",
        "name": "Vado Hondo — Río Shutaque",
        "river": "Río Shutaque (Afluente Motagua)",
        "location": "Chiquimula, Chiquimula",
        "coords": [-89.5167, 14.7333],
        "level_m": -0.30,
        "discharge_cms": 1.74,
        "normal_level_min": -0.39,
        "normal_level_max": 0.13,
        "normal_q_min": 0.33,
        "normal_q_max": 11.19,
        "status": "Río Normal",
        "basin": "Cuenca del Río Motagua",
        "date": "20/10/2026 20:00"
    },
    {
        "id": "INS-CAR-06",
        "name": "Mariscos — Lago de Izabal",
        "river": "Lago de Izabal (Desahogo Atlántico)",
        "location": "Los Amates, Izabal",
        "coords": [-89.1917, 15.4278],
        "level_m": 1.14,
        "discharge_cms": None,
        "normal_level_min": 0.52,
        "normal_level_max": 1.38,
        "normal_q_min": None,
        "normal_q_max": None,
        "status": "Nivel Normal",
        "basin": "Cuenca Río Dulce / Izabal",
        "date": "20/10/2026 20:00"
    },
    {
        "id": "INS-CAR-07",
        "name": "Santa Cruz — Río Cahabón",
        "river": "Río Cahabón",
        "location": "Santa Cruz Verapaz, Alta Verapaz",
        "coords": [-90.4333, 15.3667],
        "level_m": 1.30,
        "discharge_cms": 34.36,
        "normal_level_min": 0.36,
        "normal_level_max": 1.00,
        "normal_q_min": 1.08,
        "normal_q_max": 15.17,
        "status": "Río Crecido (Alerta BHE 0485-2026)",
        "basin": "Cuenca Río Polochic/Cahabón",
        "date": "20/10/2026 20:00"
    },
    {
        "id": "INS-CAR-08",
        "name": "Telemán — Río Polochic",
        "river": "Río Polochic",
        "location": "Panzós, Alta Verapaz",
        "coords": [-89.8667, 15.3500],
        "level_m": 3.18,
        "discharge_cms": 316.21,
        "normal_level_min": 0.52,
        "normal_level_max": 2.50,
        "normal_q_min": 33.91,
        "normal_q_max": 215.87,
        "status": "Río Crecido (Alerta BHE 0509-2026)",
        "basin": "Cuenca Río Polochic",
        "date": "20/10/2026 20:00"
    }
]

insivumeh_features = []
for st in insivumeh_stations:
    feat = {
        "type": "Feature",
        "geometry": {
            "type": "Point",
            "coordinates": st["coords"]
        },
        "properties": {
            "id": st["id"],
            "name": st["name"],
            "category": "INSIVUMEH Red Hidrológica (En Vivo 2026)",
            "water_body": st["river"],
            "location": st["location"],
            "level_m": st["level_m"],
            "discharge_cms": st["discharge_cms"],
            "normal_level_min": st["normal_level_min"],
            "normal_level_max": st["normal_level_max"],
            "normal_q_min": st["normal_q_min"],
            "normal_q_max": st["normal_q_max"],
            "status": st["status"],
            "date": st["date"],
            "source": "Boletín Hidrológico Oficial No. 880 (INSIVUMEH)"
        }
    }
    insivumeh_features.append(feat)

print(f"Prepared {len(insivumeh_features)} INSIVUMEH real-time hydrometric features.")

# 4. Load The Ocean Cleanup Plastic Outlets & Interceptor Stations
toc_stations = [
    {
        "id": "TOC-LASVACAS",
        "name": "The Ocean Cleanup — Interceptor 006 (The Barricade)",
        "coords": [-90.5006, 14.7551],
        "location": "San Antonio Las Flores / Chinautla, Río Las Vacas",
        "type": "Barrera Flotante Fluvial de Alta Resistencia",
        "captured_kg": ">10,000,000 kg acumulados",
        "peak_event": "Captura >1,000,000 kg en un solo evento de lluvia torrencial",
        "target": "Retención del 60%+ de desechos arrastrados desde vertedero Zona 3",
        "source": "The Ocean Cleanup Operational Reports (2023-2025)"
    },
    {
        "id": "TOC-QUETZALITO",
        "name": "The Ocean Cleanup — Interceptor 021 (Barricade XL)",
        "coords": [-88.2933, 15.7192],
        "location": "El Quetzalito, Desembocadura del Río Motagua",
        "type": "Sistema Barricade XL Desembocadura",
        "captured_kg": "Retención perimetral de plásticos antes del Golfo de Honduras",
        "peak_event": "Protección de arrecifes mesoamericanos",
        "target": "Interceptar plásticos residuales del Motagua inferior",
        "source": "The Ocean Cleanup & MARN"
    },
    {
        "id": "TOC-MORALES",
        "name": "Estación de Monitoreo de Flujo Morales (Meijer et al.)",
        "coords": [-88.8250, 15.4833],
        "location": "Puente Morales, Izabal (Río Motagua)",
        "type": "Estación Científica de Conteo Visual de Plásticos",
        "captured_kg": "Flujo medido: 44,968 ítems/h (Oct 2019)",
        "peak_event": "Flujo pico: 250.92 toneladas/mes",
        "target": "Calibración del modelo global de transporte fluvial de plástico",
        "source": "Meijer et al. Science Advances (2021) / USAC CEMA"
    }
]

toc_features = []
for st in toc_stations:
    feat = {
        "type": "Feature",
        "geometry": {
            "type": "Point",
            "coordinates": st["coords"]
        },
        "properties": {
            "id": st["id"],
            "name": st["name"],
            "category": "The Ocean Cleanup / Interceptor",
            "location": st["location"],
            "type": st["type"],
            "metrics": st["captured_kg"],
            "peak": st["peak_event"],
            "target": st["target"],
            "source": st["source"]
        }
    }
    toc_features.append(feat)

print(f"Prepared {len(toc_features)} Ocean Cleanup key infrastructure features.")

# Output combined dataset JSON bundle for dashboard
bundle = {
    "motagua_river_network": motagua_network,
    "usac_quality_stations": {
        "type": "FeatureCollection",
        "features": usac_features
    },
    "insivumeh_realtime_stations": {
        "type": "FeatureCollection",
        "features": insivumeh_features
    },
    "ocean_cleanup_stations": {
        "type": "FeatureCollection",
        "features": toc_features
    }
}

out_bundle_path = os.path.join(base_dir, "data/processed/dashboard_data_bundle.json")
with open(out_bundle_path, 'w', encoding='utf-8') as f:
    json.dump(bundle, f, ensure_ascii=False)

print(f"Successfully generated dashboard data bundle: {out_bundle_path} ({os.path.getsize(out_bundle_path):,} bytes)")
