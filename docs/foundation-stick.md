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
  key ingredients Facelove's page names for the same stick; the Ingredients tab says so ("The key ingredients, as the
  stick's maker lists them") and "The full ingredient list is printed on the box". Facelove publishes no full
  ingredient list: check the supplier's INCI list and correct `INGREDIENTS` and `TWIN['inside']` in `stick_copy.py`
  if it differs. Since stick reviews 7 and 8 the page says what each one is and what it does in the cream, no result
  on the skin (no "more even-looking complexion", no "soft, supple skin", no gentleness claim resting on centella),
  and the "Adaptive color science" block explains the color capsules (what the stick shares with the foundation), not
  a third ingredient list. "The full ingredient list is printed on the packaging": US cosmetic packaging must carry
  it; make sure the supplier's does.
- **Shade range.** Facelove's page says both "16 skin tones" and, in its own gallery, "For fair to medium skin tones".
  Since stick review 6 the page says fair to medium: `SHADE_FAQ` ("made for fair to medium skin tones"; deeper skin
  emails first; a full refund within 30 days, even opened), the tones panel (fair, light-medium and medium women before
  and after, the tone bar stopping at medium: "One stick, fair to medium skin"), and the `temple` and `friends` photos
  re-made with light-medium models (a deep-skin result was a claim the page could not back). The earlier photos (a deep
  before/after pair, and women with deep skin in `temple` and `friends`) are in git history: if the supplier confirms
  a wider range, bring them back with `SHADE_FAQ` and the panel's title.
- **Net weight** (`NET`): shown in the Ingredients tab once set.
- **Where it is made** (`KOREAN`): off. The foundation, balm and serum say "Formulated in Korea"; the stick doesn't
  until the supplier confirms it.
- **Refills.** Automatic Refills are on by default, as on the foundation: $31 every 28 days for 1 stick, $47 every
  56 days for 2, $62 every 84 days for 3 (20% under the one-time price; one-time stays a choice on the cart page). How
  long a stick lasts decides the 28 days: change `BUNDLES[*]['refill'|'every']` and `REFILL['every']` in
  `stick_copy.py`, then rerun `setup_brush_offers.py skinofab <work> stick_copy` and the build.
- **"16 skin tones".** The owner's reference shows "One stick for 16 skin tones". The page gives no number and says
  fair to medium (above) until the supplier confirms the range: then put it in the `tones_panel` titles in
  `product_photos.py stick` and in `SHADE_FAQ`.
- **Reviews' 3-star share.** The wall shows 0% 3-star reviews: that is the earlier store's own export (7,719 five,
  2,132 four, 0 three, 1 two, 3 one), not a filter.
- **Same formula.** The reviews near the top and in the wall are the Adaptive Peptide Foundation's, labelled "Verified
  buyer of the foundation", because the owner states the stick is the same adaptive formula. If the supplier's stick
  formula differs, set `BORROW_REVIEWS = None` and `FRONTROW_NOTE = None` in `stick_copy.py` and the page shows its
  own (empty) reviews again.
- **Same formula, different ingredient lists.** The page lists hyaluronic acid, niacinamide, squalane, vitamin E and
  centella (Facelove's list); the foundation's page lists PDRN, Matrixyl 3000, Pro-Xylane, adenosine and ceramide NP.
  An independent review (26 Oct) flagged that "the same adaptive formula" and two different lists contradict each
  other. Since stick review 5 the page claims only what both share, the colour technology: the reviews are "of our
  Adaptive Peptide Foundation, which adapts to your tone the same way", the FrontrowMD line names "the liquid that
  adapts to your tone the same way this stick does", and the FAQ "Stick or bottle" names each one's base (the
  foundation's serum with peptides and PDRN, the stick's cream with hyaluronic acid, niacinamide and squalane). If the
  supplier's INCI shows the stick is the foundation's formula, the copy can say so again; if it shows a different
  colour technology, set `BORROW_REVIEWS = None` and `FRONTROW_NOTE = None`.
- **Size.** The close-up product photos have nothing to give scale, and the in-hand photos show a stick about a
  palm long; the page states no size. Once the supplier gives the length and net weight, add them to the
  Ingredients tab (`NET`) and an FAQ ("How big is it? How long does a stick last?").
