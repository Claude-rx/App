"""Copy for the Color Changing Foundation, rewritten for the 45+ buyer persona ("Linda, 56").

Source: Skinofab_Color_Adapting_Foundation_Market_and_Persona_Report.md (21 Oct 2026).
- Her pain: she can't find her shade anymore, foundation settles into her lines and dries her skin, she wants to
  look fresh and even in a minute, and she distrusts brands that over-promise.
- Positioning: "The color-adapting serum foundation made for skin after 45. Hydrates, blurs, and treats with
  peptides & PDRN, in one bottle."
- Compliance (report section 11): no SPF claim, never "matches every skin tone" (the copy says it adapts to your
  tone), a money-back guarantee, and refill terms shown next to the button whenever refills are chosen.
- Offer (owner, 22 Oct 2026): one product for every skin tone (no bases), 1 or 2 bottles, one-time or with
  automatic refills every 28 days (PACKS / REFILL below).

Each rule is (old, new). `old` is visible text as it appears in the export; whitespace, typographic apostrophes
and dashes are matched loosely. GLOBAL rules run on every page, PAGE rules on one file. Every rule must match at
least once or the build fails, so copy can't silently drift from the design.
"""
import support_copy

# where every SKINOFAB formula is made: the buy box's line, the gallery badges (product_photos.korea_badge) and the
# pages say formulated in Korea, never made in Korea
ORIGIN = '🇰🇷 Formulated in Korea · Advanced K-beauty formula'

