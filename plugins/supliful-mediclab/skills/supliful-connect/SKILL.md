---
name: supliful-connect
description: This skill should be used when the user asks to connect Supliful, set up the Supliful API key, create the Supliful API connection, or register the Supliful webhook, especially "use the browser to connect Supliful". It drives the user's own signed-in Chrome (Claude in Chrome) through the Supliful app, with the key going straight into the private settings file.
---

# Connect Supliful through the browser

Use the Claude in Chrome tools (`mcp__claude-in-chrome__*`, loaded via ToolSearch in one call:
`tabs_context_mcp, tabs_create_mcp, navigate, computer, read_page, find, form_input`) in the user's own
Chrome, where they are already signed in to Supliful. If those tools are missing or the extension does not
respond, say so and give the manual steps at the end instead. Never ask for the Supliful password, and never
type a password.

## Before starting

1. Call `supliful_setup` to create the settings file and note its path.
2. Call `supliful_doctor`. If the key already passes, stop: Supliful is connected.

## Steps

1. `tabs_context_mcp`, then open a new tab at `https://supliful.com/stores`. If it shows a login page, ask the
   user to sign in in that tab and say when done. Do not fill in credentials.
2. Find the **"Supliful API"** card ("Push orders for fulfillment via Supliful Public API").
   - Disabled with "A Pro membership is required": stop and tell the user the plan needs upgrading
     (Pro or Enterprise) in Supliful. Do not start a purchase.
   - A connection already listed as "Connected": skip to step 4 and create a **new key** under
     Manage > API keys (name it "Cowork"), rather than rotating an existing key (rotation breaks
     whatever uses it).
3. Click the card, name the connection **"Mediclab Shopify bridge"**, click **Create connection**.
4. **The key is shown once. Do not read it, copy it into the chat, or take a screenshot that includes it.**
   Ask the user to click Supliful's copy button, then paste the key after `SUPLIFUL_API_KEY=` in the settings
   file from `supliful_setup` and save. Wait for the user to confirm, then close the dialog.
5. Call `supliful_doctor`. It should report the connection by name. If it says `invalid-api-key`, the paste
   picked up extra characters or the wrong key. Ask the user to re-copy it.
6. Products: in **My Products**, for each product to sell, click **Publish** and then **Publish** on the
   "Mediclab Shopify bridge" row. Ask the user before publishing, and which products. Publishing needs a saved
   label, a payment method, a verified email and an active membership; if Supliful shows an "Almost ready to
   publish" checklist, read it out and stop on that product.
7. Webhooks (only if the user hosts the always-on bridge): Manage > **Webhooks** > Add endpoint
   `https://<their host>/webhooks/supliful`. The signing secret goes in `SUPLIFUL_WEBHOOK_SECRETS`, pasted by
   the user the same way. Then `supliful_send_test_webhook` with `order.created`.
8. Finish with `supliful_doctor` and `supliful_list_products`, then hand over to the `supliful-shopify` skill
   (dry-run sync).

Close the tabs you opened. Do not click delete, revoke or rotate buttons, or anything that opens a
confirmation dialog, unless the user asks.

## Manual steps (no browser tools)

1. supliful.com/stores > "Supliful API" card > name it > Create connection.
2. Copy the key (shown once) into the settings file after `SUPLIFUL_API_KEY=`.
3. My Products > Publish > Publish on the API connection row, for each product.
4. Ask Claude: "is Supliful connected?"