- **Import duties.** The FAQ and the terms no longer promise "nothing more to pay at delivery" in every country
  (nothing shows the checkout collects duties): outside the US, "your country may charge import duties or taxes at
  delivery; email us before you order". If the checkout collects duties (duties paid), say so again in `FAQ` and in
  `ccf_copy.py`'s terms rule.
- **FrontrowMD's pop-up** says "Clinicians who shared this product" without naming it (FrontrowMD's own page, in a
  frame the store cannot change): the line above the badge says it is the foundation's listing. Ask FrontrowMD for a
  stick listing, or remove `FRONTROW_NOTE` to drop the badge from the stick's page.
- **Payment wallets.** The page and the drawer show the cards the checkout takes (Visa, Mastercard, Amex, Discover);
  if the checkout adds PayPal, Apple Pay or Google Pay, add their icons in Theme settings → Cart Drawer.
- **Proof.** The only demonstrations of "goes on white, turns into your tone" are AI illustrations, labelled as such.
  A 10–15 second real, unretouched clip of the stick on two or three women over 45 (fair, medium, deep) would be the
  page's strongest proof: gallery slide 3 (after the shade range) and "How does it work?".
- **Wear claim.** "From 10 AM to 10 PM" and "made to wear all day" are the owner's elements; a wear test (even an
  in-house one) would back them.
- **Real photos.** The photos are AI-generated; the wordmark is printed on every stick by `relabel_bottles.py` from
  the real wordmark (`docs/real-wordmark.md`). Once the real stick exists, photograph it on white and swap `pack` and
  `single` first. Two photos are mirrored before their print is set (`relabel_bottles.STICK_MIRROR`: `blend`,
  `buff-jaw`): held brush first towards the right, the print read upside down; mirrored, it reads the right way up
  and still runs from the brush end, as on every other photo.
- **Refill emails.** The trust row and the FAQ say "We email you before every refill" (the foundation's owner
  element): make sure the platform's subscription emails are on, since the store has no mailing service yet.
- **Brand replies to low reviews.** The wall's 1- and 2-star reviews (the earlier store's, under "Lowest rated")
  include "couldn't find how to cancel"; a short reply in your words under each would answer the next buyer.

## What Facelove's page does, and what we kept

