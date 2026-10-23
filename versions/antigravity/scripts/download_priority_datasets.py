import sys
import os
import requests
import json
import zipfile
import io

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

base_dir = "D:/Documentos D/BaseDatosGT H2O/Investigación Antigravity"
data_dir = os.path.join(base_dir, "data/raw")
os.makedirs(data_dir, exist_ok=True)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

download_manifest = []

def download_file(url, out_path, category, description):
    print(f"\nDownloading: {description}")
    print(f"  URL: {url}")
    try:
        r = requests.get(url, headers=headers, timeout=45, stream=True)
        if r.status_code == 200:
            os.makedirs(os.path.dirname(out_path), exist_ok=True)
            total_size = 0
            with open(out_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=65536):
                    if chunk:
                        f.write(chunk)
                        total_size += len(chunk)
            print(f"  SUCCESS: Saved {out_path} ({total_size:,} bytes)")
            download_manifest.append({
                'category': category,
                'description': description,
                'url': url,
                'path': out_path,
                'size_bytes': total_size,
                'status': 'Downloaded'
            })
            return True
        else:
            print(f"  FAILED: HTTP {r.status_code}")
            download_manifest.append({
                'category': category,
                'description': description,
                'url': url,
                'status': f"Failed (HTTP {r.status_code})"
            })
            return False
    except Exception as e:
        print(f"  ERROR: {e}")
        download_manifest.append({
            'category': category,
            'description': description,
            'url': url,
            'status': f"Error: {e}"
        })
        return False

# 1. Science Advances (Meijer et al. 2021) Supplementary Data - Global River Plastic Emissions (>1000 rivers, including Rio Motagua)
url_meijer_supp = "https://www.science.org/doi/suppl/10.1126/sciadv.aaz5803/suppl_file/aaz5803_data_s1.xlsx"
path_meijer_supp = os.path.join(data_dir, "ngos_cleanup/Meijer2021_ScienceAdvances_RiverPlastics_Motagua.xlsx")
download_file(url_meijer_supp, path_meijer_supp, "NGOs & Solid Waste", "Meijer et al. 2021 Science Advances - River Plastic Emissions (>1000 rivers incl. Rio Motagua)")

# 2. JMP Country Files from washdata.org
url_jmp_gtm = "https://washdata.org/sites/default/files/2023-07/jmp-2023-wat-san-hyg-guatemala.xlsx"
# Let's also try the global estimates table
url_jmp_global = "https://washdata.org/sites/default/files/2023-07/jmp-2023-wash-households.xlsx"
path_jmp_global = os.path.join(data_dir, "international/JMP_2023_WASH_Households.xlsx")
download_file(url_jmp_global, path_jmp_global, "International", "WHO/UNICEF JMP 2023 Global Household WASH Estimates")

# 3. FAO AQUASTAT Country Profile and Data
url_fao_aquastat_gtm = "https://www.fao.org/aquastat/statistics/query/results.html" # query via API or CSV
# FAO AQUASTAT Bulk Data API / Country Factsheet
url_fao_factsheet = "https://www.fao.org/countryprofiles/index/en/?iso3=GTM"

# 4. FUNCAGUA Reports (Estado del Agua en la Región Metropolitana de Guatemala)
url_funcagua_2022 = "https://funcagua.org.gt/wp-content/uploads/2022/10/Informe-de-la-Situacion-del-Agua-2022.pdf"
path_funcagua_2022 = os.path.join(data_dir, "academic/FUNCAGUA_Informe_Situacion_del_Agua_2022.pdf")
download_file(url_funcagua_2022, path_funcagua_2022, "Groundwater & Hydrology", "FUNCAGUA - Informe de la Situación del Agua en la Región Metropolitana de Guatemala 2022")

# 5. AMSCLAE Cianoséforo y Monitoreo de Cianobacterias en Lago de Atitlán
url_amsclae_pdf = "https://www.amsclae.gob.gt/wp-content/uploads/2022/09/cianosemaforo.pdf"
path_amsclae_pdf = os.path.join(data_dir, "government/AMSCLAE_Cianosemaforo_Atitlan.pdf")
download_file(url_amsclae_pdf, path_amsclae_pdf, "Government", "AMSCLAE - Cianosemáforo Lago de Atitlán")

# 6. Global Reservoir and Dam Database (GRanD) / HydroLAKES
# HydroLAKES provides polygons, lake depth, volume, residence time for Lake Atitlan, Lake Amatitlan, Lake Izabal
url_hydrolakes_meta = "https://www.hydrosheds.org/products/hydrolakes"

print("\nFinished first wave of downloads.")
with open(os.path.join(base_dir, "manifests/download_status.json"), 'w', encoding='utf-8') as f:
    json.dump(download_manifest, f, indent=2)
