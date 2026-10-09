# Action Point product feed – automatic sync

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
