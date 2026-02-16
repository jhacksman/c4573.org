# Analytics Setup: Google Analytics, Search Console, Tracking

## Overview

For a static site with no backend, analytics setup is minimal but critical. We need to track:
1. **Where visitors come from** (organic, referral, direct)
2. **What pages they view** (homepage, product page, about, blog)
3. **What they click** (CTA buttons, Gumroad links)
4. **What keywords bring them** (Search Console)
5. **Whether content converts** (blog → product page → Gumroad click)

---

## Google Analytics 4 (GA4) Setup

### Installation

Add the GA4 tag to every page's `<head>`:

```html
<!-- Google Analytics 4 -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-XXXXXXXXXX');
</script>
```

**Note:** Replace `G-XXXXXXXXXX` with actual Measurement ID from GA4 property.

### GA4 Property Configuration

1. Create a new GA4 property at analytics.google.com
2. Set data stream to "Web" with URL `https://c4573.org`
3. Enable Enhanced Measurement (scrolls, outbound clicks, file downloads)
4. Set time zone to your local time zone
5. Set currency to USD

### Custom Events to Track

| Event Name | Trigger | Purpose |
|-----------|---------|---------|
| `cta_click` | Click on "Buy on Gumroad" button | Conversion intent |
| `product_page_view` | Pageview on /products/*.html | Product interest |
| `faq_scroll` | Scroll to FAQ section | Objection handling |
| `about_page_view` | Pageview on /about.html | Brand interest |
| `blog_to_product` | Click from blog to product page | Content attribution |

### Event Tracking Implementation

Add `onclick` attributes to CTA buttons (minimal JS approach for a static site):

```html
<a href="https://c4573.gumroad.com/l/texas-scraper"
   class="btn btn-primary"
   onclick="gtag('event', 'cta_click', {
     'event_category': 'conversion',
     'event_label': 'texas-scraper-kit',
     'value': 10
   });">
  Buy on Gumroad — $10
</a>
```

### Key GA4 Reports to Monitor

| Report | What It Shows | Check Frequency |
|--------|-------------|----------------|
| Acquisition > Traffic acquisition | Where visitors come from | Weekly |
| Engagement > Pages and screens | Most viewed pages | Weekly |
| Engagement > Events | CTA clicks, scroll depth | Weekly |
| Acquisition > Google organic search traffic | Search keywords (limited) | Weekly |
| Retention > User retention | Repeat visitors | Monthly |

---

## Google Search Console Setup

### Installation

1. Go to search.google.com/search-console
2. Add property: `https://c4573.org`
3. Verify ownership via:
   - **DNS TXT record** (preferred for custom domain)
   - **HTML file upload** (add `google[hash].html` to repo root)
   - **HTML meta tag** (add `<meta name="google-site-verification" content="[hash]">` to homepage)

### Priority Actions After Setup

1. **Submit sitemap:** `https://c4573.org/sitemap.xml`
2. **Request indexing:** Use URL Inspection tool for each page:
   - `https://c4573.org/`
   - `https://c4573.org/products/texas-scraper-kit.html`
   - `https://c4573.org/about.html`
3. **Check mobile usability:** Ensure no mobile issues flagged
4. **Check Core Web Vitals:** Verify LCP, FID, CLS pass

### Key Search Console Reports

| Report | What It Shows | Check Frequency |
|--------|-------------|----------------|
| Performance > Search results | Queries, clicks, impressions, CTR, position | Weekly |
| Performance > Discover | If pages appear in Google Discover | Monthly |
| Indexing > Pages | Which pages are indexed | Monthly |
| Experience > Core Web Vitals | Page speed metrics | Monthly |
| Links > External links | Who links to the site | Monthly |
| Links > Internal links | Internal link structure | Quarterly |

### Search Console Insights to Act On

| Insight | Action |
|---------|--------|
| Query with high impressions but low CTR | Improve meta title/description for that keyword |
| Query ranking positions 5-15 | Create/optimize content to push into top 5 |
| Page not indexed | Check for crawl errors, resubmit |
| Mobile usability issues | Fix CSS/layout |
| New external link | Check quality; respond to linking site if appropriate |

---

## Bing Webmaster Tools

Lower priority but free and easy:

1. Go to bing.com/webmasters
2. Import from Google Search Console (one-click setup)
3. Submit sitemap
4. Bing drives ~5-10% of search traffic. Worth the 5 minutes.

---

## Gumroad Analytics

Gumroad provides built-in analytics for the product listing:

| Metric | Where to Find |
|--------|--------------|
| Views | Gumroad dashboard > Product > Analytics |
| Sales | Gumroad dashboard > Sales |
| Conversion rate | Views → Sales ratio |
| Traffic sources | Gumroad dashboard > Analytics > Referrers |
| Revenue | Gumroad dashboard > Balance |

### Gumroad + GA4 Integration

Gumroad doesn't support custom tracking pixels. To attribute sales:
- Track CTA clicks with GA4 events (outbound click to Gumroad)
- Compare GA4 CTA click count with Gumroad views
- Compare Gumroad referrer data with GA4 traffic sources

---

## KPI Dashboard

### Weekly Metrics (Track in a Spreadsheet)

| Metric | Source | Target (Month 1) | Target (Month 3) |
|--------|--------|-------------------|-------------------|
| Organic search impressions | Search Console | 500 | 5,000 |
| Organic search clicks | Search Console | 50 | 500 |
| Product page views | GA4 | 100 | 1,000 |
| CTA clicks (Buy button) | GA4 events | 20 | 200 |
| Gumroad views | Gumroad analytics | 30 | 300 |
| Gumroad sales | Gumroad analytics | 5 | 50 |
| Referring domains | Search Console | 10 | 30 |
| Average search position | Search Console | 50+ | 15-30 |

### Monthly Review Questions

1. Which blog posts drive the most product page visits?
2. Which keywords have the highest CTR?
3. Which referral sources convert best?
4. Is the product page conversion rate improving?
5. Which FAQ items get the most scroll-to views? (indicates common objections)

---

## Privacy Considerations

- **No cookies banner needed** if using GA4 with anonymized IP (default in GA4)
- **No personal data collection** — the site has no forms, accounts, or user input
- **Gumroad handles payment data** — c4573.org never touches credit card info
- **Consider:** Adding a simple privacy policy page linking to Gumroad's privacy policy
- **GDPR note:** If significant EU traffic, consider a minimal cookie consent banner for GA4

---

## Implementation Priority

| Priority | Action | Effort | Impact |
|----------|--------|--------|--------|
| 1 | Google Search Console setup + sitemap submit | 15 min | Critical |
| 2 | GA4 property creation + tag installation | 30 min | High |
| 3 | CTA click event tracking | 15 min | High |
| 4 | Bing Webmaster Tools setup | 5 min | Low |
| 5 | Weekly KPI tracking spreadsheet | 30 min | Medium |
| 6 | Monthly review process | 1 hr/month | High |
