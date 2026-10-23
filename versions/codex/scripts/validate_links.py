from __future__ import annotations

import json
import ssl
import urllib.error
import urllib.request
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CATALOG = json.loads((ROOT / "public" / "data" / "catalog.json").read_text(encoding="utf-8"))
REPORT = ROOT / "verification" / "link_check.json"


def check(url: str) -> dict:
    headers = {
        "User-Agent": "AguaAbiertaGuatemala-LinkCheck/0.1 (+local research validation)",
        "Accept": "text/html,application/json,application/pdf,*/*;q=0.5",
    }
    context = ssl.create_default_context()
    for method in ("HEAD", "GET"):
        request = urllib.request.Request(url, headers=headers, method=method)
        if method == "GET":
            request.add_header("Range", "bytes=0-1023")
        try:
            with urllib.request.urlopen(request, timeout=20, context=context) as response:
                return {
                    "status": response.status,
                    "finalUrl": response.geturl(),
                    "method": method,
                    "reachable": 200 <= response.status < 400,
                    "note": "",
                }
        except urllib.error.HTTPError as error:
            if method == "HEAD" and error.code in (400, 403, 405, 429, 500, 501):
                continue
            return {
                "status": error.code,
                "finalUrl": error.geturl(),
                "method": method,
                "reachable": error.code in (401, 403, 429),
                "note": "Servidor accesible con restricción de acceso" if error.code in (401, 403, 429) else str(error.reason),
            }
        except Exception as error:  # network and TLS failures are reportable data
            if method == "HEAD":
                continue
            return {"status": None, "finalUrl": url, "method": method, "reachable": False, "note": str(error)}
    return {"status": None, "finalUrl": url, "method": "GET", "reachable": False, "note": "Sin respuesta"}


def main() -> None:
    ids_by_url: dict[str, list[str]] = defaultdict(list)
    for item in CATALOG:
        if item.get("sourceUrl"):
            ids_by_url[item["sourceUrl"]].append(item["id"])
    results = []
    for url, ids in ids_by_url.items():
        result = check(url)
        result.update({"url": url, "resourceIds": ids})
        results.append(result)
        print(f'{result["status"] or "ERR"}\t{url}')
    payload = {
        "checkedAt": datetime.now(timezone.utc).isoformat(),
        "uniqueUrls": len(results),
        "reachable": sum(1 for item in results if item["reachable"]),
        "unreachable": sum(1 for item in results if not item["reachable"]),
        "results": results,
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({key: payload[key] for key in ("uniqueUrls", "reachable", "unreachable")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
