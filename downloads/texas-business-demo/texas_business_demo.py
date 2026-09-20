#!/usr/bin/env python3
"""Free Texas business lookup demo. Python 3.11+, standard library only.
Copyright 2026 c4573.org. Licensed under MIT; see LICENSE.txt.
This standalone example is separate from the paid Texas Scraper Kit.
"""
import argparse
import csv
from datetime import datetime, timezone
import io
import json
from pathlib import Path
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

API = "https://comptroller.texas.gov/data-search/franchise-tax"
FIELDS = ("entity_name", "taxpayer_number", "mailing_zip")


def lookup(name, limit):
    url = API + "?" + urlencode({"name": name})
    request = Request(url, headers={"Accept": "application/json", "User-Agent": "c4573-business-demo/1.0"})
    try:
        with urlopen(request, timeout=30) as response:
            data = json.load(response)
    except HTTPError as exc:
        if exc.code == 413:
            raise ValueError("Search too broad. Use a more specific business name.") from exc
        raise ValueError(f"Source returned HTTP {exc.code}; try the official search page.") from exc
    except (URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise ValueError(f"Could not read the government source: {exc}") from exc
    if not isinstance(data, dict) or data.get("success") is not True:
        raise ValueError("The source did not report a successful search.")
    rows = data.get("data")
    if rows is None:
        rows = []
    if isinstance(rows, dict):
        rows = [rows]
    if not isinstance(rows, list):
        raise ValueError("Source response format changed; no exports written.")
    for item in rows:
        if not isinstance(item, dict) or not item.get("name") or not item.get("taxpayerId"):
            raise ValueError("Source response is missing required business fields.")
    records = [{"entity_name": str(r["name"]), "taxpayer_number": str(r["taxpayerId"]),
                "mailing_zip": str(r.get("mailingAddressZip") or "")} for r in rows[:limit]]
    return {"retrieved_at_utc": datetime.now(timezone.utc).isoformat(), "source_url": url,
            "query": name, "returned_by_source": len(rows), "exported": len(records),
            "limit": limit, "records": records}


def csv_text(records):
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=FIELDS)
    writer.writeheader()
    for row in records:
        # Prevent names from being interpreted as spreadsheet formulas.
        writer.writerow({k: "'" + v if v.lstrip().startswith(("=", "+", "-", "@")) else v
                         for k, v in row.items()})
    return stream.getvalue()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--name", default="Space Exploration")
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--output", type=Path, default=Path("texas-business-output"))
    args = parser.parse_args()
    if not args.name.strip() or not 1 <= args.limit <= 25:
        parser.error("Provide a nonempty name and a limit between 1 and 25.")
    try:
        result = lookup(args.name.strip(), args.limit)
        args.output.mkdir(parents=True, exist_ok=True)
        (args.output / "businesses.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        (args.output / "businesses.csv").write_text(csv_text(result["records"]), encoding="utf-8")
    except (ValueError, OSError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    print("Texas business lookup | c4573.org")
    print("Retrieved (UTC):", result["retrieved_at_utc"])
    print("Source: Texas Comptroller public search")
    print("Query:", result["query"])
    print(f"Returned: {result['returned_by_source']} | Exported: {result['exported']}")
    print()
    print(csv_text(result["records"]).strip())
    print()
    print("Saved: businesses.csv + businesses.json")
    print("Search snapshot only; not a certificate or complete filing record.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