GLOBAL = [
    # the footer: the brand's name as its logo writes it, and a line that says what the brand makes and for whom,
    # not a generic one (stick review 3)
    ('A little more Skinofab in your inbox.', 'A little more SKINOFAB in your inbox.'),
    # its line said "inbox" a second time, with the page's one serial comma (stick review 8)
    ('New arrivals, beauty tips, and little treats for your inbox.', 'New arrivals, beauty tips and little treats.'),
    ('>About Skinofab<', '>About SKINOFAB<'),
    (r'RE:<p><em><strong>Skinofab</strong> is a solutions-oriented beauty brand, creating a world where everybody feels confident\.</em></p>',
     '<p><em><strong>SKINOFAB</strong> makes makeup and skincare for skin after 45: simple to use, comfortable on dry skin, '
     'and honest about what each product does.</em></p>'),
    # the comparison table's "no" mark: a white cross on light grey (#e0e0e0) all but vanished on white (stick
    # review 3); a mid grey carries it (3.4:1 against white, its white cross 3.4:1), and it says "No" to a screen reader
    (r'RE:<svg fill="none" height="20" viewbox="0 0 20 20" width="20" xmlns="http://www.w3.org/2000/svg"><circle cx="10" cy="10" fill="#e0e0e0" r="10">',
     '<svg fill="none" height="20" viewbox="0 0 20 20" width="20" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="No"><circle cx="10" cy="10" fill="#8a8a8a" r="10">'),
    # "The skinofab difference" button: there is no offer to claim, it scrolls to the packs (stick review 1)
    (r'RE:(<a class="btn btn--dark" href="#product">)Claim offer(</a>)', r'\g<1>Choose your pack\g<2>'),
    # the home hero's line: the number is the formula's verified reviews from the earlier store, not SKINOFAB's
    # customers (review 7; the listing row says the same)
    (r'RE:<span>Loved by [\d,]+\+ customers</span>', '<span>9,800+ verified reviews</span>'),
    # the old store's product name where a screen reader or the page's data still says it (review 7): the gallery's
    # thumbnails and the home card's image link, the product data's name and image alts, the old SKU
    (r'RE:aria-label="Color Changing Foundation"', 'aria-label="Adaptive Peptide Foundation"'),
    (r'RE:"(name|title)":"Color Changing Foundation"', r'"\g<1>":"Adaptive Peptide Foundation"'),
    (r'RE:Color Changing Foundation — lifestyle photo \| Skinofab', 'Adaptive Peptide Foundation, lifestyle photo'),
    (r'RE:"sku":"SMO-CCF-001"', '"sku":""'),
    # the brand's name in capitals in the product page's headings, as in the wordmark (stick review 2)
    ('Why skinofab?', 'Why SKINOFAB?'),
    ('The skinofab difference', 'The SKINOFAB difference'),
    # the contact page's answer pointed to the form "below": it sits above the questions (review 6)
    ('You can contact us by filling in the contact form below', 'You can contact us by filling in the contact form above'),
    # the policies' "the Personal Data strictly necessary" link (privacy, cookie and terms pages, all in pages/) opened
    # iubenda's hosted copy of another store's policy (review 6): this store's cookie policy
    ('href="https://www.iubenda.com/privacy-policy/65675001" target="_blank"', 'href="cookie-policy.html"'),
    # the product gallery's image sizes: from 768 to 1023 px the gallery is one column, the page's whole width
    # (apply_persona.LAYOUT_FIXES), not 60% of it, so it asked for a file half the size it shows
    (r'RE:sizes="\(min-width: 1400px\) 762px, \(min-width: 768px\) calc\(\(100vw - 40px\) \* 0\.6 - 30px\), calc\(100vw - 40px\)"',
     'sizes="(min-width: 1400px) 762px, (min-width: 1024px) calc((100vw - 40px) * 0.6 - 30px), calc(100vw - 40px)"'),
    # the product page's "How does it work?": the old store's "intelligent mineral pigments", in the product's words
    (r'RE:Our (?:Skin-Tone Adapting|Color Changing|Color-Adapting|Adaptive Peptide) Foundation uses intelligent mineral pigments that adjust as you blend\.',
     'Our Adaptive Peptide Foundation goes on white and adapts to your skin tone as you blend.'),
    (r'RE:At first touch, the pigments look soft and neutral\. As you smooth the formula across your skin, these micro-pigments disperse and warm up, revealing the natural blend of tones your complexion needs\.',
     'Its color-adapting pigments are encapsulated. As you smooth the formula across your skin, they release and mix into your own tone in about a minute.'),
    # the money-back icon was a warped photo of a seal ("% 100 %"): a drawn 30-day badge, crisp at 50 px. It fills
    # its holder the way the photo's figure did (the holder is 0 px tall with a padding-top ratio: a 100%-tall svg
    # in it drew nothing, review 4)
    (r'RE:<figure class="lazy-image is-loading lazy-image--cover"><img class="is-loading product__icon__img img-object-cover"[^>]*'
     r'Color_Changing_Foundation_-_Product_images_photos_2-[^>]*>\s*</figure>',
     '<svg class="product__icon__img" viewBox="0 0 100 100" width="50" height="50" role="img" aria-label="30-day money-back guarantee" '
     'style="display:block;position:absolute;top:0;left:0;width:100%;height:100%"><circle cx="50" cy="50" r="48" fill="#151515"/>'
     '<circle cx="50" cy="50" r="40" fill="none" stroke="#fff" stroke-width="2" stroke-dasharray="2.5 3.5"/>'
     '<text x="50" y="54" text-anchor="middle" font-family="Jost,Arial,sans-serif" font-weight="700" font-size="34" fill="#fff">30</text>'
     '<text x="50" y="73" text-anchor="middle" font-family="Jost,Arial,sans-serif" font-weight="600" font-size="12" letter-spacing="1.5" fill="#fff">DAYS</text></svg>'),
    # the listing pages' benefit row: claims no product here can back ("100% natural": the foundation's silica and
    # boron nitride are not; "proven results" with no study named) become what holds for all four products
    (r'RE:(icons-row__title">)100% natural<', r'\g<1>Made for skin after 45<'),
    (r'RE:(icons-row__title">)Natural ingredients<', r'\g<1>Made for skin after 45<'),
    (r'RE:(icons-row__title">)Proven results<', r'\g<1>30-day money-back guarantee<'),
    (r'RE:(icons-row__title">)Scientifically proven<', r'\g<1>30-day money-back guarantee<'),
    (r'RE:(icons-row__title">)Quick results<', r'\g<1>30-day money-back guarantee<'),
    # 9,800+ is the count of the foundation formula's verified reviews from the earlier store, not of SKINOFAB's
    # customers (review 6): the row says what the number is
    (r'RE:(icons-row__title">)Loved by 100\.000\+<', r'\g<1>9,800+ verified reviews<'),
    ('>Korean inspired performance formulas<', '>Formulated in Korea, with advanced K-beauty science<'),
    ('>3. Built in Korea, by the people who invented the science<', '>3. Formulated in Korea, with advanced K-beauty science<'),
    ('a breakthrough foundation from Korean pharmacies,', 'a breakthrough foundation formulated in Korea,'),
    # the announcement bar: 60% is the deepest saving on the site (the foundation's 2 bottles on refills, $47 vs
    # $118; every other pack saves at most a third: a new product has no "was" price of its own), not every
    # product's, and the gifts come with the 2-bottle pack and the brush 3-pack
    ("🍂 Fall Sale: 60% OFF + FREE Mystery Gift", "🍂 Fall Sale: Up to 60% OFF + FREE Gifts on Select Packs"),
    # one dermatologist speaks on the homepage, not "leading dermatologists worldwide"; the results card is backed by
    # the verified reviews under it, not by a study
    ("Trusted by leading dermatologists worldwide", "Recommended by a dermatologist"),
    ("Proven results on real skin", "Real results on real skin"),
    # SPF: the foundation carries no SPF claim (report 11). Sentences first, then the bare chips.
    # Dr. Mamaeva's quote keeps her own words: the SPF clause is dropped, nothing is put in its place.
    ("The Color Changing Foundation is what I recommend most to patients over forty. It adapts to her tone, it has SPF, and it doesn't turn orange or sink into fine lines.",
     "The Color Changing Foundation is what I recommend most to patients over forty. It adapts to her tone, and it doesn't turn orange or sink into fine lines."),
    ("I loved not having to layer sunscreen underneath.", "I loved how it felt like skincare, not makeup."),
    ("The SPF 15 is built in, so my skin is protected during everyday exposure without shine or heaviness.",
     "It feels like a serum, so my dry patches stay comfortable all day, without shine or heaviness."),
    ("5. Built-in SPF 15 without the greasy feel", "5. Hydrates like a serum, without the greasy feel"),
    ("7. Built-in SPF 15 without the greasy feel", "7. Hydrates like a serum, without the greasy feel"),
    ("Yes! The Color Changing Foundation includes SPF 15, providing a layer of sun protection as part of your everyday makeup routine.",
     "No. We left SPF out on purpose so the formula can stay a light, hydrating serum. Wear it over your daily sunscreen; it blends on top without pilling."),
    ("Heavy foundations feel tight by midday. This one is weightless. It doesn't cling to dry patches or slide into lines, and there's SPF 15 built in.",
     "Heavy foundations feel tight by midday. This one is weightless. It doesn't cling to dry patches or slide into lines, and it's fragrance-free."),
    ("5. Built-in SPF 15", "5. Hydrating serum base"),
    ("SPF 15 helps defend your skin from everyday sun damage - the quiet culprit behind dark spots, fine lines, and dullness. Lightweight, invisible, and easy to wear daily.",
     "Hyaluronic acid, ceramide NP and squalane keep thinner, drier skin comfortable all day, so the finish stays smooth instead of tight or flaky. Wear it over your daily sunscreen."),
    ("Has SPF 15", "Hydrating serum base"),
    ("SPF 15 for everyday sun protection", "Hydrating serum base for dry, mature skin"),
    ("Hydrates and Protects with SPF 15", "Hydrates with a serum base, fragrance-free"),
    (", lasts all day (up to 16 hours), and hydrates skin while protecting it with SPF 15. The Changing Foundation is hypoallergenic, vegan, and waterproof.",
     ", stays comfortable through a full day, and hydrates with hyaluronic acid, ceramide NP and squalane. It's fragrance-free and made for skin after 45."),
    ("Meet the foundation that takes the guesswork out of beauty. Our color-changing formula adjusts seamlessly to fair to medium skin tones, giving you a radiant, natural finish that looks like your skin, only better. It blurs imperfections, softens fine lines, and neutralizes redness in seconds, all while protecting with SPF 15. One shade, endless confidence. Just apply, blend, and watch the transformation.",
     "Your skin changed after 45: a few sun spots, some redness, a tone that isn't what it was. This foundation goes on white and turns into your skin tone as you blend. A satin serum finish evens out spots and redness and blurs the look of fine lines without sitting in them. No shade guessing, no mask, about a minute with your fingertips."),
    ("With SPF 15", "Fragrance-free"),
    ("SPF protection", "Hydrating, fragrance-free formula"),
    ("— Sun damage accelerates skin aging, so a built-in SPF is a bonus, not a gimmick.",
     "— Mature skin makes less oil, so a hydrating, fragrance-free base matters more than an SPF number in your foundation. Keep sunscreen as its own step."),
    ("Yes, I know, SPF every day. I never did it. It was greasy and it made everything pill. So we put <strong>SPF 15</strong> straight into the foundation and now I'm covered for everyday sun without thinking about it. No shine, no heaviness, and one less bottle on my counter.",
     "Yes, I know, sunscreen every day. I wear mine, but every foundation I put on top of it pilled or dried into my lines. So we made a hydrating, fragrance-free foundation that layers over sunscreen without pilling. No shine, no heaviness, nothing tight by lunch."),
    # Shipping: the store has one rate, free on every order (NEXT shipping method "Default", $0.00). There is no paid
    # "premium insured" option at checkout, so the sentences offering one go.
    (r'RE:\s*Additionally,\s+we\s+offer\s+a\s+premium\s+international\s+insured\s+shipping\s+option\s+at\s+a\s+modest\s+charge\s+of\s*<strong>[^<]*</strong>,\s+which\s+we\s+highly\s+recommend\s+for\s+prioritized\s+service\s+and\s+faster\s+delivery\.', ''),
    (r'RE:\s*We\s+also\s+offer\s+a\s+premium\s+international\s+insured\s+shipping\s+option\s+for\s+just\s+\$2\.99\s?USD,\s+which\s+we\s+recommend\s+for\s+prioritized\s+service\s+and\s+faster\s+delivery\.?', ''),
    # the remaining bare "SPF 15" chips / comparison-table rows
    (">SPF 15<", ">Fragrance-free<"),
    # 16-hour wear and "all skin tones" over-promises (report 4.4 and 11)
    ("Natural look for 16+ hours", "Hydrates like a serum"),
    ("Lasts 16+ hours", "Hydrating serum base"),
    (">Lasts 16 hours<", ">No creasing<"),
    # a heading's "K-beauty" kept on one line: capitalised, it broke after the hyphen ("Advanced K-" / "Beauty
    # Science", review 5)
    (r'RE:(<h[1-3][^>]*>[^<]*?)\bK-([Bb]eauty)', r'\g<1><span style="white-space:nowrap">K-\g<2></span>'),
    # the ingredients pop-up lists the key ingredients (the full list is on the box): its link said "View full list"
    # (review 5)
    (r'RE:(<a class="accordion-popup-trigger" data-popup-trigger="[^"]*" href="#">)\s*View full list\s*(</a>)', r'\g<1>See all key ingredients\g<2>'),
    (r'RE:(<h3 class="popup-modal__title">)Ingredients(</h3>\s*<div class="popup-modal__body rte">\s*<p>Key ingredients:)', r'\g<1>Key ingredients\g<2>'),
    # the policy pages' contents and summary cards opened as dialogs on the old platform (its script is gone): here
    # they are always shown in the page, and their "Table of contents", "Back to overview" and close buttons did
    # nothing (review 5)
    (r'RE:<div class="table-of-content-btn-wrapper d-mobile">\s*<button aria-controls="table-of-content-wrapper" class="open-dialog table-of-content-toggle">Table of contents</button>\s*</div>\s*', ''),
    (r'RE:<p><a class="close-dialog">Back to overview</a></p>\s*', ''),
    (r'RE:<a class="close-dialog"></a>\s*', ''),
    (r'RE:<button class="close-dialog">(?:Back to overview|<span class="sr-only">Close</span>)</button>\s*', ''),
    # Shopify's installments widget, carrying the old shop's data (its variant, a $49 price), dead on NEXT (review 5)
    (r'RE:<shopify-payment-terms[^>]*>[\s\S]*?</shopify-payment-terms>', ''),
    (r'RE:<div class="card-buttons-group d-mobile">(?:\s*<button aria-controls="[^"]*" class="card-button open-dialog">[^<]*</button>)+\s*</div>\s*', ''),
]

