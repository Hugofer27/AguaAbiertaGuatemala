import sys
import os
import requests

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

headers = {'User-Agent': 'Mozilla/5.0'}
repos = ['drwatercambioclima-eng/DatosEstacionesINSIVUMEH', 'PJH720/EnvEcon_MarineDebris_DID_2025']

for repo in repos:
    r = requests.get(f'https://api.github.com/repos/{repo}/contents', headers=headers)
    if r.status_code == 200:
        print(f"\n=== {repo} ===")
        for item in r.json():
            name = item.get('name')
            ftype = item.get('type')
            size = item.get('size', 0)
            durl = item.get('download_url')
            print(f"  [{ftype}] {name} ({size:,} bytes)")
            # If there's a subfolder or data file, let's inspect
            if ftype == 'dir':
                r_sub = requests.get(item.get('url'), headers=headers)
                if r_sub.status_code == 200:
                    for sub_item in r_sub.json()[:10]:
                        print(f"    - [{sub_item.get('type')}] {sub_item.get('name')} ({sub_item.get('size', 0):,} bytes) -> {sub_item.get('download_url')}")
