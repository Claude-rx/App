# The Adaptive Foundation Stick

SKINOFAB's fifth product: a dual-ended foundation stick. One end is a twist-up cream foundation that goes on white and
shifts toward the wearer's skin tone as it is blended; the other end is a dense kabuki brush to buff it in. Inspired by
the owner's other brand, Facelove's "Changing Foundation Stick"
(https://facelove-cosmetics.com/products/changing-foundation-stick-main), rebuilt for SKINOFAB: the Adaptive Peptide
Foundation page's structure and look, photos of women past 45 holding and using the black SKINOFAB stick on white,
SKINOFAB's real wordmark on every stick, and nothing on the page we can't stand behind.

Preview: https://skinofab.29next.store/catalogue/adaptive-foundation-stick_235/?preview_theme=34

## Before launch (owner)

- **Name.** The page calls it the **Adaptive Foundation Stick**, so it reads as part of the SKINOFAB line next to the
  Adaptive Peptide Foundation (Facelove's name is "Changing Foundation Stick"). To change it: `TITLE` and `NAV_LABEL`
  in `tools/persona/stick_copy.py`, then rerun `setup_brush_offers.py skinofab <work> stick_copy` and the build.
- **Formula.** The page names hyaluronic acid, niacinamide, squalane, vitamin E and centella asiatica, the five
  ingredients Facelove's page names. Facelove publishes no full ingredient list: check the supplier's INCI list and
  correct `INGREDIENTS` and `TWIN['inside']` in `stick_copy.py` if it differs. The tab says "The full ingredient list
  is printed on the box".
- **Shade range.** Facelove's page says both "16 skin tones" and "fair to medium" (its own image). Our page says only
  that it is made to adapt to "a wide range of skin tones" and tells her to try it along her jaw in daylight, with the
  30-day refund (`SHADE_FAQ`). Two photos (`temple`, `friends`) show women with deep skin: if the supplier's range
  stops at medium, say so in `SHADE_FAQ` and swap those two photos.
- **Net weight** (`NET`): shown in the Ingredients tab once set.
- **Where it is made** (`KOREAN`): off. The foundation, balm and serum say "Formulated in Korea"; the stick doesn't
  until the supplier confirms it.
- **Refills.** Automatic Refills are on by default, as on the foundation: $31 every 28 days for 1 stick, $47 every
  56 days for 2, $62 every 84 days for 3 (20% under the one-time price; one-time stays a choice on the cart page). How
  long a stick lasts decides the 28 days: change `BUNDLES[*]['refill'|'every']` and `REFILL['every']` in
  `stick_copy.py`, then rerun `setup_brush_offers.py skinofab <work> stick_copy` and the build.
- **"16 skin tones".** The owner's reference shows "One stick for 16 skin tones". The page says "One stick, many skin
  tones" (12 swatches, no number) until the supplier confirms the range: then put the number in the `tones_panel`
  titles in `product_photos.py stick` and in `SHADE_FAQ`.
- **Same formula.** The reviews near the top and in the wall are the Adaptive Peptide Foundation's, labelled "Verified
  buyer of the foundation", because the owner states the stick is the same adaptive formula. If the supplier's stick
  formula differs, set `BORROW_REVIEWS = None` and `FRONTROW_NOTE = None` in `stick_copy.py` and the page shows its
  own (empty) reviews again.
- **Same formula, different ingredient lists.** The page lists hyaluronic acid, niacinamide, squalane, vitamin E and
  centella (Facelove's list); the foundation's page lists PDRN, Matrixyl 3000, Pro-Xylane, adenosine and ceramide NP.
  An independent review (26 Oct) flagged that "the same adaptive formula" and two different lists contradict each
  other. Either the stick is the foundation's formula (then `INGREDIENTS`, `TWIN['inside']` and the science rows
  take the foundation's actives) or it shares only the colour technology (then the reviews' labels say "of our
  Adaptive Peptide Foundation" without "same formula", or the stick shows only its own reviews).
- **Wear claim.** "From 10 AM to 10 PM" and "made to wear all day" are the owner's elements; a wear test (even an
  in-house one) would back them.
- **Real photos.** The photos are AI-generated; the wordmark is printed on every stick by `relabel_bottles.py` from
  the real wordmark (`docs/real-wordmark.md`). Once the real stick exists, photograph it on white and swap `pack` and
  `single` first.

## What Facelove's page does, and what we kept

| Facelove device | Here |
|---|---|
| "The stick that makes mature skin glow again" | The buy box lead: the foundation that finds your shade for you, the brush on the other end, a minute, nothing to spill; three checks under it (`BULLETS`: no shade to choose, the brush built in, creamy for dry skin); under the title's price, what it is ("2 Sticks with Automatic Refills, $23.50 a stick", kept in step with the chosen pack) |
| "5 reasons" (natural finish, automatic shade, mature skin, light wear, skincare) | Problem / root cause / solution with five fixes, "The skinofab difference", the compare table and the six tabs |
| "No orange, grey or yellow tint", "no time wasted on color choices" | The problem ("orange in daylight, grey by the window"), "No shade to guess", "0 shades to choose" |
| "Does not settle into wrinkles", "no cakey, dry or tight feeling" | Said as how to get it: thin layers, buffed in with the brush, on moisturised skin (FAQ, tabs) |
| The five ingredient cards | The ingredient carousel, the science block and the Ingredients tab, as cosmetic effects |
| 30-day money-back guarantee, free shipping | The store's 30-day guarantee (a full refund, even opened, no questions asked: the original store's own words; nothing promises she keeps it, which the refund policy does not say) and free shipping. The header's line on this page says what a stick order gets ("Buy 2, get 1 free · Free shipping · 30-day money-back guarantee", `ANNOUNCEMENT`), not the store's sale line with its gifts and 60% |
| $39 | 1 stick $39 · 2 sticks $59 (recommended, compare $78) · 3 sticks: buy 2, get 1 free $78 (compare $117, exactly 3 × $39); with Automatic Refills $31 / $47 / $62. Each card of several shows its price per stick, and the note under the cards says the crossed-out prices are sticks bought one at a time ($39 each) and that one-time is chosen on the cart page |
| "10 AM Morning / 10 PM Evening" | The `wear-day` photo (the same woman, morning and evening, labelled an illustration on the image; the evening half colour-matched to the morning's, since the page says it does not turn orange) and "From 10 AM to 10 PM", said as "made to wear all day" |
| "One stick for 16 skin tones" + three before/afters | The `tones` panel: 12 swatches and three women, fair, medium and deep, before and after (illustrations) |
| Linda S. and the other testimonials | The foundation's real imported reviews (same formula), labelled as the foundation's, in green boxed stars (the owner's request; no review site's name or logo). "Most helpful" puts first the reviews that tell her most: photos, fuller text, her age (45+) and her worries (shade, lines, dry skin); a review about a skin condition (acne, rosacea...) goes last, since a cosmetic treats none |
| FrontrowMD "Clinicians' Choice" | The foundation's FrontrowMD sticker in a box under the add-to-cart button, after a line saying it is the foundation's listing (not on the stick's photo, not under the title, where it read as the stick's and pushed the price under the phone's sticky bar); its × closes the whole box |
| "Love it or your money back · Refill reminder · Cancel any time · Renews at $66/mo" | The same trust row under the button, with the stick's own refill price and days |

## What we left out, and why

- **"Only 7 pieces remain in stock", "Promotion runs until 11:59 PM tonight"**: false urgency.
- **The $59 "was" price**: one stick is sold at $39 and nowhere at $59. Bundle savings are real (the single-stick
  price times the sticks).
- **"More than 50,000 women", "Loved by thousands"**: their count, not ours.
- **Its testimonials** (Linda S., Sarah 42, Claudia 38, Monica 52, Pamela 67): no review app behind them, several
  from women under 45, and not our customers (16 CFR 465). In their place: the foundation's real imported reviews,
  labelled as the foundation's.
- **The number in "16 skin tones"**: its own image says "fair to medium" (see Before launch).
- **"Anti-aging", "reduces redness", "supports the skin barrier", "supports recovery", "refines pores"**: skincare
  effects that need tests, some of them drug claims. A makeup evens the *look* of redness and spots, and that is what
  the page says.
- **"Lasts all day", "no irritation"**: wear and tolerance claims nothing backs.
- **The Facelove name and look**: the stick is SKINOFAB black, with the real wordmark.

## The buyer, and how the page talks to her

She is past 45 (Linda, 56, in our persona work): drier skin, more redness and sun spots, a shifted undertone. She
has bought five to ten foundations; the shade that matched in the shop looks orange at home, the formula settles into
her lines by lunch and looks cakey on dry patches, and she is tired of sponges, brushes and half-used bottles. Her
fears are the wrong shade, looking made-up, and wasting money again.

The page answers in that order: her problem in her words ("Your foundation used to work. Your skin changed."), why it
happens (her tone moved, her skin got drier, too many tools), then the stick as the answer (one shade that adapts,
creamy for dry skin, buffed in thin, the brush built in), how to use it in three steps, what to expect (1 minute, 0
shades, 30 days to try it), and the ten objections she will have (shade, lines, cakey, dry skin, spots, SPF, the
brush, sensitive skin, layering, refunds). It doesn't promise she will look 30.

## What is on the site

| Where | What |
|---|---|
| NEXT product 235 | "Adaptive Foundation Stick", public, subscriptions on (every 28, 56 or 84 days), template `adaptive-foundation-stick`, Face / Skin / Bestsellers; a gallery of 6 photos on the page, a woman past 50 with the stick first (none repeated in the sections, no two-tube packshot, each with its own alt text) |
| Bundles (variants) | 236: 1 stick $39, refills $31 · 237: 2 sticks $59, refills $47 (default; compare $78) · 238: 3 sticks (buy 2, get 1 free) $78, refills $62 (compare $117) |
| Product page | The Adaptive Peptide Foundation page's structure, section by section (`tools/persona/twin.py`), with `stick_copy.py`'s copy and `brand/foundation-stick/` photos |
| Homepage | A card in the product shelf after the foundation (default list, Bestsellers, New and Face tabs), "New" and "Buy 2, get 1 free" badges; a card in Essentials |
| Menus | "Adaptive Foundation Stick" after the foundation in the menu and in the footer's Shop column (the footer uses the menu's names, in its order) |
| Cart drawer | Its own upgrade card, 1 → 2 sticks for $20 (Theme settings → Cart Drawer → Fifth upgrade); not an add-on to the foundation (one foundation is enough) |

## Images

Made with GPT Image 2 through 4SToken (about $0.01 each; prompts in `tools/persona/image_prompts.json` under
`foundation-stick`), from one packshot of the black stick as the reference, on pure white, with women past 45 of
several ages and skin tones. `product_photos.py stick` prints the real wordmark on every stick
(`relabel_bottles.STICK`) and lays out the gallery's panels (One Stick, Your Shade; What's inside; The Science;
skinofab vs. others). The before/after photo is one AI portrait edited into its "after", so it is the same woman, the
same light and the same pose; it is an illustration and says so on the image and under it.