| Facelove device | Here |
|---|---|
| "The stick that makes mature skin glow again" | The buy box lead: stop guessing your shade, it goes on white and adapts to your tone; three checks under it (`BULLETS`: for fair to medium skin tones, the brush built in, creamy for dry skin); under the title's price, what it is ("2 sticks with Automatic Refills, $23.50 a stick", kept in step with the chosen pack); the note on the refill and one-time prices under the button, where she agrees to the refills |
| "5 reasons" (natural finish, automatic shade, mature skin, light wear, skincare) | Problem / root cause / solution with five fixes, "The skinofab difference", the compare table and the six tabs |
| "No orange, grey or yellow tint", "no time wasted on color choices" | The problem ("orange in daylight, grey by the window"), "No shade to guess", "0 shades to choose" |
| "Does not settle into wrinkles", "no cakey, dry or tight feeling" | Said as how to get it: thin layers, buffed in with the brush, on moisturised skin (FAQ, tabs) |
| The five ingredient cards | The ingredient carousel, the science block and the Ingredients tab, as cosmetic effects |
| 30-day money-back guarantee, free shipping | Under the button, as on the foundation: the trust row, then "Free shipping on every order · Ships in 1 business day, tracked" and the boxed 30-day guarantee. The store's 30-day guarantee (a full refund, even opened, no questions asked: the original store's own words; nothing promises she keeps it, which the refund policy does not say) and free shipping. The header's line on this page says what a stick order gets ("Buy 2, get 1 free · Free shipping · 30-day money-back guarantee", `ANNOUNCEMENT`), not the store's sale line with its gifts and 60% |
| $39 | 1 stick $39 · 2 sticks $59 (recommended, compare $78) · 3 sticks: buy 2, get 1 free $78 (compare $117, exactly 3 × $39); with Automatic Refills $31 / $47 / $62. Each card of several shows its price per stick, and the note under the cards says the crossed-out prices are sticks bought one at a time ($39 each) and that one-time is chosen on the cart page |
| "10 AM Morning / 10 PM Evening" | The `wear-day` photo (the same woman, morning and evening, labelled an illustration on the image; the evening half colour-matched to the morning's, since the page says it does not turn orange) and "From 10 AM to 10 PM", said as "made to wear all day" |
| "One stick for 16 skin tones" + three before/afters | The `tones` panel, gallery slide 2: a tone bar from fair to medium and three women, fair, light-medium and medium, before and after (illustrations) |
| "Your old foundation" comparison | "Why SKINOFAB?" against a typical liquid foundation, each row as it is: no shade to choose, the brush built in, touch-ups from your bag (crossed for the liquid), buildable, natural coverage (ticked for both). Nothing knocks a pump bottle: the brand's own foundation is one |
| Linda S. and the other testimonials | The foundation's real imported reviews (it adapts to her tone the same way), labelled as the foundation's, in green boxed stars (the owner's request; no review site's name or logo). "Most helpful" puts first the reviews that tell her most: photos, fuller text, her age (45+) and her worries (shade, lines, dry skin); a review about a skin condition (acne, rosacea...) goes last, since a cosmetic treats none |
| FrontrowMD "Clinicians' Choice" | The foundation's FrontrowMD sticker in a box under the foundation's review strip (since stick review 6; in the buy box it read as the stick's own), after a line saying it is the foundation's listing (not on the stick's photo, not under the title, where it read as the stick's and pushed the price under the phone's sticky bar); its × closes the whole box |
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
creamy for dry skin, buffed in thin, the brush built in), how to use it in three steps (twist, dot, buff, the same three everywhere on the page), what to expect (3 steps,
0 shades, 30 days to try it), and the ten objections she will have (shade, lines, cakey, dry skin, spots, SPF, the
brush, sensitive skin, layering, refunds). It doesn't promise she will look 30.

## What is on the site

| Where | What |
|---|---|
| NEXT product 235 | "Adaptive Foundation Stick", public, subscriptions on (every 28, 56 or 84 days), template `adaptive-foundation-stick`, Face / Skin / Bestsellers; a gallery of 6 photos on the page, a woman past 50 with the stick first (none repeated in the sections, no two-tube packshot, each with its own alt text) |
| Bundles (variants) | 236: 1 stick $39, refills $31 · 237: 2 sticks $59, refills $47 (default; compare $78) · 238: 3 sticks (buy 2, get 1 free) $78, refills $62 (compare $117); the buy box's cards use these names, as the bag and the cart do. The cart page's choice says each price ("One-time purchase · $59", "Refill every 56 days · $47") |
| Product page | The Adaptive Peptide Foundation page's structure, section by section (`tools/persona/twin.py`), with `stick_copy.py`'s copy and `brand/foundation-stick/` photos |
| Homepage | A card in the product shelf after the foundation (default list, Bestsellers, New and Face tabs), "New" and "Buy 2, get 1 free" badges; a card in Essentials |
| Menus | "Adaptive Foundation Stick" after the foundation in the menu and in the footer's Shop column (the footer uses the menu's names, in its order) |
| Cart drawer | A line bought once says "One-time purchase · Change" (a refill line says how often it ships). Its own upgrade cards: 1 → 2 sticks ($16 more with refills, $20 bought once; Theme settings → Cart Drawer → Fifth upgrade) and, with the 2-stick pack in the bag, 2 → 3 sticks, buy 2, get 1 free ($15 more with refills, $19 bought once; Sixth upgrade); not an add-on to the foundation (one foundation is enough). The 30-day guarantee sits in the drawer's footer, under the checkout button |

## Images

Made with GPT Image 2 through 4SToken (about $0.01 each; prompts in `tools/persona/image_prompts.json` under
`foundation-stick`), from one packshot of the black stick as the reference, on pure white, with women past 45 of
several ages and skin tones. `product_photos.py stick` prints the real wordmark on every stick
(`relabel_bottles.STICK`) and lays out the gallery's panels (One Stick, Your Shade; What's inside; The Science;
skinofab vs. others). The before/after photo is one AI portrait edited into its "after", so it is the same woman, the
same light and the same pose; it is an illustration and says so on the image and under it.
