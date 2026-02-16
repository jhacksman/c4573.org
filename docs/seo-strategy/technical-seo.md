# Technical SEO: Site Speed, Mobile, Schema Markup, Meta Tags

## Current State Assessment

c4573.org is a static HTML/CSS site hosted on GitHub Pages. This gives us inherent advantages:

- **No JavaScript framework overhead** — pages load in <500ms
- **No server-side rendering delays** — pure static files
- **CDN-backed** — GitHub Pages uses Fastly CDN globally
- **HTTPS by default** — GitHub Pages enforces SSL

The site is already faster than 95% of competitors. The focus should be on optimizing meta tags, structured data, and ensuring crawlability.

---

## Meta Tags (Per-Page)

### Homepage (index.html)

```html
<title>c4573.org — $10 Developer Tools | Data Scrapers & Automation Kits</title>
<meta name="description" content="Developer tools for $10. Data scrapers, automation kits, API wrappers. No subscriptions, no API keys, no vendor lock-in. Download, run, own your data.">
<meta name="keywords" content="developer tools, data scraper, python scraper, property data, cheap data tools, no subscription">

<!-- Open Graph -->
<meta property="og:title" content="c4573.org — $10 Developer Tools">
<meta property="og:description" content="Data scrapers, automation kits, API wrappers. $10 one-time. No subscriptions.">
<meta property="og:type" content="website">
<meta property="og:url" content="https://c4573.org/">
<meta property="og:image" content="https://c4573.org/img/og-homepage.png">
<meta property="og:site_name" content="c4573.org">

<!-- Twitter Card -->
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="c4573.org — $10 Developer Tools">
<meta name="twitter:description" content="Data scrapers & automation kits. $10 one-time. No subscriptions.">
<meta name="twitter:image" content="https://c4573.org/img/og-homepage.png">
```

### Product Page (products/texas-scraper-kit.html)

```html
<title>Texas Scraper Kit — 764 Data Sources, $10 | c4573.org</title>
<meta name="description" content="Scrape property data from 764 Texas data sources across 254 counties. Python CLI + Docker + REST API. CSV, JSON, or PostgreSQL output. $10 one-time.">

<!-- Open Graph -->
<meta property="og:title" content="Texas Scraper Kit — 764 TX Data Sources for $10">
<meta property="og:description" content="Property data from 764 Texas sources. Python + Docker + REST API. One-time $10 purchase.">
<meta property="og:type" content="product">
<meta property="og:url" content="https://c4573.org/products/texas-scraper-kit.html">
<meta property="og:image" content="https://c4573.org/img/og-texas-scraper.png">

<!-- Product price for rich results -->
<meta property="product:price:amount" content="10.00">
<meta property="product:price:currency" content="USD">
```

### About Page (about.html)

```html
<title>About c4573.org — Why We Sell $10 Developer Tools</title>
<meta name="description" content="c4573 is leetspeak for 'caste.' We sell $10 developer tools to fight technofeudalism. No subscriptions, no API keys, no vendor lock-in.">

<!-- Open Graph -->
<meta property="og:title" content="About c4573.org — Anti-Technofeudalism Developer Tools">
<meta property="og:description" content="Why we sell $10 developer tools. The anti-SaaS manifesto.">
<meta property="og:type" content="website">
<meta property="og:url" content="https://c4573.org/about.html">
```

---

## Structured Data (JSON-LD)

### Homepage — Organization Schema

```json
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "c4573.org",
  "url": "https://c4573.org",
  "description": "$10 developer tools. Data scrapers, automation kits, API wrappers.",
  "sameAs": [
    "https://github.com/jhacksman/c4573.org",
    "https://c4573.gumroad.com"
  ]
}
```

### Product Page — Product Schema

Already implemented. Verify it includes:

```json
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "Texas Scraper Kit",
  "description": "Scrape property data from 764 Texas data sources across all 254 counties.",
  "offers": {
    "@type": "Offer",
    "price": "10.00",
    "priceCurrency": "USD",
    "availability": "https://schema.org/InStock",
    "url": "https://c4573.gumroad.com/l/texas-scraper"
  },
  "brand": {
    "@type": "Brand",
    "name": "c4573.org"
  }
}
```

### Blog Posts — Article Schema (for future blog)