PAGE = {
    'index.html': [
        # the product shelf: four of its five products are new, so it is the range, not "Bestsellers" (review 7)
        (r'RE:<h2>Bestsellers</h2>', '<h2>Shop the range</h2>'),
        (r'RE:aria-label="Bestsellers"( class="fh-tabs")', r'aria-label="Shop the range"\g<1>'),
        (r'RE:(data-fh-tab="bestsellers_0" role="tab" type="button">)Bestsellers<', r'\g<1>All<'),
        # the one-shade card: the tint shifts as you blend, in about a minute (the PDP's own wording), not on contact
        ("Our color-adapting foundation shifts to match your skin tone the moment it touches your skin, then settles"
         " into a smooth, natural finish",
         "Our color-adapting foundation goes on white and shifts to your skin tone as you blend, in about a minute, "
         "then settles into a smooth, natural finish"),
        # "Formulated in Korea" cards: "ceramides, panthenol and glycerin in every formula", "vitamin C": no product lists
        # vitamin C, the serum has neither ceramides nor panthenol, only the foundation says fragrance-free
        ('Ceramides, panthenol and glycerin in every formula. Fragrance-free, so nothing fights your barrier while the rest works.',
         'Hydrating bases for dry, mature skin: hyaluronic acid in the foundation and the balm, glycerin in the serum. The '
         'foundation is fragrance-free.'),
        ('PDRN, peptides, collagen and vitamin C, at levels that do something. Named on the box, never hidden in a complex.',
         'PDRN, peptides, EGF, NAD+ and collagen, each named on its box, never hidden in a complex.'),
        # meta description + og:description (the theme uses it while Settings > SEO has no store description)
        ("Cosmetics made to glow, feel skinofab.",
         "Adaptive Peptide Foundation: the color-adapting serum foundation made for skin after 45. Goes on white, turns into your skin tone. Free shipping, 30-day money-back guarantee."),
        # the hero and "One shade that finds yours" keep the export's own words (the homepage is its original
        # design), with one claim made accurate: it softens the look of lines as it blends, not "in seconds"
        ("blurring blemishes, redness, and fine lines in seconds.", "softening the look of blemishes, redness and fine lines as you blend."),
        # "flawlessly" beside the FAQ's honest word for very fair and deep skin (review 3)
        ("Adapts flawlessly to your unique skin tone,", "Adapts to your unique skin tone,"),
        (">Look visibly younger<", ">Made for 45+<"),
    ],
    'pages/bestfoundation-2.html': [
        # reason 7's clip is the old brand's bottle (SMOOCHE, "With SPF 15", "16+ hours"): the page's own photo of a
        # woman blending our bottle in its place, in the markup of the page's other reasons
        (r'RE:<div class="bf-media bf-video" data-bf-video="">\s*<video [^>]*9d634628[^>]*></video>\s*'
         r'<div class="bf-video-controls">.*?</div>\s*</div>',
         '<picture class="bf-media"><img alt="Blending the Adaptive Peptide Foundation" height="405" loading="lazy" '
         'src="../assets/img/9be7e268-4413-428c-b92c-b660e1331473-433765.jpg" width="405"/></picture>'),
    ],
    # the policies (iubenda's, from the old store): their icons loaded from iubenda's own path on this domain (404, a
    # console error each), the processors' logos were signed links that expire a week after export (empty bullets),
    # and a bullet showed a logo only. iubenda's copies of the icons, its generic icon for the logos, and the names
    'pages/privacy-policy.html': [
        (r'RE:src="/assets/site/legal_docs/', 'src="https://www.iubenda.com/assets/site/legal_docs/'),
        (r'RE:src="https://s3\.eu-west-1\.amazonaws\.com/prd\.mater/uploads/service_provider_icons/[^"]*"',
         'src="https://www.iubenda.com/assets/site/favicons/default_thirdparty_icon-7c0e4af091131d326a69845f5900e1fbf9fdea8b8cecbe7e7aaecf6dbf0da741.svg"'),
        (r'RE:<li class="third-parties-item"><img alt="\s*([^"]*?)\s*"[^>]*/></li>',
         r'<li class="third-parties-item" style="display:inline-block;margin:0 6px 6px 0;padding:3px 10px;border:1px solid #d9d9d9;border-radius:999px;font-size:13px;line-height:1.5">\1</li>'),
        # its links to "the Cookie Policy" and to "the Personal Data strictly necessary" opened iubenda's hosted copies
        # of the old store's policies (smooche.com, Smooche LLC, review 6): this store's own cookie policy instead
        ('href="//www.iubenda.com/app/privacy-policy/10395211/cookie-policy"', 'href="cookie-policy.html"'),
    ],
    'pages/cookie-policy.html': [
        # the browsers' cookie help and the opt-out sites, at their current addresses (a retired Windows Vista page and
        # http:// links that no longer load, store audit 8)
        ('href="http://windows.microsoft.com/en-us/windows-vista/block-or-allow-cookies"',
         'href="https://support.microsoft.com/en-us/microsoft-edge/delete-cookies-in-microsoft-edge-63947406-40ac-c3b8-57b9-2a946a29ae09"'),
        ('>Microsoft Internet Explorer<', '>Microsoft Edge<'),
        ('href="http://www.ddai.info/optout"', 'href="https://www.ddai.info/optout"'),
        ('href="http://www.youronlinechoices.eu/"', 'href="https://www.youronlinechoices.eu/"'),
        (r'RE:src="https://s3\.eu-west-1\.amazonaws\.com/prd\.mater/uploads/service_provider_icons/[^"]*"',
         'src="https://www.iubenda.com/assets/site/favicons/default_thirdparty_icon-7c0e4af091131d326a69845f5900e1fbf9fdea8b8cecbe7e7aaecf6dbf0da741.svg"'),
    ],
    'pages/terms-of-service.html': [
        # the generator's "1 days", and a 30-day delivery default beside the shipping policy's own times
        ('Terminations shall take effect 1 days after', 'Terminations shall take effect 1 day after'),
        ('The notice period is 1 days.', 'The notice period is 1 day.'),
        ('Unless otherwise specified on this Application or agreed with Users, Products shall be delivered within thirty (30) days from purchase.',
         'Products are shipped within 1 business day of purchase and delivered within the times our Shipping Policy gives for each destination.'),
        # the money-back guarantee as the refund policy, FAQ and product pages give it: a full refund, opened or not
        # (the generator's text had the goods sent back at the buyer's cost, unused and in their packaging; a "no need
        # to send it back" here was a promise the owner never made, and the refund policy did not say it, store audit 8)
        (r'RE:<p>Within the same period of time stated above, Users must also return the purchased goods to the Owner at their own '
         r'expense, making sure that they are undamaged, clean and fit for resale\. Goods must be returned inside the original packaging\.<br/>\s*'
         r'Upon receipt of the goods, the Owner will verify that all conditions applicable to the money-back-guarantee are fulfilled and, if so, refund the purchase price\.</p>',
         '<p>Under this guarantee the Owner refunds the price of the Product in full, even if it has been opened and used, '
         'as set out in the Owner’s refund policy.</p>'),
        # a second delivery is not part of the free shipping (the generator's line read as if shipping cost something)
        ('Unless otherwise agreed, any delivery attempt starting from the second shall be at the User’s expense.',
         'Shipping is free. Unless otherwise agreed, a new delivery after a failed or uncollected first delivery is at the '
         'User’s expense.'),
        # prices as the FAQ and the product pages state them (the generator's "exclusive or inclusive, depending on
        # the section")
        (r'RE:<p>Prices on this Application are displayed:</p>\s*<ul>\s*<li>either exclusive or inclusive of any applicable fees, '
         r'taxes and costs, depending on the section the User is browsing\.</li>\s*</ul>',
         # (no promise about import duties: nothing shows the checkout collects them, stick review 5)
         '<p>The price shown at checkout includes any applicable fees and taxes the Owner collects. Import duties or taxes '
         'charged by the destination country, if any, are not included and are payable by the User at delivery.</p>'),
        # payment methods the checkout does not offer (it takes cards)
        (r'RE:(?s)<h3 id="payment-of-price-in-installments">Payment of price in installments</h3>\s*<p>.*?</p>\s*', ''),
        (r'RE:(?s)<h3 id="authorization-for-future-paypal-payment">Authorization for future PayPal payment</h3>\s*<p>.*?</p>\s*<p>.*?</p>\s*', ''),
    ],
    'pages/about-skinofab.html': [
        # "98% feel more confident" and the rest came from no survey: what holds instead
        (r'RE:<span class="sa-eyebrow" style="justify-content:center;">The results</span><h2>What our community feels</h2>',
         '<span class="sa-eyebrow" style="justify-content:center;">Our promise</span><h2>What you can count on</h2>'),
        (r'RE:<div class="sa-stat__num">98%</div>\s*<div class="sa-stat__label">Feel more confident</div>',
         '<div class="sa-stat__num">30 days</div> <div class="sa-stat__label">to try it, or your money back</div>'),
        (r'RE:<div class="sa-stat__num">97%</div>\s*<div class="sa-stat__label">Feel more attractive</div>',
         '<div class="sa-stat__num">9,800+</div> <div class="sa-stat__label">verified reviews of our foundation’s formula, from our earlier store</div>'),
        (r'RE:<div class="sa-stat__num">100%</div>\s*<div class="sa-stat__label">Feel more like themselves</div>',
         # (the foundation, serum and balm: the stick's origin is not confirmed yet, and the brush is a tool)
         '<div class="sa-stat__num">Korea</div> <div class="sa-stat__label">where our foundation, serum and balm are formulated</div>'),
    ],
    'pages/postflows-track-your-order.html': [
        ("Fill in your order number or tracking code to see where your package currently is.",
         "Fill in your tracking code to see where your package is right now."),
    ],
    'policies/shipping-policy.html': [
        (r'RE:<span>6-8 Business Day</span>', '<span>6-8 Business Days</span>'),
        (r'RE:6-8\xa0 Business Days', '6-8 Business Days'),
    ],
    'products/color-changing-foundation.html': [
        # 'The skinofab difference': the shade takes about a minute of blending, as the page says everywhere else
        ('Visible results in seconds', 'Your shade in about a minute'),
        ('Watch it adapt to your exact skin tone as you blend', 'It goes on white and shifts toward your skin tone as you blend'),
        (r'RE:(skinofab-why__feature-icon">\s*<img) alt="[^"]*"', r'\g<1> alt=""'),     # decorative icons
        # the guarantee tab: the refund policy's terms (an email within 30 days, a full refund once approved, no return)
        ("We know finding the perfect foundation match online can feel like a gamble. That's why we've eliminated the risk "
         "entirely. Try it on your skin, in your lighting, with your routine. If it's not your perfect match, simply let us "
         "know within 30 days and we'll process your full refund immediately.",
         "Buying foundation online after 45 feels like a gamble, so try it on your skin, in your lighting, with your "
         "routine. If you don't love it, email info@skinofab.com within 30 days and we'll refund it in full, even "
         "opened, no questions asked."),
        # "Shipping and returns" and two FAQ answers came from the old store: 24-48 h dispatch, 5-7 days, "65+ countries",
        # returns "new, unused, in their original packaging". The store's terms instead (support_copy.py, as the
        # shipping and refund policies say them)
        (r'RE:(?s)<div id="shippingAccordionContent">.*?</p></div>',
         '<div id="shippingAccordionContent">' + support_copy.SHIPPING_TAB_HTML + '</div>'),
        ('We offer free worldwide shipping to 65+ countries. Please see our',
         'Shipping is free to every country offered at checkout, with tracking: 2–4 business days in the US, 6–9 to '
         'Europe, the UK, Canada, Australia and New Zealand, 8–12 elsewhere. See our'),
        ('All returns must be postmarked within thirty (30) days of delivery. All returned items must be new, unused, '
         'and in their original packaging. See our', support_copy.RETURNS_SHORT + ' See our'),
        # ingredient carousel: photo alt, heading and line change together
        (r'RE:alt="SPF\ 15"', 'alt="Peptides + PDRN"'),
        (r'RE:(<h3[^>]*>)\s*SPF\ 15\s*(</h3>\s*<p[^>]*>)\s*Helps\ protect\ skin\ from\ everyday\ UV\ exposure\s*(?=</p>)', r'\g<1>Peptides + PDRN\g<2>Matrixyl 3000 peptides, PDRN and niacinamide: skincare for thinner skin after 45, not just color on top'),
        (r'RE:alt="Glycerin"', 'alt="Hyaluronic acid + ceramide NP"'),
        (r'RE:(<h3[^>]*>)\s*Glycerin\s*(</h3>\s*<p[^>]*>)\s*This\ ingredient\ helps\ skin\ feel\ hydrated\ and\ comfortable\.\s*(?=</p>)', r'\g<1>Hyaluronic acid + ceramide NP\g<2>Two forms of hyaluronic acid with ceramide NP, squalane and panthenol keep dry skin comfortable all day'),
        (r'RE:alt="Color\ Changing\ Pigments"', 'alt="Color-adapting pigments"'),
        (r'RE:(<h3[^>]*>)\s*Color\ Changing\ Pigments\s*(</h3>\s*<p[^>]*>)\s*Adapt\ to\ your\ skin\ tone\ as\ you\ blend\s*(?=</p>)', r'\g<1>Color-adapting pigments\g<2>Go on white and shift to your tone as you blend'),
        (r'RE:alt="Natural\-looking\ coverage"', 'alt="Soft-focus powders"'),
        (r'RE:(<h3[^>]*>)\s*Natural\-looking\ coverage\s*(</h3>\s*<p[^>]*>)\s*Evens\ out\ your\ complexion\ and\ helps\ fine\ lines\ look\ less\ noticeable\s*(?=</p>)', r'\g<1>Soft-focus powders\g<2>Silica and boron nitride blur the look of lines and pores without a dry, matte finish'),
        (r'RE:alt="Mica"', 'alt="Fragrance-free"'),
        (r'RE:(<h3[^>]*>)\s*Mica\s*(</h3>\s*<p[^>]*>)\s*Natural\ mineral\ pigments\ for\ a\ soft,\ healthy\ glow\.\s*(?=</p>)', r'\g<1>Fragrance-free\g<2>No fragrance, propylene glycol, drying alcohol or parabens, so thinner skin doesn’t sting'),
        ("The viral skin tone adapting foundation", ORIGIN),
        ("Hides imperfections", "Won't settle into lines"),
        ("Say goodbye to shade-matching struggles. This color-changing foundation adapts flawlessly to your unique skin tone, blurring blemishes, redness, and fine lines in seconds.",
         "Stop guessing your shade after 45. It goes on white and turns into your skin as you blend, evening out spots and redness and softening the look of fine lines in about a minute. A hydrating serum base with peptides and PDRN means it doesn't dry you out or settle into your lines."),
        ("Try it worry-free. If our skin-adapting foundation doesn't blend seamlessly with your tone, you'll get your money back*",
         "Wear it in your own daylight for 30 days. If you don't love it, we'll refund you."),     # (the export's * had no footnote)
        ("One shade, verified range", "One adaptive shade"),
        ("Simpler shade selection within fair-to-medium",
         "Goes on white and adapts to your tone, so there is no shade to pick"),
        ("Skin-like finish designed for mature-skin preparation", "Satin, skin-like finish made for dry, lined skin after 45"),
        ("Our adaptive pigment formula removes the need to choose a shade. As you blend, micro-encapsulated pigments react to your skin’s warmth and undertones, shifting within seconds to match your unique complexion. Made for fair to medium tones, it evens redness, blurs imperfections, and melts into the skin for a seamless, second-skin finish.",
         "Most color-changing foundations are a basic, drying base with fragrance and nothing in it for your skin. Ours is a serum. Hyaluronic acid, ceramide NP, squalane and panthenol keep dry skin comfortable; peptides (Matrixyl 3000), PDRN and niacinamide are there for the skin underneath; soft-focus powders blur the look of lines and pores. Adaptive pigments go on white and shift to your tone as you blend, inside the base you choose."),
        ("Our Color Changing Foundation is suitable for all skin tones above and in between.",
         "There is one shade. It goes on white and adapts to your skin tone as you blend, so there is nothing to match or mix. If your skin is very fair or deep, email us first at info@skinofab.com and we'll tell you honestly how it's likely to look. Either way, wear it in your own daylight for 30 days; if you don't love it, we'll refund you."),
        # under "There is one shade", 14 fair-to-medium swatches read as a shade chart (review 3)
        (r'RE:<div class="accordion-content-image">\s*<img alt="" loading="lazy" src="\.\./assets/img/foundation_png_1-[^"]+"[^>]*/>\s*</div>', ''),
        ("Step 1: Create the Perfect Canvas", "Step 1: Moisturizer and sunscreen first"),
        ("Start with moisturized skin. Smooth on your go-to primer or hydrating cream to create an even base that helps your foundation glide on seamlessly.",
         "Apply your usual moisturizer and your daily sunscreen. No primer needed."),
        ("Step 2: Build Your Base", "Step 2: One pump, five dots"),
        ("Dispense one pump onto the back of your hand. Using a brush, dot foundation on your forehead, cheeks, nose, and chin. Blend outward from the center of your face using circular motions for a naturally soft, medium coverage finish with a velvety matte texture.",
         "Dot one pump on your forehead, cheeks, nose and chin. It looks white. That's the point."),
        ("Step 3: Customize Your Coverage", "Step 3: Blend and watch it change"),
        ("Want more coverage in specific areas? Layer a second application on any spots that need extra attention—blemishes, redness, or discoloration—and blend seamlessly into your base.",
         "Blend outward with your fingertips or a brush. In about a minute the white turns into your skin tone, with a satin finish that doesn't need good eyesight or a magnifying mirror to get right."),
        ("Step 4: Lock It In", "Step 4: Add a second layer only where you want it"),
        ("Brighten under-eyes with your favorite concealer, then lightly dust translucent powder across your T-zone (forehead, nose, and chin) to control shine and keep your look fresh all day.",
         "Tap a little more over sun spots or redness. Skip the powder on dry areas so lines stay soft."),
        ("Revitalizing ingredients", "What's inside"),
        (">Glycerin<", ">Peptides (Matrixyl 3000)<"),
        (": Skin-loving glycerin for all-day hydration", ": smooth the look of fine lines while you wear it"),
        (">Mica<", ">PDRN + niacinamide<"),
        (": Natural mineral pigments for a soft, healthy glow", ": skincare actives for thinner, drier skin after 45"),
        (">Vitamin E<", ">Hyaluronic acid + ceramide NP<"),
        (": Nourishes and protects with skin-soothing Vitamin E", ": keep dry skin comfortable, so the finish never cracks"),
        ("Water, Titanium Dioxide, Alumina, Silica, Propylene Glycol, Ethylhexyl Palmitate, Isononyl Isononanoate, Glycerin, Peg-30 Dipolyhydroxystearate, Cetyl Peg/Ppg-10/1 Dimethicone, Triethylhexanoin, Mica, C12-15 Alkyl Benzoate, Disteardimonium Hectorite, Ci 77491, Ci 77492, Ci 77499, Tocopheryl Acetate, Phenoxyethanol, Ethylhexylglycerin, Parfum",
         "Key ingredients: Sodium Hyaluronate, Sodium Hyaluronate Crosspolymer, Ceramide NP, Squalane, Panthenol, Palmitoyl Tripeptide-1, Palmitoyl Tetrapeptide-7, Sodium DNA (PDRN, from salmon), Hydroxypropyl Tetrahydropyrantriol, Niacinamide, Adenosine, Silica, Boron Nitride, Mica, Iron Oxides. Fragrance-free. No propylene glycol, drying alcohol or parabens. The full ingredient list is printed on the box."),
        ("Our long-wear formula is designed to stay put for up to 16 hours without fading, oxidizing, or transferring onto clothes or masks. The breathable, lightweight texture locks onto skin while still feeling comfortable, so you get all-day coverage that looks as fresh at 8 PM as it did at 8 AM.",
         "It's made to stay even and comfortable through a full day, without turning orange or drying into your lines. If you're out from morning to dinner, a light touch-up on the nose and chin is usually all it needs."),
        ("Our formula is dermatologist-tested, non-comedogenic (won't clog pores), and free from harsh irritants. We've also excluded common sensitizers like parabens, sulfates, and synthetic fragrances. In fact, 88% of users in our clinical study reported improved skin texture after just 2 weeks of use—it's skincare and makeup in one.",
         "It's fragrance-free and made without propylene glycol, drying alcohol or parabens, the usual reasons thinner skin stings. As with anything new, try it on your jawline first. It contains salmon-derived DNA (PDRN): if you have a fish allergy, ask your doctor first."),
        ("Clean & cruelty free", "Fragrance-free serum base"),
        ("Vegan formula with skin-nourishing ingredients", "With peptides, PDRN and hyaluronic acid"),
    ],
}

