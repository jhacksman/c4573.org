# Cameron County appraisal findings

Retrieved: 2026-09-05T10:22:40-07:00 (America/Los_Angeles).

Read AGENTS.md and installed this extracted local project into `.venv` using Python 3.14.6 and `pip install --no-cache-dir -e .`. Confirmed CLI output: `texas-scrape, version 1.0.2`.

Query: owner full-text search for `SPACE EXPLORATION`, Cameron County, limit 3. This is a limited result set, not a complete holdings inventory.

```sh
.venv/bin/texas-scrape property search --county cameron --owner "SPACE EXPLORATION" --limit 3 --output results/cameron.json
```

The command reported three results; the saved JSON was inspected and contains three matching listed owners. All records are tax year 2026 and list ESPERSON ST.

| Parcel/account number | Listed owner | Tax year | Official source |
| --- | --- | --- | --- |
| 460312 | SPACE EXPLORATION TECHNOLOGIES CORP | 2026 | [County appraisal detail](https://cameron.prodigycad.com/property-detail/460312/2026) |
| 460313 | SPACE EXPLORATION TECHNOLOGIES CORP | 2026 | [County appraisal detail](https://cameron.prodigycad.com/property-detail/460313/2026) |
| 460314 | SPACE EXPLORATION TECHNOLOGIES CORP | 2026 | [County appraisal detail](https://cameron.prodigycad.com/property-detail/460314/2026) |

## First-parcel check and access limitations

Attempted to open the official detail page for account 460312. The web reader returned an internal error stating the URL was not safe to open (non-retryable). The browser attempt was then rejected by automatic browser security review because site permission had been declined. No workaround was attempted. Therefore account, owner, tax year, and legal description were not independently verified against the live detail page.

The raw export for 460312 lists this legal description:

LOT 1 BLOCK 1 SOLAR SYSTEM MAST RE-PLAT SUBDIVISION LOT 1 (2026 RE-PLAT C1-5249 CCMR FILED 11/10/2025)(2018 C1-3584 CCMR FILED 03/10/2017)

## Missing fields and interpretation

All three exports have blank city and ZIP code; null subdivision, owner mailing address, ownership percentage, land square footage, improvement square footage, year built, bedrooms, bathrooms, taxable value, last sale date, last sale price, and prior-year taxes; and an empty exemptions list. These are unpopulated export fields, not proof that the information or exemptions do not exist.

All three exports report `land_acres: 0.0`. This is not confirmed zero acreage. AGENTS.md documents a prior September 4, 2026 discrepancy for account 460312: export 0.0 versus detail-page 0.0800 acres. That historical observation was not reverified today and has not been applied as a correction to the raw JSON.

Appraisal values are not sale prices. No purchase date or price is inferred; dates embedded in legal descriptions are not treated as purchase dates. No deed search was performed, and matching owner names alone do not establish a transaction or corporate affiliation.

Raw output: [cameron.json](cameron.json). Raw records remain unchanged.
