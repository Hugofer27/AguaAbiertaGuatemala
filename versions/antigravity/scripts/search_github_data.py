import sys
import os
import requests
import json

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

headers = {'User-Agent': 'Mozilla/5.0'}
queries = ['insivumeh', 'guatemala water', 'motagua river', 'rio motagua', 'lago atitlan water', 'cuenca motagua', 'funcagua']

results = {}
for q in queries:
    url = f"https://api.github.com/search/repositories?q={requests.utils.quote(q)}&per_page=10"
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        data = r.json()
        items = []
        for item in data.get('items', []):
            items.append({
                'full_name': item.get('full_name'),
                'description': item.get('description'),
                'html_url': item.get('html_url'),
                'stars': item.get('stargazers_count'),
                'updated_at': item.get('updated_at'),
                'language': item.get('language')
            })
        results[q] = {
            'total_count': data.get('total_count'),
            'items': items
        }
        print(f"Query '{q}': found {data.get('total_count')} repositories.")
        for it in items[:3]:
            print(f"  - {it['full_name']} [{it['language']}]: {it['description']}")
    else:
        print(f"Query '{q}' returned status {r.status_code}")

out_path = "D:/Documentos D/BaseDatosGT H2O/Investigación Antigravity/data/raw/publications/github_repositories.json"
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f"Saved results to {out_path}")