# The offer on the product page (owner's brief, 22 Oct 2026): one product, 1 or 2 bottles, bought once or with
# automatic refills every 28 days. One source for every price on the site: setup_ccf_offers.py writes these to NEXT
# (variant price, compare-at and refill price, refill interval); apply_persona.py builds the picker and terms from
# them and writes sf-offer.json, which the theme build turns into the cart drawer's upgrade offer.
PACKS = [
    {'key': '1', 'name': '1 bottle', 'variant': '1 bottle', 'sku': 'SKF-APF-1',
     # (the export's "Temporary deal" had no end and no deal it was taken from: what the pack is, store audit 8)
     'price': '47.00', 'refill': '37.00', 'compare': '59.00', 'note': 'Free shipping, 30-day guarantee', 'gifts': []},
    {'key': '2', 'name': '2 bottles', 'variant': '2 bottles + free gifts', 'sku': 'SKF-APF-2-GIFTS',
     'price': '57.00', 'refill': '47.00', 'compare': '118.00', 'note': 'The lowest price per bottle', 'badge': 'Best value',
     'gifts': [('blender', 'FREE SKINOFAB Blender', '9.00'), ('mystery', 'FREE Mystery Gift', '15.00'), ('shipping', 'FREE Shipping', None)]},
]
# default: refills are on when the page loads (the cards show the refill prices); show_box: the "Save 37% with
# Automatic Refills" box is shown (False: hidden, so every pack bought from the product page is a refill). The terms
# under the button ("You pay $37 today, then $37 every 28 days until you cancel...") always show while refills are on.
REFILL = {'interval': 'day', 'every': 28, 'name': 'Automatic Refills', 'default': True, 'show_box': False,
          'perks': ['No Commitment', 'Cancel Anytime', 'Refills every 28 days']}

