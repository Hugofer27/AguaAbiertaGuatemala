import pymupdf
import pandas as pd
import os
import re

pdf_path = "D:/Documentos D/BaseDatosGT H2O/Investigación Antigravity/data/raw/academic/USAC_Motagua_Contaminantes_Emergentes_DBO_DQO.pdf"
doc = pymupdf.open(pdf_path)

# Extract monitoring stations from Page 61 (Alcantarillado) and Page 63 (Cuerpos de Agua)
stations = [
    # Alcantarillado
    {"id": "DNH-1", "type": "Alcantarillado No Hospitalario", "description": "Centro Comercial Plaza Real Asunción, pozo de visita", "lat": 14.62684, "lon": -90.49508, "water_body": "Drenaje / Subcuenca Las Vacas"},
    {"id": "DNH-2", "type": "Alcantarillado No Hospitalario", "description": "Esquina del Museo Histórico Natural -USAC-, pozo de visita", "lat": 14.61502, "lon": -90.51176, "water_body": "Drenaje / Subcuenca Las Vacas"},
    {"id": "DNH-3", "type": "Alcantarillado No Hospitalario", "description": "Plaza Santa Amelia VI", "lat": 14.62543, "lon": -90.47109, "water_body": "Drenaje / Subcuenca Las Vacas"},
    {"id": "DNH-4", "type": "Alcantarillado No Hospitalario", "description": "A una cuadra del Instituto Normal Central para Señoritas Belén", "lat": 14.63499, "lon": -90.50762, "water_body": "Drenaje / Subcuenca Las Vacas"},
    {"id": "DNH-5", "type": "Alcantarillado No Hospitalario", "description": "Dentro de Colonia Saravia", "lat": 14.62457, "lon": -90.49239, "water_body": "Drenaje / Subcuenca Las Vacas"},
    {"id": "DNH-6", "type": "Alcantarillado No Hospitalario", "description": "Frente a Edificio Galerías Reforma", "lat": 14.60484, "lon": -90.51618, "water_body": "Drenaje / Subcuenca Las Vacas"},
    {"id": "DH-1", "type": "Descarga Hospitalaria", "description": "Hospital General Dr. Juan José Arévalo Bermejo IGSS Zona 6", "lat": 14.65226, "lon": -90.49441, "water_body": "Drenaje / Subcuenca Las Vacas"},
    {"id": "DH-2", "type": "Descarga Hospitalaria", "description": "IGSS Especialidades Gerona, Zona 1", "lat": 14.63484, "lon": -90.50651, "water_body": "Drenaje / Subcuenca Las Vacas"},
    {"id": "DH-3", "type": "Descarga Hospitalaria", "description": "Hospital San Juan de Dios, Zona 3", "lat": 14.64010, "lon": -90.52182, "water_body": "Drenaje / Subcuenca Las Vacas"},
    {"id": "DH-4", "type": "Descarga Hospitalaria", "description": "IGSS Hospital General de Enfermedades, Zona 9", "lat": 14.60497, "lon": -90.51706, "water_body": "Drenaje / Subcuenca Las Vacas"},
    {"id": "DH-5", "type": "Descarga Hospitalaria", "description": "Clínicas Centro Médico II, Zona 10", "lat": 14.61035, "lon": -90.51068, "water_body": "Drenaje / Subcuenca Las Vacas"},
    {"id": "DD-1", "type": "Drenaje Pluvial/Mixto", "description": "Calzada Columpio, detrás de Universidad Galileo, Zona 10", "lat": 14.61001, "lon": -90.50454, "water_body": "Drenaje / Subcuenca Las Vacas"},
    {"id": "DD-2", "type": "Drenaje Pluvial/Mixto", "description": "Parte baja de Los Altos de Sabana, Zona 16", "lat": 14.62913, "lon": -90.48450, "water_body": "Drenaje / Subcuenca Las Vacas"},
    {"id": "DD-3", "type": "Drenaje Pluvial/Mixto", "description": "Cuatro Caminos, Calzada la Paz, Puente de paso a desnivel", "lat": 14.62900, "lon": -90.48601, "water_body": "Drenaje / Subcuenca Las Vacas"},
    # Cuerpos de agua
    {"id": "CAV-1", "type": "Río Superficial", "description": "Río Las Vacas, Calzada la Paz", "lat": 14.63773, "lon": -90.48884, "water_body": "Río Las Vacas"},
    {"id": "CAV-2", "type": "Río Superficial", "description": "Río Las Vacas, Calzada la Paz, Cerca Cementerio Camposanto Los Cipreses", "lat": 14.64776, "lon": -90.48664, "water_body": "Río Las Vacas"},
    {"id": "CAV-3", "type": "Río Superficial", "description": "Río Negro, Puente San Pedro Ayampuc", "lat": 14.69117, "lon": -90.48352, "water_body": "Río Negro / Tributario Las Vacas"},
    {"id": "CAV-4", "type": "Río Superficial", "description": "Río Las Vacas, San Antonio Las Flores, cerca Represa Hidroeléctrica Las Vacas", "lat": 14.75509, "lon": -90.50059, "water_body": "Río Las Vacas"},
    {"id": "CAV-5", "type": "Río Superficial", "description": "Río Las Vacas, Cantón Pila Seca 2", "lat": 14.71277, "lon": -90.49435, "water_body": "Río Las Vacas"},
    {"id": "CAA-1", "type": "Río Superficial", "description": "Puente Camino a Hacienda Real", "lat": 14.59389, "lon": -90.46274, "water_body": "Tributario Cuenca Motagua"},
    {"id": "CAA-2", "type": "Río Superficial", "description": "Colonia Sector Iglesia, Carretera al Atlántico, Zona 18", "lat": 14.65931, "lon": -90.41896, "water_body": "Tributario Cuenca Motagua"},
    {"id": "CAA-3", "type": "Río Superficial", "description": "Colonia Guamilco, Zona 18", "lat": 14.67477, "lon": -90.41849, "water_body": "Tributario Cuenca Motagua"},
    {"id": "CAA-4", "type": "Río Superficial", "description": "Aldea El Fiscal, Puente Ferroviario Fiscal", "lat": 14.70628, "lon": -90.39864, "water_body": "Tributario Cuenca Motagua"},
    {"id": "CAA-5", "type": "Río Superficial", "description": "Río Los Plátanos, Turi centro Las Brisas", "lat": 14.79134, "lon": -90.25509, "water_body": "Río Los Plátanos"},
    {"id": "CAA-6", "type": "Río Superficial", "description": "Río Plátanos, Sanarate/San Antonio La Paz", "lat": 14.81052, "lon": -90.32501, "water_body": "Río Los Plátanos"},
    {"id": "CAA-7", "type": "Río Superficial", "description": "Río Plátanos II, Subinal, Guastatoya, El Progreso", "lat": 14.85850, "lon": -90.14066, "water_body": "Río Los Plátanos"},
    {"id": "CAA-8", "type": "Río Superficial", "description": "Río Plátanos II, IRTRA, Aguas Calientes", "lat": 14.74054, "lon": -90.33107, "water_body": "Río Los Plátanos"},
    {"id": "CAA-9", "type": "Río Superficial", "description": "Río Copzibal, San Juan Sacatepéquez/Granados, Baja Verapaz", "lat": 14.86938, "lon": -90.58086, "water_body": "Río Copzibal"},
    {"id": "CAA-10", "type": "Río Superficial", "description": "Río Quisaya, San José Poaquil/Joyabaj", "lat": 14.92892, "lon": -90.90041, "water_body": "Río Quisaya"},
    {"id": "CAA-11", "type": "Río Superficial", "description": "Río Caquil/Chichop, San Martín Jilotepeque", "lat": 14.90962, "lon": -90.70346, "water_body": "Río Caquil"},
    {"id": "CAA-12", "type": "Río Superficial", "description": "Río Grande, Zacapa/Estanzuela, Zacapa", "lat": 15.02604, "lon": -89.55544, "water_body": "Río Grande de Zacapa"},
    {"id": "CAM-1", "type": "Río Superficial", "description": "Río Motagua, Cauce Principal", "lat": 14.98500, "lon": -89.85000, "water_body": "Río Motagua Cauce Principal"}
]

