import json
import re
import os

def check_subagent(cid, label):
    log_path = f"C:/Users/hugof/.gemini/antigravity/brain/{cid}/.system_generated/logs/transcript_full.jsonl"
    if not os.path.exists(log_path):
        print(f"Log not found for {label}: {log_path}")
        return
    lines = open(log_path, encoding='utf-8').readlines()
    print(f"\n==================== {label} ({cid}) - {len(lines)} steps ====================")
    
    # Check if there is an end message / final report
    final_report = None
    for l in reversed(lines):
        j = json.loads(l)
        content = j.get('content', '')
        if isinstance(content, str) and ('# ' in content or '## ' in content or len(content) > 1500):
            final_report = content
            break
            
    if final_report:
        print("--- Final Report / Major Finding Found ---")
        print(final_report[:2500])
        print("...\n[Truncated for summary]")
    
    all_text = "".join([str(json.loads(l).get('content', '')) for l in lines])
    urls = set(re.findall(r'https?://[a-zA-Z0-9_\-\./?=&%#]+', all_text))
    
    # Filter high value urls
    hydrosheds = [u for u in urls if 'hydrosheds' in u.lower()]
    usac = [u for u in urls if 'usac' in u.lower()]
    gov = [u for u in urls if 'gob.gt' in u.lower()]
    zenodo = [u for u in urls if 'zenodo' in u.lower() or 'doi.org' in u.lower()]
    
    print(f"\nDiscovered Categories in {label}:")
    print(f"  HydroSHEDS ({len(hydrosheds)}):", hydrosheds[:5])
    print(f"  USAC Repositories ({len(usac)}):", usac[:5])
    print(f"  Guatemala Gov (.gob.gt) ({len(gov)}):", gov[:5])
    print(f"  DOIs / Zenodo ({len(zenodo)}):", zenodo[:5])

if __name__ == '__main__':
    check_subagent("8c36122e-a9b5-4b7a-8780-76fcc86ca100", "SUBAGENT 1: Guatemala Water Data")
    check_subagent("6554a02a-074b-4c4b-a115-d9e8e640c9d0", "SUBAGENT 2: Geospatial & Global Water")
