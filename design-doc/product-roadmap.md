# Product Roadmap: Texas Scraper Kit → Full Product Line

## Product #1: Texas Scraper Kit ($10)

### What It Is

A single Python script that scrapes all 254 Texas county assessor/appraisal district websites and outputs structured property data in CSV and JSON formats.

### Technical Spec

| Attribute | Detail |
|-----------|--------|
| Language | Python 3.9+ |
| Dependencies | requests, beautifulsoup4, lxml, csv (stdlib), json (stdlib) |
| Lines of code | < 500 (main script) + per-county adapters |
| Output formats | CSV, JSON, or both |
| Execution time | 2-4 hours (full state, rate-limited) |
| Rate limiting | 1 request/second per county site (configurable) |
| Retry logic | 3 retries with exponential backoff |
| Logging | Structured logs to stdout, optional file output |
| Error handling | Graceful skip on county failures, summary report at end |

### Architecture

```
texas_scraper/
├── scraper.py           # Main entry point — CLI interface
├── counties/
│   ├── __init__.py      # County registry (254 entries)
│   ├── travis.py        # Per-county scraping adapter
│   ├── harris.py
│   ├── dallas.py
│   └── ...              # One file per county (or grouped by platform)
├── models.py            # Property data model (dataclass)
├── output.py            # CSV/JSON writers
├── config.py            # Rate limits, retry settings, output dir
├── requirements.txt     # requests, beautifulsoup4, lxml
├── README.md            # Setup guide (< 5 min)
├── sample_output/
│   ├── travis_sample.csv
│   ├── travis_sample.json
│   └── harris_sample.csv
└── video/
    └── walkthrough.mp4   # 10-minute demo (or link to YouTube)
```

### Data Schema

```python
@dataclass
class Property:
    county: str
    address: str
    city: str
    state: str = "TX"
    zip_code: str = ""
    owner_name: str = ""
    owner_mailing_address: str = ""
    assessed_value: float = 0.0
    land_value: float = 0.0
    improvement_value: float = 0.0
    tax_amount: float = 0.0
    tax_year: int = 0
    exemptions: str = ""
    year_built: int = 0
    sqft: int = 0
    lot_size_acres: float = 0.0
    bedrooms: int = 0
    bathrooms: float = 0.0
    property_type: str = ""    # residential, commercial, land, etc.
    last_sale_date: str = ""
    last_sale_price: float = 0.0
    legal_description: str = ""
    parcel_id: str = ""
    scraped_at: str = ""       # ISO 8601 timestamp
```

### County Coverage Strategy

Texas counties fall into ~5 categories by assessor website platform:

| Platform | Counties | Approach |
|----------|----------|----------|
| True Automation (TAD) | ~100+ | Single adapter, parameterized by county |
| Tyler Technologies (iasWorld) | ~50+ | Single adapter, different URL patterns |
| Harris County (custom) | 1 | Dedicated adapter |
| Custom government portals | ~50 | Individual adapters |
| No web presence | ~30-40 | Skip, document in README |

The ~30-40 smallest rural counties may not have web-accessible assessor data. These are documented as "not available" in the README, with instructions for requesting data via FOIA/public records request.

### Pricing Justification

**Why $10 works:**
- RE investors pay $50-$500/month for this data from BatchData, PropStream, ATTOM
- $10 is an impulse purchase that undercuts monthly subscriptions by 50-500x
- The tool runs locally — no ongoing costs, no usage limits, no vendor dependency
- At $10, buyers don't expect 24/7 support — README + video is sufficient

