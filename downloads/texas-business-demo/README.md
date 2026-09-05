# Free Texas business lookup demo

Python 3.11+; no pip packages, account, or API key. Unzip this download,
open a terminal in its folder, and run:

```sh
python3 texas_business_demo.py --name "Space Exploration" --limit 5
```

On Windows, use `py -3` instead of `python3`.
Results are written to `texas-business-output/businesses.csv` and
`texas-business-output/businesses.json`. Re-running replaces those files;
use `--output another-folder` to retain separate runs.

The JSON includes the retrieval timestamp, source URL, query, returned count,
and exported count. Open CSV identifier/ZIP columns as text to retain formatting.
The `sample/` folder contains a real snapshot retrieved September 5, 2026 UTC
(September 4 in Pacific time), not results generated when you open the file.

One search request goes directly to the Texas Comptroller. Use specific names;
HTTP 413 means the search was too broad. There is no automatic retry or crawling.
An empty successful result writes an empty CSV with a header; source errors exit
nonzero without writing exports. Government endpoints can change.

This example exports name, Texas taxpayer number, and mailing ZIP. It does not
return officers, account-status detail, certified records, or a complete filing
history. A name match alone does not establish an entity's identity or status.
Official lookup: https://comptroller.texas.gov/taxes/franchise/account-status/search

This standalone demo is MIT licensed. The separate paid Texas Scraper Kit has
its own source-available license and wider supported workflow:
https://c4573.org/products/texas-scraper-kit.html

SpaceX-area research: the name search can match unrelated entities. Mailing ZIP is not parcel location. Follow the tutorial for official Cameron County parcel and deed sources. No purchase or ownership finding is asserted by this demo.