# Product page additions taken from the homepage (apply_persona.py): the dermatologist section and the customer video
# reviews, rebuilt in the product page's style. A homepage review whose story the product page already tells under
# another name is left out (the makeup artist, 53, is "Deborah, 53" in the product page reviews). The review videos
# still show the previous brand's bottle (only their posters were re-made), so the cards use the posters as photos.
PDP_REVIEW_SKIP = ['Olivia M.']
# The homepage's three video "reviews" (Amber T., Olivia M., Claire R., "Verified buyer") are creator clips re-cast
# with AI models: no such buyers are among the imported reviews, and Olivia M.'s real review says something else.
# They stay as what they are, illustrative videos of the foundation on skin, captioned in the store's own words; the
# buyers' own words are the review wall's. (title, caption) per card, in the section's order.
# the header's line on the cart page (apply_persona: the sale line is the foundation's offer)
CART_ANNOUNCEMENT = 'Free shipping on every order · 30-day money-back guarantee'

VIDEO_DEMOS = [
    ('Goes on white, turns into your tone', 'Dots on the back of the hand, blended in: the white shifts to your skin as you work it in.'),
    ('Glides over texture', 'Dotted on cheeks and forehead and buffed in: a thin layer that blends over texture instead of settling into it.'),
    # (the clip: dotted on the back of her hand, then buffed over her cheeks with a brush; no fingertip, no eye area,
    # review 6)
    ('Soft on fine lines', 'Warmed on the back of the hand, then buffed over the cheeks with a brush: one thin layer '
     'that blurs the look of fine lines.'),
]
# A card whose own clip does not show the product: another re-make in its place, (clip, poster frame in seconds), by
# card. The second card's clip (gj-88d49199) shows a glossy angled pump with no SKINOFAB wordmark, only on the back
# of the hand (review 3, 26 Oct 2026); gj-b705ce67 shows the SKINOFAB bottle at its start and end, dotted on her
# cheeks and forehead and buffed in with a brush.
VIDEO_DEMO_CLIPS = {1: ('brand/videos/gj-b705ce67.mp4', 0.3)}
VIDEO_DEMO_LABEL = 'Illustrative video · AI model'
VIDEO_DEMO_NOTE = 'Illustrative videos made with AI models, not customer reviews. Real buyers’ reviews are just below.'