```json
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "Stop Paying $500/Month for Texas Property Data",
  "author": {
    "@type": "Organization",
    "name": "c4573.org"
  },
  "datePublished": "2026-02-15",
  "dateModified": "2026-02-15",
  "publisher": {
    "@type": "Organization",
    "name": "c4573.org"
  }
}
```

### FAQ Schema (Product Page)

The product page has 8 FAQ items. Wrap them in FAQ schema for rich results:

```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "Is this legal?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Yes. County assessor data is public record under Texas law."
      }
    },
    {
      "@type": "Question",
      "name": "Why 764 sources for 254 counties?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Many counties have multiple data portals — a central appraisal district, a tax office, and sometimes a separate GIS portal."
      }
    }
  ]
}
```

---

## Site Speed Optimization

### Current Advantages (Static Site)

| Metric | Expected Value | Target |
|--------|---------------|--------|
| First Contentful Paint (FCP) | <0.5s | <1.0s |
| Largest Contentful Paint (LCP) | <0.8s | <2.5s |
| Cumulative Layout Shift (CLS) | 0 | <0.1 |
| Time to Interactive (TTI) | <0.5s | <3.0s |
| Total Blocking Time (TBT) | 0 | <200ms |

### Optimization Checklist

- [x] No JavaScript frameworks (zero JS bundle)
- [x] Single CSS file (no render-blocking imports)
- [x] No external font downloads (system font stack with fallbacks)
- [ ] **Add:** `<link rel="preconnect" href="https://fonts.googleapis.com">` if using Google Fonts
- [ ] **Add:** Image optimization (WebP format, lazy loading for below-fold images)
- [ ] **Add:** `<link rel="canonical" href="https://c4573.org/">` on every page
- [ ] **Add:** `<meta name="robots" content="index, follow">` on all pages
- [ ] **Add:** XML sitemap at `/sitemap.xml`
- [ ] **Add:** `robots.txt` at root

### robots.txt

```
User-agent: *
Allow: /
Sitemap: https://c4573.org/sitemap.xml
```

### sitemap.xml

```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://c4573.org/</loc>
    <lastmod>2026-02-15</lastmod>
    <changefreq>weekly</changefreq>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>https://c4573.org/products/texas-scraper-kit.html</loc>
    <lastmod>2026-02-15</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.9</priority>
  </url>
  <url>
    <loc>https://c4573.org/about.html</loc>
    <lastmod>2026-02-15</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.7</priority>
  </url>
</urlset>
```

---

## Mobile Optimization

### Current State

- [x] Responsive CSS with breakpoints at 768px and 480px
- [x] `<meta name="viewport" content="width=device-width, initial-scale=1.0">`
- [x] Monospace font stack with system fallbacks
- [x] Touch-friendly button sizes (min 44x44px)
- [x] No horizontal scrolling

### Additional Recommendations

- [ ] Test with Google Mobile-Friendly Test after deployment
- [ ] Test with PageSpeed Insights for mobile score
- [ ] Ensure CLI mockup code blocks don't overflow on mobile (add `overflow-x: auto`)
- [ ] Consider `font-size: 12px` minimum for mobile readability on code blocks

---

## Crawlability & Indexing

### Priority Actions

1. **Submit sitemap to Google Search Console** — after GitHub Pages deployment
2. **Submit sitemap to Bing Webmaster Tools** — secondary but free
3. **Request indexing** — use Google Search Console's URL Inspection tool for each page
4. **Internal linking** — every page links to every other page via nav and footer
5. **Canonical URLs** — add `<link rel="canonical">` to prevent duplicate content issues

### URL Structure

Current structure is clean and SEO-friendly:

```
https://c4573.org/                          (homepage)
https://c4573.org/products/texas-scraper-kit.html  (product page)
https://c4573.org/about.html                (about page)
https://c4573.org/blog/                     (future blog index)
https://c4573.org/blog/stop-paying-500-month.html  (future blog post)
```

### GitHub Pages Considerations

- GitHub Pages serves `index.html` at `/` automatically
- Custom domain: configure `CNAME` file with `c4573.org`
- HTTPS: GitHub Pages enforces HTTPS with Let's Encrypt
- No server-side redirects available — use `<link rel="canonical">` instead
- 404 page: already implemented at `404.html`
