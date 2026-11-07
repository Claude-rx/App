---
name: supliful-shopify
description: This skill should be used when the user wants to connect Supliful to Shopify, push or sync Supliful products to the Mediclab store, send orders to Supliful, check a Supliful order or its tracking, cancel a Supliful order, or test the Supliful integration. Trigger phrases include "push products to Shopify", "sync Supliful", "send this order to Supliful", "where is order", "Supliful tracking", "is Supliful connected".
---

# Supliful <-> Shopify for Mediclab

Drive the Supliful integration through the `supliful_*` tools of this plugin's MCP server. Mediclab sells
private-label supplements made and shipped by Supliful on its Shopify store (mediclab.us), next to
GLP-1 and prescription products that Supliful never touches.

## What can and cannot be done

The Supliful API reads products and places orders. It **cannot** create products, design or upload
labels, or publish products. Those happen in the Supliful app (My Products; then Publish -> the
"Supliful API" row). Never claim a product or label was created in Supliful by these tools. For label
artwork, use the `supliful-labels` skill.

## Start every session

1. Call `supliful_doctor`. Relay each FAIL in plain language.
2. If a key or token is missing, call `supliful_setup` and tell the user to open the returned settings
   file and paste the values there. **Never ask for, accept, repeat or store a key in the chat.** If the user
   pastes one anyway, say it should be rotated in Supliful (Stores -> connection -> Manage -> API keys).
3. Re-run `supliful_doctor` after the user says they saved the file (no restart needed).

## Push products to Shopify

1. `supliful_sync_products` with no arguments: a dry run. Show the table and explain each action:
   - `link`: the Shopify product already exists with the same SKU. It gets tied to Supliful; its copy, images and price stay as they are.
   - `create`: new product, created as a **draft** for review (or active with `publish: true`).
   - `update`: changed in Supliful. Only the link refreshes, unless `update_content: true`.
   - `hide`: discontinued or unavailable in Supliful. The product goes to draft; it is never deleted.
   - `conflict`: several Shopify products share the SKU, so a person chooses which one.
   - `skip`: not sellable and not in Shopify.
2. Ask the user to confirm, including whether new products should go live and any price overrides
   (`prices: {"SKU": 39}`). Only then call it again with `apply: true`.
3. Report the result and mention that drafts need publishing in Shopify admin when they are ready.

## Send an order

1. Get one Shopify order id from the user. Do not browse or list customer orders.
2. `supliful_push_order` with `dry_run: true`; show the lines that will go to Supliful and the ones that
   stay in Shopify.
3. Point out the mode reported by doctor: **sandbox** orders are never charged or shipped. In **live**
   mode the merchant is charged immediately. Never suggest switching to live mode without an explicit
   request; live mode is set by the user in the settings file (`SUPLIFUL_LIVE_ORDERS=1`).
4. On confirmation, call it again without `dry_run`. Repeating it is safe: the same Shopify order never creates
   a second Supliful order.

## Status, tracking, cancellation

- Order status: `supliful_get_order` with the Supliful id or `shopify-<shopify order id>`. Explain `local`
  (submitted, accepted, partially_shipped, shipped, on_hold, completed, canceled, returned) and any `onHoldReasons`.
- Tracking to Shopify: `supliful_sync_shipments`, or `supliful_reconcile` for every open order. The customer
  gets Shopify's shipping email.
- Cancel: only while the order is NEW (about two hours after creation). Confirm with the user first, then
  `supliful_cancel_order`. A 409 `order-not-cancelable` means it is already moving: say so and suggest
  contacting Supliful.

## Prove the setup

- `supliful_rehearse` walks a sandbox order through accept, ship and complete.
- `supliful_send_test_webhook` checks the always-on webhook receiver, if the user hosts one (see
  `references/bridge-server.md`).

## Errors

Branch on the Supliful error code in the tool output: `invalid-api-key` (fix the settings file),
`subscription-required` (needs a Pro or Enterprise plan; reads still work), `validation-failed` 422 on
`lines.productId` (the product is not published to the connection or is discontinued), on `shippingAddress`
(show the address issues), `rate-limit-exceeded` (wait), `internal-error` (Supliful's side; pass on
the `instance` and the time to help@supliful.com). Details are in the `supliful-api` skill.
