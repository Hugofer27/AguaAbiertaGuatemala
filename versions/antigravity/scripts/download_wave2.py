import requests
import os
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

downloads = [
    # INSIVUMEH Boletines Diarios de Niveles y Caudales
    ("INSIVUMEH_Boletin_Caribe_Motagua.pdf", "https://insivumeh.gob.gt/hidrologia/hidro/niveles/BHVC.pdf", "D:/Documentos D/BaseDatosGT H2O/Investigación Antigravity/data/raw/government"),
    ("INSIVUMEH_Boletin_Pacifico.pdf", "https://insivumeh.gob.gt/hidrologia/hidro/niveles/BHVP.pdf", "D:/Documentos D/BaseDatosGT H2O/Investigación Antigravity/data/raw/government"),
    ("INSIVUMEH_Boletin_GolfoMexico.pdf", "https://insivumeh.gob.gt/hidrologia/hidro/niveles/BHVGM.pdf", "D:/Documentos D/BaseDatosGT H2O/Investigación Antigravity/data/raw/government"),
    
    # AMSCLAE DICA 2024 & Recreacional
    ("AMSCLAE_Informe_DICA_2024.pdf", "https://www.amsclae.gob.gt/wp-content/uploads/2025/02/InformesDICA2024.pdf", "D:/Documentos D/BaseDatosGT H2O/Investigación Antigravity/data/raw/government"),
    ("AMSCLAE_Uso_Recreacional_Playas_2021.pdf", "https://www.amsclae.gob.gt/wp-content/uploads/2021/12/usorecreacional2021.pdf", "D:/Documentos D/BaseDatosGT H2O/Investigación Antigravity/data/raw/government"),
    
    # USAC Tesis de Grado con datos cuantitativos
    ("USAC_LasVacas_ISQA_BMWP_BocelCastro_2021.pdf", "http://www.repositorio.usac.edu.gt/16477/1/Crispy%20Lam%C3%A9c%20Bocel%20Castro.pdf", "D:/Documentos D/BaseDatosGT H2O/Investigación Antigravity/data/raw/academic"),
    ("USAC_Monitoreo_Rios_MuniGuate_Urrutia_2020.pdf", "http://www.repositorio.usac.edu.gt/15296/1/Marco%20Antonio%20Urrutia%20Campo.pdf", "D:/Documentos D/BaseDatosGT H2O/Investigación Antigravity/data/raw/academic"),
    ("USAC_Rio_Marrullero_LasVacas_Coloma_2021.pdf", "http://www.repositorio.usac.edu.gt/16367/1/Arlene%20Jocabed%20Coloma%20Leiva.pdf", "D:/Documentos D/BaseDatosGT H2O/Investigación Antigravity/data/raw/academic"),
    ("USAC_Rio_Platanitos_Vanegas_2014.pdf", "http://www.repositorio.usac.edu.gt/4515/1/Eddi%20Alejandro%20Vanegas%20Chac%C3%B3n.pdf", "D:/Documentos D/BaseDatosGT H2O/Investigación Antigravity/data/raw/academic")
]

for name, url, out_dir in downloads:
    os.makedirs(out_dir, exist_ok=True)
    dest = os.path.join(out_dir, name)
    try:
        r = requests.get(url, headers=headers, timeout=45, verify=False)
        print(f"{name} -> HTTP {r.status_code}, {len(r.content):,} bytes")
        if r.status_code == 200 and len(r.content) > 1000:
            with open(dest, 'wb') as f:
                f.write(r.content)
            print(f"  SAVED to {dest}")
        else:
            print(f"  FAILED or too small: {r.status_code}")
    except Exception as e:
        print(f"  ERROR {name}: {e}")
