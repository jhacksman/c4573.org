# Site Design: Homepage, Product Pages, Tech Stack, and Brand Guidelines

## Tech Stack

| Layer | Choice | Notes |
|-------|--------|-------|
| Generator | Hugo | v0.140+, extended edition for SCSS |
| Hosting | GitHub Pages | Free, auto-deploy via GitHub Actions |
| Domain | c4573.org | Custom domain, HTTPS via GitHub Pages |
| Checkout | Gumroad (embedded) | `<script>` embed or overlay, handles tax/delivery |
| Analytics | Plausible or none | Privacy-respecting, no cookies, optional |
| Fonts | System monospace stack | `"JetBrains Mono", "Fira Code", "Cascadia Code", "Consolas", monospace` |
| CSS | Custom, no framework | < 5KB total, dark theme, responsive |
| JS | Zero or minimal | No React, no build tools, no npm. Pure HTML/CSS where possible |

### Why Hugo + GitHub Pages

- **Hugo:** Builds in < 1 second. No Node.js dependency. Markdown content. Go templates. Excellent theme ecosystem but we'll use a custom minimal theme.
- **GitHub Pages:** Free hosting. Automatic deploys on push. Custom domain with HTTPS. No server to manage. Perfect for a site that's mostly static content + Gumroad buy buttons.
- **No database, no backend, no API.** Every page is a static HTML file. The only external dependency is Gumroad's checkout JS.

### GitHub Actions Deploy

```yaml
# .github/workflows/deploy.yml
name: Deploy Hugo to GitHub Pages
on:
  push:
    branches: [main]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: peaceiris/actions-hugo@v3
        with:
          hugo-version: 'latest'
          extended: true
      - run: hugo --minify
      - uses: peaceiris/actions-gh-pages@v4
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./public
```

## Homepage Design

### Structure

The homepage has four sections, stacked vertically. No sidebar, no navigation bar — just scroll.

1. **Hero** — Manifesto headline + one-line pitch + CTA
2. **Product Grid** — Cards for each tool, 2-3 columns on desktop, 1 column mobile
3. **Manifesto** — Extended "about" / why this exists
4. **Footer** — Links, contact, legal

### ASCII Wireframe

