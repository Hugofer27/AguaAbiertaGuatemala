import sys
import os
import requests
import json

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

headers = {'User-Agent': 'Mozilla/5.0'}
queries = [
    'Atitlan water',
    'Amatitlan water',
    'Motagua water',
    'Guatemala groundwater',
    'Guatemala river',
    'Guatemala limnology',
    'Guatemala sediment'
]

zenodo_results = []
for q in queries:
    url = f"https://zenodo.org/api/records?q={requests.utils.quote(q)}&size=15"
    try:
        r = requests.get(url, headers=headers, timeout=15)
        if r.status_code == 200:
            data = r.json()
            hits = data.get('hits', {}).get('hits', [])
            print(f"Zenodo '{q}': {len(hits)} hits")
            for h in hits:
                files = h.get('files', [])
                if files:
                    meta = h.get('metadata', {})
                    rec = {
                        'query': q,
                        'id': h.get('id'),
                        'doi': h.get('doi'),
                        'title': meta.get('title'),
                        'publication_date': meta.get('publication_date'),
                        'creators': [c.get('name') for c in meta.get('creators', [])],
                        'description': meta.get('description', '')[:300],
                        'files': [{'key': f.get('key'), 'size': f.get('size'), 'download_url': f.get('links', {}).get('self')} for f in files],
                        'record_url': h.get('links', {}).get('self_html')
                    }
                    zenodo_results.append(rec)
                    print(f"  [{rec['publication_date']}] {rec['title']} -> {[f['key'] for f in rec['files']]}")
    except Exception as e:
        print(f"Error {q}: {e}")

out_path = "D:/Documentos D/BaseDatosGT H2O/Investigación Antigravity/data/raw/publications/zenodo_water_records.json"
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(zenodo_results, f, indent=2, ensure_ascii=False)
print(f"\nSaved {len(zenodo_results)} Zenodo records with downloadable files to {out_path}")