# More questions for the product page FAQ (appended to its two accordion columns): the skin questions women 45+ ask,
# and how Automatic Refills work and how to buy once.
PDP_FAQ_SKIN = [
    ('Which shade do I choose?',
     "There's no shade to choose. It goes on white and adapts to your skin tone as you blend. If you don't love how it looks on you, we'll refund you within 30 days."),
    ('Will it settle into my fine lines?',
     "It's designed not to. The base is a satin serum, not a matte formula, and soft-focus powders blur the look of lines instead of filling them with pigment. For the smoothest finish, use one thin layer and skip powder on dry areas."),
    ('My skin is very dry. Will it look patchy?',
     "Dry, mature skin is who we made it for. Two forms of hyaluronic acid, ceramide NP, squalane and panthenol keep the finish comfortable, so it doesn't crack or cling to dry patches. Apply it over your usual moisturizer."),
]
def pdp_faq_orders():
    one, two = PACKS[0], PACKS[1]
    usd = lambda v: '$%d' % float(v) if float(v) == int(float(v)) else '$%.2f' % float(v)
    return [
        ('How do Automatic Refills work?',
         f"Your pack ships again every {REFILL['every']} days at the refill price: {usd(one['refill'])} for 1 bottle, "
         f"{usd(two['refill'])} for 2 bottles. We email you before every refill. To skip or cancel, just email "
         "info@skinofab.com: no minimum, no fees."),
        ('Can I buy just once?',
         f"Yes. In your bag, tap Change under the bottle, then on the cart page set it to One-time purchase before checkout: {usd(one['price'])} for 1 bottle or "
         f"{usd(two['price'])} for 2 bottles, with no refills."),
        ('Does it have SPF?',
         'No. We left SPF out on purpose so the formula can stay a light, hydrating serum. Apply your daily sunscreen first; the foundation layers on top without pilling.'),
    ]

