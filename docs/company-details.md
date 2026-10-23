# Company details

Every page of the store names the company behind SKINOFAB from one place, `tools/persona/company.py`:

| | |
|---|---|
| Company | **Synderra Inc**, a Colorado domestic profit corporation, in good standing |
| Company number | 20258305259 (Colorado Secretary of State) |
| Registered agent | Global Accounting service inc, 2525 Arapahoe Ave Ste E4 Unit 1280, Boulder, CO 80302, US |
| Address shown on the store | 2525 Arapahoe Ave, Ste E4 Unit 1280, Boulder, CO 80302, United States (the registered agent's; the record gives no other) |
| Email | hello@skinofab.com |
| Brand | SKINOFAB ("SKINOFAB is a brand of Synderra Inc") |

## What the theme build changes (automatic)

`apply_persona.py` runs `company.rewrite()` on every page and data file, then fails the build if any old detail is
left (the old store's "Skinofab LLC" and West Hollywood mailbox, `hey@`/`info@`/`contact@skinofab.com`, and the
placeholder German notices):

- the footer on every page, the contact and contact-information pages, the FAQ;
- the privacy policy (owner and data controller), the terms (provider, withdrawal form; the courts are those where
  the owner is based, now Boulder, Colorado), the cookie policy, the refund and shipping policies;
- the collaboration agreement: Colorado law, courts in Boulder County, Colorado (was Delaware);
- both Impressum pages: they carried a placeholder notice ("John M. Schneider", "+49 (0)30 12345678",
  "HRB 123456 B", "Anna Becker, Musterstraße 12") and another company's notice (Xevio GmbH, Cologne). They now carry
  Synderra Inc's details under § 5 DDG. **Add the name of the person authorised to represent the company**
  (`company.OFFICER`): German law asks for it and the record does not give it;
- product data (`"vendor": "SKINOFAB"`).

## What you set in the NEXT dashboard (the Admin API cannot)

The hosted checkout reads these from the store settings. Today its Terms & Conditions still say "This website is
operated by demo.29next.store", and the store's company name and address are empty.

1. **Settings → Policies.** Paste each file from `docs/checkout-policies/` into its policy (the build regenerates
   them from the store's own pages):
   - Terms & Conditions: `terms.html`
   - Privacy Policy: `privacy.html`
   - Subscription Terms: `subscription-terms.html` (the Automatic Refills terms)
   - Refund and Shipping policies, if the dashboard has them: `refund.html`, `shipping.html`
2. **Store details** (General settings): company / legal name `Synderra Inc`; address `2525 Arapahoe Ave`,
   `Ste E4 Unit 1280`, `Boulder`, `CO`, `80302`, United States.
3. **Support email** (Support & Notifications): `hello@skinofab.com`, and the sender of order emails if it still
   says `hey@`.

Then reload a checkout: the footer links should open SKINOFAB's terms and privacy policy, naming Synderra Inc.