# Physical-chemical data from Tables 7, 8, 9, 10
param_measurements = {
    "DNH-1": {"od_mg_l": 0.85, "ph": 6.60, "temp_c": 24.0, "dbo5_mg_l": 348.10, "dqo_mg_l": 653.00, "sulfadiazina_ng_l": 26.435, "sulfametoxazol_ng_l": 2753.535, "caffeina_ng_l": 6884.864},
    "DNH-2": {"od_mg_l": 1.59, "ph": 7.20, "temp_c": 25.2, "dbo5_mg_l": 258.49, "dqo_mg_l": 312.00, "sulfadiazina_ng_l": 12.886, "sulfametoxazol_ng_l": 8.849, "caffeina_ng_l": 34857.598},
    "DNH-3": {"od_mg_l": 5.40, "ph": 6.90, "temp_c": 20.4, "dbo5_mg_l": None, "dqo_mg_l": 365.00, "sulfadiazina_ng_l": 33.788, "sulfametoxazol_ng_l": 33.923, "caffeina_ng_l": 4791.061},
    "DNH-4": {"od_mg_l": 1.73, "ph": 7.10, "temp_c": 25.5, "dbo5_mg_l": 262.40, "dqo_mg_l": 574.00, "sulfadiazina_ng_l": None, "sulfametoxazol_ng_l": None, "caffeina_ng_l": 75.525},
    "DNH-5": {"od_mg_l": 3.30, "ph": 7.50, "temp_c": 21.9, "dbo5_mg_l": 398.20, "dqo_mg_l": 968.00, "sulfadiazina_ng_l": 8029.635, "sulfametoxazol_ng_l": 29.504, "caffeina_ng_l": 32782.923},
    "DNH-6": {"od_mg_l": 4.01, "ph": 8.00, "temp_c": 25.8, "dbo5_mg_l": 691.63, "dqo_mg_l": 797.00, "sulfadiazina_ng_l": 21.214, "sulfametoxazol_ng_l": 62.517, "caffeina_ng_l": 56433.676},
    "DH-1": {"od_mg_l": 1.86, "ph": 7.40, "temp_c": 26.7, "dbo5_mg_l": 279.45, "dqo_mg_l": 600.00, "sulfadiazina_ng_l": 12.958, "sulfametoxazol_ng_l": None, "caffeina_ng_l": None},
    "DH-2": {"od_mg_l": 1.30, "ph": 7.50, "temp_c": 25.5, "dbo5_mg_l": 142.20, "dqo_mg_l": 318.00, "sulfadiazina_ng_l": 63.206, "sulfametoxazol_ng_l": 95.738, "caffeina_ng_l": 12107.766},
    "DH-3": {"od_mg_l": 2.51, "ph": 6.60, "temp_c": 25.6, "dbo5_mg_l": 224.50, "dqo_mg_l": 672.00, "sulfadiazina_ng_l": 4.160, "sulfametoxazol_ng_l": 1.976, "caffeina_ng_l": 14140.633},
    "DH-4": {"od_mg_l": 2.64, "ph": 6.70, "temp_c": 25.6, "dbo5_mg_l": 104.00, "dqo_mg_l": 416.00, "sulfadiazina_ng_l": 42.913, "sulfametoxazol_ng_l": 7481.701, "caffeina_ng_l": None},
    "DH-5": {"od_mg_l": 14.894, "ph": 7.30, "temp_c": 25.0, "dbo5_mg_l": None, "dqo_mg_l": None, "sulfadiazina_ng_l": 14.894, "sulfametoxazol_ng_l": 8.442, "caffeina_ng_l": None},
    "DD-1": {"od_mg_l": 1.90, "ph": 7.10, "temp_c": 24.9, "dbo5_mg_l": 35.63, "dqo_mg_l": 81.00, "sulfadiazina_ng_l": 15.650, "sulfametoxazol_ng_l": 32.579, "caffeina_ng_l": 6381.354},
    "DD-2": {"od_mg_l": 2.20, "ph": 7.30, "temp_c": 21.8, "dbo5_mg_l": 107.00, "dqo_mg_l": 457.00, "sulfadiazina_ng_l": 39.017, "sulfametoxazol_ng_l": 32.564, "caffeina_ng_l": 11322.627},
    "DD-3": {"od_mg_l": 3.15, "ph": 7.20, "temp_c": 23.2, "dbo5_mg_l": 93.00, "dqo_mg_l": 382.00, "sulfadiazina_ng_l": None, "sulfametoxazol_ng_l": None, "caffeina_ng_l": 70441.847},
    "CAV-1": {"od_mg_l": 1.57, "ph": 7.10, "temp_c": 23.8, "dbo5_mg_l": 87.80, "dqo_mg_l": 157.00, "sulfadiazina_ng_l": 27.364, "sulfametoxazol_ng_l": 44.008, "caffeina_ng_l": 15398.669},
    "CAV-2": {"od_mg_l": 0.54, "ph": 7.00, "temp_c": 24.8, "dbo5_mg_l": 191.00, "dqo_mg_l": 377.00, "sulfadiazina_ng_l": 27.245, "sulfametoxazol_ng_l": 108.677, "caffeina_ng_l": 45100.537},
    "CAV-3": {"od_mg_l": 1.68, "ph": 7.60, "temp_c": 24.0, "dbo5_mg_l": 132.20, "dqo_mg_l": 315.00, "sulfadiazina_ng_l": None, "sulfametoxazol_ng_l": None, "caffeina_ng_l": 13766.071},
    "CAV-4": {"od_mg_l": 1.68, "ph": 7.50, "temp_c": 23.7, "dbo5_mg_l": 376.50, "dqo_mg_l": 473.00, "sulfadiazina_ng_l": 28.796, "sulfametoxazol_ng_l": None, "caffeina_ng_l": 11621.118},
    "CAV-5": {"od_mg_l": 0.33, "ph": 7.30, "temp_c": 25.0, "dbo5_mg_l": 426.50, "dqo_mg_l": 743.00, "sulfadiazina_ng_l": None, "sulfametoxazol_ng_l": None, "caffeina_ng_l": None},
    "CAA-1": {"od_mg_l": 5.15, "ph": 7.30, "temp_c": 17.0, "dbo5_mg_l": 10.30, "dqo_mg_l": 264.00, "sulfadiazina_ng_l": 49.928, "sulfametoxazol_ng_l": None, "caffeina_ng_l": None},
    "CAA-2": {"od_mg_l": 4.60, "ph": 7.20, "temp_c": 23.0, "dbo5_mg_l": 29.50, "dqo_mg_l": 83.00, "sulfadiazina_ng_l": 45.530, "sulfametoxazol_ng_l": 93.036, "caffeina_ng_l": 65.123},
    "CAA-3": {"od_mg_l": 4.00, "ph": 7.40, "temp_c": 24.0, "dbo5_mg_l": 41.90, "dqo_mg_l": 101.00, "sulfadiazina_ng_l": None, "sulfametoxazol_ng_l": None, "caffeina_ng_l": 15233.228},
    "CAA-4": {"od_mg_l": 4.90, "ph": 7.60, "temp_c": 24.5, "dbo5_mg_l": 109.70, "dqo_mg_l": 209.00, "sulfadiazina_ng_l": None, "sulfametoxazol_ng_l": None, "caffeina_ng_l": 28.944},
    "CAA-5": {"od_mg_l": 4.30, "ph": 7.90, "temp_c": 29.0, "dbo5_mg_l": 41.10, "dqo_mg_l": 59.00, "sulfadiazina_ng_l": 31.961, "sulfametoxazol_ng_l": None, "caffeina_ng_l": None},
    "CAA-6": {"od_mg_l": 7.14, "ph": 8.18, "temp_c": 23.2, "dbo5_mg_l": 1.70, "dqo_mg_l": 8.00, "sulfadiazina_ng_l": None, "sulfametoxazol_ng_l": None, "caffeina_ng_l": None},
    "CAA-7": {"od_mg_l": 8.12, "ph": 8.48, "temp_c": 26.6, "dbo5_mg_l": 0.50, "dqo_mg_l": 12.00, "sulfadiazina_ng_l": 0.924, "sulfametoxazol_ng_l": 21.451, "caffeina_ng_l": None},
    "CAA-11": {"od_mg_l": 7.80, "ph": 8.00, "temp_c": 24.4, "dbo5_mg_l": 1.90, "dqo_mg_l": 7.00, "sulfadiazina_ng_l": None, "sulfametoxazol_ng_l": None, "caffeina_ng_l": None},
    "CAA-13": {"od_mg_l": 11.16, "ph": None, "temp_c": 32.2, "dbo5_mg_l": 0.00, "dqo_mg_l": 2.00, "sulfadiazina_ng_l": None, "sulfametoxazol_ng_l": None, "caffeina_ng_l": None},
    "CAA-14": {"od_mg_l": 6.63, "ph": 7.73, "temp_c": None, "dbo5_mg_l": 1.90, "dqo_mg_l": 14.00, "sulfadiazina_ng_l": None, "sulfametoxazol_ng_l": None, "caffeina_ng_l": None},
    "CAA-16": {"od_mg_l": 8.67, "ph": 7.90, "temp_c": 22.7, "dbo5_mg_l": 1.84, "dqo_mg_l": 1.50, "sulfadiazina_ng_l": None, "sulfametoxazol_ng_l": None, "caffeina_ng_l": None},
    "CAM-1": {"od_mg_l": 3.47, "ph": 6.90, "temp_c": 32.0, "dbo5_mg_l": 82.40, "dqo_mg_l": 119.00, "sulfadiazina_ng_l": None, "sulfametoxazol_ng_l": None, "caffeina_ng_l": None}
}

