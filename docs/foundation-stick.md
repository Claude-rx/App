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
- **Real photos.** The photos are AI-generated; the wordmark is printed on every stick by `relabel_bottles.py` from
  the real wordmark (`docs/real-wordmark.md`). Once the real stick exists, photograph it on white and swap `pack` and
  `single` first.

## What Facelove's page does, and what we kept

| Facelove device | Here |
|---|---|
| "The stick that makes mature skin glow again" | The buy box lead: the foundation that finds your shade for you, the brush on the other end, a minute, nothing to spill |
| "5 reasons" (natural finish, automatic shade, mature skin, light wear, skincare) | Problem / root cause / solution with five fixes, "The skinofab difference", the compare table and the six tabs |
| "No orange, grey or yellow tint", "no time wasted on color choices" | The problem ("orange in daylight, grey by the window"), "No shade to guess", "0 shades to choose" |
| "Does not settle into wrinkles", "no cakey, dry or tight feeling" | Said as how to get it: thin layers, buffed in with the brush, on moisturised skin (FAQ, tabs) |
| The five ingredient cards | The ingredient carousel, the science block and the Ingredients tab, as cosmetic effects |
| 30-day money-back guarantee, free shipping | The store's 30-day guarantee (no need to send it back) and free shipping |
| $39 | 1 stick $39 · 2 sticks $59 (most popular, compare $78) · Buy 2, get 1 free $78 (compare $117, exactly 3 × $39) |

## What we left out, and why

- **"Only 7 pieces remain in stock", "Promotion runs until 11:59 PM tonight"**: false urgency.
- **The $59 "was" price**: one stick is sold at $39 and nowhere at $59. Bundle savings are real (the single-stick
  price times the sticks).
- **"More than 50,000 women", "Loved by thousands"**: their count, not ours.
- **Its testimonials** (Linda S., Sarah 42, Claudia 38, Monica 52, Pamela 67): no review app behind them, several
  from women under 45, and not our customers (16 CFR 465). The stick shows "No reviews of the stick yet" until real
  SKINOFAB buyers review it; the reviews near the top are the foundation's, labelled as theirs.
- **"16 skin tones"**: its own image says "fair to medium".
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
| NEXT product 235 | "Adaptive Foundation Stick", public, one-time purchase, template `adaptive-foundation-stick`, Face / Skin / Bestsellers; gallery of 15 photos |
| Bundles (variants) | 236: 1 stick $39 · 237: 2 sticks $59 (default; compare $78) · 238: 3 sticks (buy 2, get 1 free) $78 (compare $117) |
| Product page | The Adaptive Peptide Foundation page's structure, section by section (`tools/persona/twin.py`), with `stick_copy.py`'s copy and `brand/foundation-stick/` photos |
| Homepage | A card in the product shelf after the foundation (default list, Bestsellers, New and Face tabs), "New" and "Buy 2, get 1 free" badges; a card in Essentials |
| Menus | "Adaptive Foundation Stick" after the foundation in the menu; "Foundation Stick" after it in the footer's Shop column |
| Cart drawer | Its own upgrade card, 1 → 2 sticks for $20 (Theme settings → Cart Drawer → Fifth upgrade); not an add-on to the foundation (one foundation is enough) |

## Images

Made with GPT Image 2 through 4SToken (about $0.01 each; prompts in `tools/persona/image_prompts.json` under
`foundation-stick`), from one packshot of the black stick as the reference, on pure white, with women past 45 of
several ages and skin tones. `product_photos.py stick` prints the real wordmark on every stick
(`relabel_bottles.STICK`) and lays out the gallery's panels (One Stick, Your Shade; What's inside; The Science;
skinofab vs. others). The before/after photo is one AI portrait edited into its "after", so it is the same woman, the
same light and the same pose; it is an illustration and says so on the image and under it.