```
┌─────────────────────────────────────────────────────────────┐
│                         c4573.org                           │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐  │
│  │                                                       │  │
│  │   Don't get stuck in the caste system                 │  │
│  │   of technofeudalism.                                 │  │
│  │                                                       │  │
│  │   Here are the tools. $10 each. No subscriptions.     │  │
│  │   No API keys. No vendor lock-in.                     │  │
│  │   Download. Run. Own your data.                       │  │
│  │                                                       │  │
│  │              [ Browse Tools ↓ ]                        │  │
│  │                                                       │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                             │
│  ─── TOOLS ─────────────────────────────────────────────    │
│                                                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌────────────┐  │
│  │ 🔧 Texas        │  │ 🔧 Florida      │  │ 🔧 Federal │  │
│  │ Scraper Kit     │  │ Scraper Kit     │  │ Data Kit   │  │
│  │                 │  │                 │  │            │  │
│  │ Scrape all 254  │  │ 67 counties of  │  │ SEC, USDA, │  │
│  │ TX county       │  │ FL property     │  │ Census     │  │
│  │ assessor sites  │  │ records in one  │  │ data in    │  │
│  │ for property    │  │ script. CSV +   │  │ clean JSON │  │
│  │ data. CSV/JSON. │  │ JSON output.    │  │ format.    │  │
│  │                 │  │                 │  │            │  │
│  │ $10  [Buy Now]  │  │ $10  [Buy Now]  │  │ $10 [Buy]  │  │
│  └─────────────────┘  └─────────────────┘  └────────────┘  │
│                                                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌────────────┐  │
│  │ 🤖 MCP Data     │  │ 🧹 CSV Cleaner  │  │ 📡 API     │  │
│  │ Pipeline Kit    │  │ Toolkit         │  │ Wrapper    │  │
│  │                 │  │                 │  │ Pack       │  │
│  │ Feed structured │  │ Dedupe, norma-  │  │ Python     │  │
│  │ data to Claude, │  │ lize, validate  │  │ wrappers   │  │
│  │ Cursor, or any  │  │ messy CSVs.     │  │ for poorly │  │
│  │ MCP-compatible  │  │ Works with any  │  │ documented │  │
│  │ AI agent.       │  │ dataset.        │  │ gov APIs.  │  │
│  │                 │  │                 │  │            │  │
│  │ $10  [Buy Now]  │  │ $10  [Buy Now]  │  │ $10 [Buy]  │  │
│  └─────────────────┘  └─────────────────┘  └────────────┘  │
│                                                             │
│  ─── MANIFESTO ─────────────────────────────────────────    │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐  │
│  │                                                       │  │
│  │  The internet was supposed to be a commons.           │  │
│  │  Instead, it became a feudal estate.                  │  │
│  │                                                       │  │
│  │  Big Tech charges rent for access to data that        │  │
│  │  should be free. $500/month for property records.     │  │
│  │  $200/month for public SEC filings. $1,000/month     │  │
│  │  for census data with a nice API wrapper.             │  │
│  │                                                       │  │
│  │  We think that's absurd.                              │  │
│  │                                                       │  │
│  │  Every tool on this site costs $10. It's a Python     │  │
│  │  script you download, run on your machine, and own    │  │
│  │  forever. No API keys. No subscriptions. No           │  │
│  │  telemetry. No "free tier" that expires.              │  │
│  │                                                       │  │
│  │  We're selling shovels during the gold rush.          │  │
│  │  And we price them so everyone can dig.               │  │
│  │                                                       │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                             │
│  ─── FOOTER ────────────────────────────────────────────    │
│                                                             │
│  c4573.org · GitHub · Contact · Terms                       │
│  "c4573" = "caste" in leetspeak.                            │
│  Built with Hugo. Hosted on GitHub Pages.                   │
│  No cookies. No tracking. No JavaScript (almost).           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Mobile Layout

On screens < 768px:
- Product grid collapses to single column
- Hero text shrinks but stays readable
- Buy buttons become full-width
- Font size stays 16px minimum for readability

## Product Page Template

Each tool gets its own page at `/tools/{tool-slug}/`. Every product page follows the same template:

### Product Page Wireframe

```
┌─────────────────────────────────────────────────────┐
│  ← Back to all tools                                │
│                                                     │
│  # Texas Scraper Kit                                │
│  $10 · Python · No API keys · Works offline         │
│                                                     │
│  [ Buy on Gumroad — $10 ]                           │
│                                                     │
│  ─── What It Does ──────────────────────────────    │
│                                                     │
│  Scrapes all 254 Texas county assessor websites     │
│  and outputs structured property data:              │
│                                                     │
│  • Property address, owner name, mailing address    │
│  • Assessed value, land value, improvement value    │
│  • Tax amount, tax year, exemptions                 │
│  • Lot size, square footage, year built             │
│  • Last sale date, last sale price                  │
│                                                     │
│  Output: CSV + JSON. One file per county or         │
│  one merged statewide file.                         │
│                                                     │
│  ─── What You Get ──────────────────────────────    │
│                                                     │
│  ✓ Python script (single file, < 500 lines)         │
│  ✓ requirements.txt (requests, beautifulsoup4)      │
│  ✓ Sample output data (3 counties)                  │
│  ✓ README with setup guide (< 5 min)                │
│  ✓ Video walkthrough (10 min)                       │
│  ✓ County coverage map                              │
│                                                     │
│  ─── Requirements ──────────────────────────────    │
│                                                     │
│  • Python 3.9+                                      │
│  • pip install -r requirements.txt                  │
│  • Internet connection                              │
│  • No API keys needed                               │
│                                                     │
│  ─── Sample Output ─────────────────────────────    │
│                                                     │
│  ```json                                            │
│  {                                                  │
│    "county": "Travis",                              │
│    "address": "123 Main St, Austin, TX 78701",      │
│    "owner": "Jane Doe",                             │
│    "assessed_value": 450000,                        │
│    "tax_amount": 8325.00,                           │
│    "year_built": 1998,                              │
│    "sqft": 2100,                                    │
│    "lot_acres": 0.18,                               │
│    "last_sale_date": "2021-03-15",                  │
│    "last_sale_price": 385000                        │
│  }                                                  │
│  ```                                                │
│                                                     │
│  ─── FAQ ────────────────────────────────────────   │
│                                                     │
│  Q: Is this legal?                                  │
│  A: Yes. County assessor data is public record      │
│     by law. This tool accesses the same data        │
│     you'd see on the county website.                │
│                                                     │
│  Q: How long does a full state scrape take?         │
│  A: 2-4 hours for all 254 counties, depending       │
│     on your connection and rate limiting.            │
│                                                     │
│  Q: Do I need an API key?                           │
│  A: No. Zero external dependencies.                 │
│                                                     │
│  [ Buy on Gumroad — $10 ]                           │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### Required Fields per Product Listing