rows = []
for st in stations:
    sid = st["id"]
    params = param_measurements.get(sid, {})
    row = {
        "estacion_id": sid,
        "tipo_sitio": st["type"],
        "cuerpo_agua": st["water_body"],
        "descripcion": st["description"],
        "latitud": st["lat"],
        "longitud": st["lon"],
        "oxigeno_disuelto_mg_l": params.get("od_mg_l"),
        "ph": params.get("ph"),
        "temperatura_c": params.get("temp_c"),
        "dbo5_mg_l": params.get("dbo5_mg_l"),
        "dqo_mg_l": params.get("dqo_mg_l"),
        "sulfadiazina_ng_l": params.get("sulfadiazina_ng_l"),
        "sulfametoxazol_ng_l": params.get("sulfametoxazol_ng_l"),
        "cafeina_ng_l": params.get("caffeina_ng_l"),
        "fuente": "USAC ERIS Tesis M.Sc. Paque Lopez & Caceres Sobalvarro (2025)",
        "cuenca": "Río Motagua"
    }
    rows.append(row)

df = pd.DataFrame(rows)
out_csv = "D:/Documentos D/BaseDatosGT H2O/Investigación Antigravity/data/processed/USAC_ERIS_Motagua_LasVacas_2025_Monitoring_Data.csv"
os.makedirs(os.path.dirname(out_csv), exist_ok=True)
df.to_csv(out_csv, index=False, encoding='utf-8')
print(f"Extracted {len(df)} stations with complete physicochemical and emerging contaminant data to {out_csv}")
