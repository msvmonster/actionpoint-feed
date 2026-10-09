# Action Point product feed – automatic sync

**Live feed:** https://msvmonster.github.io/actionpoint-feed/actionpoint-google-feed.xml
(spreadsheet copy: `actionpoint-products.tsv` at the same address). Rebuilt every hour.

## Status (9 Oct 2026)
Switched over. Meta catalogue "Flexify Product Catalog" → data source "New data feed for Flexify Product Catalog"
now fetches the live feed above hourly (same data source, so ad history, product sets and IDs are unchanged).
First upload: 10.1K updated/added, 0 failed, 0 issues. Sold-out variants (~1.1K) dropped, as intended.
Left to do: unlink "Supplementary feed from Flexify" from that data source, then uninstall Flexify.

## Replacing Flexify without breaking ads
1. Check which ID format the current Meta catalogue uses (Commerce Manager → Catalogue → Items → open any item → Content ID).
   - A long number like `41234567890123` → keep `FEED_ID_FORMAT: variant` (the default).
   - `shopify_SG_…_…` → set `FEED_ID_FORMAT: shopify` in `.github/workflows/feed.yml` and run the workflow once.
2. Commerce Manager → the **same** catalogue → Data sources → Add items → Data feed → Scheduled feed → paste the live feed URL → Hourly → SGD.
   (Simplest: edit the existing Flexify data source's Replace schedule and swap in the new URL. That is what we did.)
3. When the new source shows its items, unlink the Flexify supplementary feed (data source → Settings →
   Supplementary feed → Edit). This feed already sends what it added: clean card-name titles and the
   language / printing variant attributes.
4. Then uninstall Flexify in Shopify (Apps → Flexify → Uninstall). Billing stops when the app is removed.

Rebuilds the full catalogue feed every 3 hours and publishes it at a fixed web address.
Meta (and Google) fetch that address on a schedule, so the catalogue stays in sync with no Shopify app.

## One-time setup (about 10 minutes)
1. Create a free GitHub account and a new **public** repository, e.g. `actionpoint-feed`.
2. Upload everything in this folder (including the hidden `.github` folder).
3. Repository **Settings → Pages → Build and deployment → Source: GitHub Actions**.
4. **Actions** tab → *Product feed* → **Run workflow** once. After a minute the feed is live at
   `https://<your-username>.github.io/actionpoint-feed/actionpoint-google-feed.xml`

## Connect Meta
Commerce Manager → your catalogue → **Data sources → Add items → Data feed → Scheduled feed**
→ paste the URL above → schedule **Hourly** (or Daily) → currency SGD.
Meta then adds new cards, updates prices, and removes cards that sell out
(the feed only lists in-stock variants, so anything missing is treated as gone).

## Connect Google Merchant Center (optional)
Products → Feeds → Add primary feed → **Scheduled fetch** → same URL.

## Notes
- The catalogue data is already public on the storefront; nothing private is published.
- If a build ever produces fewer than 1,000 items the workflow refuses to publish, so a bad run cannot wipe the catalogue.
- Settings live at the top of `build_feed.py` (store URL, currency, how Near Mint is labelled).
- `FEED_TITLE_STYLE`: `product` (default, card name only, like the ads always showed) or `variant`
  (adds " – Near Mint / English / Normal"; better if the same feed is ever used for Google Merchant Center).
