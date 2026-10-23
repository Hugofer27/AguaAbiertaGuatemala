import requests
import re
import json

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
r = requests.get('https://washdata.org/data/tables', headers=headers)
print('Status:', r.status_code)
# Search for API endpoints
matches = set(re.findall(r'(/api/[a-zA-Z0-9_/]+|https?://[a-zA-Z0-9_./-]+/api/[a-zA-Z0-9_/]+)', r.text))
print('API endpoints found:', matches)

# Also check common JMP endpoints
test_endpoints = [
    'https://washdata.org/api/data/household/GTM',
    'https://washdata.org/api/v1/data?country=GTM',
    'https://washdata.org/data/household/export/csv',
    'https://washdata.org/sites/default/files/2023-07/JMP_2023_WASH_households.xlsx'
]
for ep in test_endpoints:
    res = requests.get(ep, headers=headers, timeout=10)
    print(ep, '->', res.status_code, len(res.content))