| Field | Type | Example |
|-------|------|---------|
| `title` | string | "Texas Scraper Kit" |
| `slug` | string | "texas-scraper-kit" |
| `price` | string | "$10" |
| `gumroad_url` | string | "https://c4573.gumroad.com/l/texas-scraper" |
| `one_liner` | string | "Scrape all 254 TX county assessor sites" |
| `language` | string | "Python" |
| `requirements` | list | ["Python 3.9+", "No API keys"] |
| `what_you_get` | list | ["Python script", "README", "Sample data", "Video"] |
| `features` | list | ["254 counties", "CSV + JSON output", ...] |
| `sample_output` | code block | JSON example |
| `faq` | list of Q&A | [{q: "Is this legal?", a: "Yes..."}] |

### Hugo Content Structure

```
content/
├── _index.md              # Homepage
├── tools/
│   ├── _index.md          # Tool listing page
│   ├── texas-scraper-kit.md
│   ├── florida-scraper-kit.md
│   ├── mcp-data-pipeline.md
│   └── csv-cleaner.md
├── manifesto.md           # Full manifesto page
└── about.md               # Contact, legal
```

### Hugo Front Matter (Product)

```yaml
---
title: "Texas Scraper Kit"
slug: "texas-scraper-kit"
price: "$10"
gumroad_url: "https://c4573.gumroad.com/l/texas-scraper"
one_liner: "Scrape all 254 TX county assessor sites for property data"
language: "Python"
tags: ["real-estate", "scraper", "texas", "property-data"]
requirements:
  - "Python 3.9+"
  - "No API keys needed"
  - "Works offline (after initial scrape)"
what_you_get:
  - "Python script (single file, < 500 lines)"
  - "requirements.txt"
  - "Sample output data (3 counties)"
  - "README with setup guide"
  - "Video walkthrough (10 min)"
weight: 1
featured: true
---
```

## Brand Guidelines

### Color Palette

| Color | Hex | Usage |
|-------|-----|-------|
| Background | `#0d1117` | Page background (GitHub dark) |
| Surface | `#161b22` | Card backgrounds, code blocks |
| Border | `#30363d` | Card borders, dividers |
| Text primary | `#e6edf3` | Body text |
| Text secondary | `#8b949e` | Muted text, labels |
| Accent (green) | `#3fb950` | Buy buttons, CTAs, links |
| Accent (orange) | `#d29922` | Warnings, price tags |
| Accent (blue) | `#58a6ff` | Links, hover states |

### Typography

```css
:root {
  --font-mono: "JetBrains Mono", "Fira Code", "Cascadia Code",
               "SF Mono", "Consolas", "Liberation Mono", monospace;
  --font-size-base: 16px;
  --font-size-sm: 14px;
  --font-size-lg: 20px;
  --font-size-xl: 28px;
  --font-size-hero: 40px;
  --line-height: 1.6;
}
```

All text is monospace. No serif or sans-serif fonts anywhere on the site. This reinforces the "tools for developers" identity and makes the whole site feel like a terminal.

### Design Principles

1. **No images** (almost). Product cards use text and unicode symbols, not screenshots or illustrations. The only images are the optional video walkthrough thumbnails.
2. **No JavaScript** (almost). The only JS is Gumroad's checkout embed. Everything else is pure HTML/CSS.
3. **< 50KB total page weight.** No web fonts downloaded (system monospace stack). No images. Minimal CSS. This site should load in < 0.5 seconds on any connection.
4. **Dark theme only.** No light mode toggle. The audience lives in dark mode.
5. **Mobile-first.** Single column layout that doesn't break on any screen size.

### Gumroad Integration

Two options for buy buttons:

**Option A: Gumroad Overlay (Recommended)**
```html
<script src="https://gumroad.com/js/gumroad.js"></script>
<a class="gumroad-button" href="https://c4573.gumroad.com/l/texas-scraper">
  Buy on Gumroad — $10
</a>
```
User stays on c4573.org. Gumroad opens as an overlay. Best for conversion.

**Option B: Direct Link**
```html
<a href="https://c4573.gumroad.com/l/texas-scraper" target="_blank">
  Buy on Gumroad — $10
</a>
```
User leaves c4573.org. Simpler, no JS dependency. Worse for conversion.

Recommendation: Start with Option A. Fall back to Option B if Gumroad's JS causes performance issues.
