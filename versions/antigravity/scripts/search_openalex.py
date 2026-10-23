import sys
import requests
import json
import os

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

queries = [
    ("Motagua Basin", 'default.search:Motagua AND Guatemala AND (water OR river OR rio OR agua OR basin OR cuenca OR plastic OR calidad OR microplastic)'),
    ("Rio Las Vacas", 'default.search:("Las Vacas" OR "rio Las Vacas") AND Guatemala AND (water OR river OR rio OR agua OR contaminacion OR residual)'),
    ("Lake Amatitlan", 'default.search:Amatitlan AND Guatemala AND (water OR calidad OR lake OR limnology OR eutrophication OR lago OR cianobacterias)'),
    ("Lake Atitlan", 'default.search:Atitlan AND Guatemala AND (water OR calidad OR lake OR limnology OR eutrophication OR lago OR cyanobacteria OR cianobacterias)'),
    ("Guatemala Water Quality", 'default.search:Guatemala AND ("water quality" OR "calidad del agua" OR "calidad de agua" OR "metales pesados" OR "heavy metals" OR "coliformes" OR "contaminacion hidrica")'),
    ("Guatemala Groundwater", 'default.search:Guatemala AND (groundwater OR "agua subterranea" OR "acuifero" OR "acuiferos" OR "FUNCAGUA" OR hidrogeologia)'),
    ("Guatemala Hydrology", 'default.search:Guatemala AND (INSIVUMEH OR "estaciones hidrologicas" OR "caudal" OR "aforo" OR streamflow OR "cuenca hidrografica")'),
    ("Ocean Cleanup Motagua", 'default.search:"Ocean Cleanup" AND (Guatemala OR Motagua OR "Las Vacas")')
]

all_works = {}

for label, q in queries:
    print(f"\n=== Query: {label} ===")
    r = requests.get('https://api.openalex.org/works', params={
        'filter': q,
        'per-page': 35,
        'sort': 'cited_by_count:desc'
    }, headers={'User-Agent': 'mailto:openwater_gt@antigravity.org'})
    
    if r.status_code == 200:
        res = r.json()
        count = res.get('meta', {}).get('count', 0)
        print(f"Total found in OpenAlex: {count}")
        for w in res.get('results', []):
            wid = w.get('id')
            title = w.get('title')
            year = w.get('publication_year')
            doi = w.get('doi')
            oa_url = (w.get('open_access') or {}).get('oa_url')
            if wid not in all_works:
                all_works[wid] = {
                    'title': title,
                    'year': year,
                    'doi': doi,
                    'authors': [a.get('author', {}).get('display_name') for a in w.get('authorships', [])],
                    'venue': (w.get('primary_location') or {}).get('source', {}).get('display_name') if w.get('primary_location') and w.get('primary_location').get('source') else None,
                    'is_oa': (w.get('open_access') or {}).get('is_oa'),
                    'oa_url': oa_url,
                    'landing_page_url': (w.get('primary_location') or {}).get('landing_page_url'),
                    'cited_by_count': w.get('cited_by_count'),
                    'query_topic': label,
                    'type': w.get('type')
                }
                print(f"  [{year}] {title} (DOI: {doi}) | OA: {oa_url is not None}")

out_path = 'D:/Documentos D/BaseDatosGT H2O/Investigación Antigravity/data/raw/publications/openalex_relevant_works.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(all_works, f, indent=2, ensure_ascii=False)
print(f"\nSuccessfully saved {len(all_works)} unique works to {out_path}")