# FrontrowMD "Clinicians' Choice" badge under the product title (Theme settings > SKINOFAB > Product Page). The
# foundation's FrontrowMD listing, product 4694, from the original store's loader; the owner runs both brands
# (confirmed 22 Oct 2026). The count, clinicians and FAQ are FrontrowMD's live data for that listing.
FRONTROW_PRODUCT_ID = 4694

# Cart drawer (Theme settings > SKINOFAB > Cart Drawer): the last step before payment is about trust and order value,
# not plan terms. Add-ons are design handles (mapped to NEXT by the catalog). The review is an imported verified review
# that the product page shows, word for word (Lora Z., reviews.json id zjPC7IPmY, the first testimonial card); the
# drawer shows it only while the foundation is in the bag. The guarantee line is every product's (refund policy).
CART = {
    'product': 'color-changing-foundation',
    # the drawer offers the first two not yet in the bag: the brush, then the balm (the new under-eye product), then the
    # firming serum
    'addons': ['the-lymphatic-brush', 'pdrn-plumping-balm', 'egf-nad-firming-serum'],
    'upgrade_title': 'Upgrade to 2 bottles + free gifts',
    'upgrade_button': 'Upgrade',
    'review_text': ("I’m 65 and my skin has uneven color. This product has evened out those places. Also, it’s the "
                    "perfect color match—never too light or orange! I’m very pleased!"),
    'review_name': 'Lora Z. · Verified buyer',
    'guarantee_text': "Try it for 30 days. If you don't love it, we'll refund you, even if it's opened.",
}

# Product gallery order on NEXT (first 10 are uploaded): the 45+ women and the "goes on white" demo up front.
# Entries are file-name prefixes from the product snapshot's image list.
GALLERY = [
    'KoreanColorChangingFoundation-Productimages_1_',   # black bottle packshot
    '2_221c6006',                                        # woman 55+ with the bottle
    '21_7a5d845a',                                       # 58, silver hair, bottle at temple (persona)
    '22_ed20463f',                                       # white dots turning into skin (persona)
    'ColorChangingFoundation-Productimagesphotos_412bfd2c',  # Adapts to your skin (persona infographic)
    '6_d0973846',                                        # What's inside
    'ColorChangingFoundation-Productimagesphotos_2_1791540a',  # results panel
    '8_87ca3242',                                        # skinofab vs. others
    '24_e2816f7f',                                       # 55, medium-deep skin (persona)
]
