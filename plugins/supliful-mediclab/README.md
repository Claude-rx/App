# Supliful for Mediclab (Cowork plugin)

Private-label supplements from Supliful, sold on the Mediclab Shopify store.

**Ask Claude things like:**
- "Use the browser to connect Supliful" (uses Claude in Chrome in your signed-in Chrome; you paste the key yourself)
- "Is Supliful connected?"
- "Push our Supliful products to Shopify" (shows the plan first, applies only when you say so)
- "Send order 6123456789 to Supliful" / "Where is that order?" / "Cancel it"
- "Design the label for Magnesium Glycinate" / "Render all labels into my Labels folder"

## Install

- **Cowork:** upload `supliful-mediclab.plugin` (Customize > Plugins > upload), or add the marketplace `Claude-rx/App`.
- **Claude Code:**

```
/plugin install supliful-mediclab --marketplace Claude-rx/App
```

## Setup (once)

1. It needs **Node.js 20 or newer** on the computer (`node -v`).
2. Ask Claude to "set up Supliful". It creates a private settings file
   (`~/.supliful-mediclab/.env`, readable only by you) and tells you where it is.
3. Open that file and fill in the values. **Never paste keys in the chat.**
   - `SUPLIFUL_API_KEY`: Supliful > Stores > "Supliful API" card > Create connection (needs a Pro or
     Enterprise plan; the key is shown once).
   - `SHOPIFY_STORE_DOMAIN=mediclab-2.myshopify.com`, and `SHOPIFY_ADMIN_TOKEN` from Shopify admin >
     Settings > Apps > Develop apps > custom app with scopes `read_products, write_products, read_orders,
     write_orders, read_merchant_managed_fulfillment_orders, write_merchant_managed_fulfillment_orders`.
4. Ask "is Supliful connected?". Every line should say PASS.

Orders stay in **sandbox mode** (never charged, never shipped) until you add `SUPLIFUL_LIVE_ORDERS=1`
to the settings file yourself.

## What it can't do

Supliful's API cannot create products, upload labels or publish products. Do those in the Supliful app
using the label PDFs this plugin makes, then publish each product to the "Supliful API" connection.

## Labels

PDF rendering uses Playwright if it is installed (`npm i -g playwright && npx playwright install chromium`).
Without it, the plugin writes print-ready HTML files that you save as PDFs from Chrome. Label settings live in
`~/.supliful-mediclab/labels/`, so your edits survive plugin updates.

## Contents

| Part | Purpose |
|---|---|
| Skill `supliful-shopify` | Product sync, orders, tracking, troubleshooting |
| Skill `supliful-labels` | Label design workflow and pre-print checks |
| Skill `supliful-connect` | Browser-guided connection setup in your own Chrome (Claude in Chrome) |
| Skill `supliful-api` | Supliful's official API reference (MIT, from github.com/Supliful/agent-skills) |
| MCP server `supliful` | 15 local tools; no dependencies to install; talks only to Supliful and your Shopify store |

Built from the Claude-rx/App repository (`npm run plugin:build`). Source: `tools/supliful/`.