**Why not $29:**
- $10 fits the c4573.org brand ("every tool costs $10")
- The consistent pricing simplifies marketing and builds brand identity
- Lower price = higher volume = more email addresses for cross-selling
- $10 with 100 buyers/month = $1,000/mo (after Gumroad's 10%) — viable starting point

## Future Products Roadmap

### Phase 1: State Scrapers (Month 1-3)

| Product | Price | Target Launch | Notes |
|---------|-------|--------------|-------|
| Texas Scraper Kit | $10 | Month 1 | 254 counties, priority launch |
| Florida Scraper Kit | $10 | Month 2 | 67 counties, large investor market |
| California Scraper Kit | $10 | Month 2 | 58 counties, highest home values |
| Ohio Scraper Kit | $10 | Month 3 | Active wholesaling market |
| Georgia Scraper Kit | $10 | Month 3 | Atlanta metro growth |

**Cross-sell:** Email previous buyers when new states launch. Gumroad provides buyer email addresses automatically.

### Phase 2: Bundles + Federal (Month 3-6)

| Product | Price | Contents |
|---------|-------|----------|
| 5-State Bundle (TX+FL+CA+OH+GA) | $30 | All 5 state scrapers + unified schema |
| 10-State Bundle | $50 | 10 states + unified schema + merge tool |
| Federal Data Kit | $10 | SEC EDGAR, USDA, Census, BLS scrapers |
| All-States Pass | $99 | All current + future state scrapers, 1yr updates |

The bundle pricing breaks the "$10 always" rule but in a way that rewards bulk buyers. Individual tools remain $10 each.

### Phase 3: AI Agent Tools (Month 4-8)

| Product | Price | Description |
|---------|-------|------------|
| MCP Data Pipeline Kit | $10 | Feed property/SEC/census data to Claude, Cursor, or any MCP-compatible agent |
| LangChain Data Tool Pack | $10 | Pre-built LangChain tools for 5 common data sources |
| CrewAI Agent Templates | $10 | 3 pre-built CrewAI agents (RE analyst, SEC filing reader, news monitor) |
| RAG Data Prep Kit | $10 | Clean, chunk, and embed documents for RAG pipelines |

### Phase 4: Utilities (Month 6-12)

| Product | Price | Description |
|---------|-------|------------|
| CSV Cleaner Toolkit | $10 | Dedupe, normalize, validate messy CSVs |
| API Wrapper Pack | $10 | Python wrappers for poorly-documented government APIs |
| Webhook Monitor | $10 | Self-hosted webhook receiver + logger |
| Cron Job Dashboard | $10 | Lightweight web UI for managing scheduled scripts |
| Log Parser Kit | $10 | Parse, search, and analyze log files without ELK |

### Revenue Projections

| Month | Products | Units/Month | Revenue | After Gumroad (10%) |
|-------|----------|------------|---------|---------------------|
| 1 | 1 (TX) | 30 | $300 | $260 |
| 2 | 3 (TX+FL+CA) | 80 | $800 | $690 |
| 3 | 5 states + bundle | 150 | $1,700 | $1,470 |
| 6 | 10 states + bundles + AI tools | 400 | $5,200 | $4,480 |
| 12 | Full catalog (20+ products) | 800 | $10,500 | $9,050 |

These projections assume:
- 30-50% of sales come from organic search (SEO blog posts)
- 20-30% from Reddit/BiggerPockets referrals
- 10-20% from cross-selling to existing buyers
- 10% from Product Hunt / Hacker News spikes

### Product Quality Standards

Every product shipped on c4573.org must meet:

| Standard | Requirement |
|----------|-------------|
| Documentation | README with < 5 minute setup guide |
| Sample output | At least one example of real output data |
| Error handling | Graceful failures with clear error messages |
| Rate limiting | Built-in, configurable, never hammers target sites |
| Dependencies | Listed in requirements.txt, no version conflicts |
| Testing | At minimum, a quick "smoke test" script that verifies connectivity |
| Video | 5-10 minute walkthrough (optional for utilities, required for scrapers) |
| Licensing | MIT license for the code. Buyer owns it, can modify it, can resell it. |

### Maintenance Model

Each product requires ongoing maintenance:

| Task | Frequency | Time |
|------|-----------|------|
| Monitor county site changes | Weekly | 1 hour |
| Fix broken county adapters | Monthly | 2-4 hours |
| Update dependencies | Quarterly | 30 min |
| Respond to buyer questions | As needed | 15 min/ticket |
| Add new features/counties | Monthly | 2-4 hours |

At scale (20+ products), maintenance becomes the primary time cost. Budget 10-15 hours/week for maintenance across the full catalog.

### Success Metrics

| Metric | Month 3 Target | Month 6 Target | Month 12 Target |
|--------|---------------|----------------|-----------------|
| Monthly revenue | $1,000 | $4,000 | $9,000 |
| Total products | 5 | 12 | 20+ |
| Email list size | 200 | 800 | 2,000 |
| Blog posts | 3 | 8 | 15 |
| Support tickets/mo | 10-20 | 30-50 | 50-80 |
| Repeat buyer rate | 10% | 20% | 25% |
