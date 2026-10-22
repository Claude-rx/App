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

GLOBAL = [
    # SPF: the foundation carries no SPF claim (report 11). Sentences first, then the bare chips.
    ("The Color Changing Foundation is what I recommend most to patients over forty. It adapts to her tone, it has SPF, and it doesn't turn orange or sink into fine lines.",
     "The Color Changing Foundation is what I recommend most to patients over forty. It adapts to her tone, it hydrates instead of drying, and it doesn't turn orange or sink into fine lines."),
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
]

PAGE = {
    'index.html': [
        # meta description + og:description (the theme uses it while Settings > SEO has no store description)
        ("Cosmetics made to glow, feel skinofab.",
         "Adaptive Peptide Foundation: the color-adapting serum foundation made for skin after 45. Goes on white, turns into your skin tone. Free shipping, 30-day money-back guarantee."),
        ("Foundation that adapts to you", "Stop guessing your shade after 45"),
        ("Adapts flawlessly to your unique skin tone, blurring blemishes, redness, and fine lines in seconds.",
         "It goes on white and turns into your skin as you blend. A hydrating serum foundation with peptides and PDRN that won't settle into your lines."),
        (">Look visibly younger<", ">Made for 45+<"),
        ("One shade that finds yours", "One shade. No more guessing."),
        ("Our color-adapting foundation shifts to match your skin tone the moment it touches your skin, then settles into a smooth, natural finish that doesn't sit in fine lines or cake as the day goes on.",
         "There's no shade to choose. As you blend, the color adapts to your tone, so sun spots, redness and a sallow cast even out without a white cast or an orange edge. The satin serum base stays comfortable on dry skin and doesn't sink into fine lines, even on a long day or a close-up video call."),
        ("Made for mature skin, it's lightweight, hydrating and forgiving, so you look like yourself, just fresher.",
         "Made for skin after 45: fragrance-free, with peptides, PDRN and hyaluronic acid. Fingertips only, about a minute, and you look like yourself, just fresher."),
    ],
    'products/color-changing-foundation.html': [
        # ingredient carousel: photo alt, heading and line change together
        (r'RE:alt="SPF\ 15"', 'alt="Peptides + PDRN"'),
        (r'RE:(<h3[^>]*>)\s*SPF\ 15\s*(</h3>\s*<p[^>]*>)\s*Helps\ protect\ skin\ from\ everyday\ UV\ exposure\s*(?=</p>)', r'\g<1>Peptides + PDRN\g<2>Matrixyl 3000 peptides, PDRN and Pro-Xylane: skincare for thinner skin after 45, not just color on top'),
        (r'RE:alt="Glycerin"', 'alt="Hyaluronic acid + ceramide NP"'),
        (r'RE:(<h3[^>]*>)\s*Glycerin\s*(</h3>\s*<p[^>]*>)\s*This\ ingredient\ helps\ skin\ feel\ hydrated\ and\ comfortable\.\s*(?=</p>)', r'\g<1>Hyaluronic acid + ceramide NP\g<2>Two forms of hyaluronic acid with ceramide NP, squalane and panthenol keep dry skin comfortable all day'),
        (r'RE:alt="Color\ Changing\ Pigments"', 'alt="Color-adapting pigments"'),
        (r'RE:(<h3[^>]*>)\s*Color\ Changing\ Pigments\s*(</h3>\s*<p[^>]*>)\s*Adapt\ to\ your\ skin\ tone\ as\ you\ blend\s*(?=</p>)', r'\g<1>Color-adapting pigments\g<2>Go on white and shift to your tone as you blend'),
        (r'RE:alt="Natural\-looking\ coverage"', 'alt="Soft-focus powders"'),
        (r'RE:(<h3[^>]*>)\s*Natural\-looking\ coverage\s*(</h3>\s*<p[^>]*>)\s*Evens\ out\ your\ complexion\ and\ helps\ fine\ lines\ look\ less\ noticeable\s*(?=</p>)', r'\g<1>Soft-focus powders\g<2>Silica and boron nitride blur the look of lines and pores without a dry, matte finish'),
        (r'RE:alt="Mica"', 'alt="Fragrance-free"'),
        (r'RE:(<h3[^>]*>)\s*Mica\s*(</h3>\s*<p[^>]*>)\s*Natural\ mineral\ pigments\ for\ a\ soft,\ healthy\ glow\.\s*(?=</p>)', r'\g<1>Fragrance-free\g<2>No fragrance, propylene glycol, drying alcohol or parabens, so thinner skin doesn\'t sting'),
        ("The viral skin tone adapting foundation", "The color-adapting serum foundation made for skin after 45"),
        ("Hides imperfections", "Won't settle into lines"),
        ("Say goodbye to shade-matching struggles. This color-changing foundation adapts flawlessly to your unique skin tone, blurring blemishes, redness, and fine lines in seconds.",
         "Stop guessing your shade after 45. It goes on white and turns into your skin as you blend, evening out spots and redness and softening the look of fine lines in about a minute. A hydrating serum base with peptides and PDRN means it doesn't dry you out or settle into your lines."),
        ("Try it worry-free. If our skin-adapting foundation doesn't blend seamlessly with your tone, you'll get your money back*",
         "Wear it in your own daylight for 30 days. If you don't love it, we'll refund you.*"),
        ("One shade, verified range", "One adaptive shade"),
        ("Simpler shade selection within fair-to-medium",
         "Goes on white and adapts to your tone, so there is no shade to pick"),
        ("Skin-like finish designed for mature-skin preparation", "Satin, skin-like finish made for dry, lined skin after 45"),
        ("Our adaptive pigment formula removes the need to choose a shade. As you blend, micro-encapsulated pigments react to your skin’s warmth and undertones, shifting within seconds to match your unique complexion. Made for fair to medium tones, it evens redness, blurs imperfections, and melts into the skin for a seamless, second-skin finish.",
         "Most color-changing foundations are a basic, drying base with fragrance and nothing in it for your skin. Ours is a serum. Hyaluronic acid, ceramide NP, squalane and panthenol keep dry skin comfortable; peptides (Matrixyl 3000), PDRN and Pro-Xylane are there for the skin underneath; soft-focus powders blur the look of lines and pores. Adaptive pigments go on white and shift to your tone as you blend, inside the base you choose."),
        ("Our Color Changing Foundation is suitable for all skin tones above and in between.",
         "There is one shade. It goes on white and adapts to your skin tone as you blend, so there is nothing to match or mix. Wear it in your own daylight for 30 days; if you don't love it, we'll refund you."),
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
        (">Mica<", ">PDRN + Pro-Xylane<"),
        (": Natural mineral pigments for a soft, healthy glow", ": skincare actives for thinner, drier skin after 45"),
        (">Vitamin E<", ">Hyaluronic acid + ceramide NP<"),
        (": Nourishes and protects with skin-soothing Vitamin E", ": keep dry skin comfortable, so the finish never cracks"),
        ("Water, Titanium Dioxide, Alumina, Silica, Propylene Glycol, Ethylhexyl Palmitate, Isononyl Isononanoate, Glycerin, Peg-30 Dipolyhydroxystearate, Cetyl Peg/Ppg-10/1 Dimethicone, Triethylhexanoin, Mica, C12-15 Alkyl Benzoate, Disteardimonium Hectorite, Ci 77491, Ci 77492, Ci 77499, Tocopheryl Acetate, Phenoxyethanol, Ethylhexylglycerin, Parfum",
         "Key ingredients: Sodium Hyaluronate, Sodium Hyaluronate Crosspolymer, Ceramide NP, Squalane, Panthenol, Palmitoyl Tripeptide-1, Palmitoyl Tetrapeptide-7, Sodium DNA (PDRN), Hydroxypropyl Tetrahydropyrantriol (Pro-Xylane), Niacinamide, Adenosine, Silica, Boron Nitride, Mica, Iron Oxides. Fragrance-free. No propylene glycol, drying alcohol or parabens. The full ingredient list is printed on the box."),
        ("Our long-wear formula is designed to stay put for up to 16 hours without fading, oxidizing, or transferring onto clothes or masks. The breathable, lightweight texture locks onto skin while still feeling comfortable, so you get all-day coverage that looks as fresh at 8 PM as it did at 8 AM.",
         "It's made to stay even and comfortable through a full day, without turning orange or drying into your lines. If you're out from morning to dinner, a light touch-up on the nose and chin is usually all it needs."),
        ("Our formula is dermatologist-tested, non-comedogenic (won't clog pores), and free from harsh irritants. We've also excluded common sensitizers like parabens, sulfates, and synthetic fragrances. In fact, 88% of users in our clinical study reported improved skin texture after just 2 weeks of use—it's skincare and makeup in one.",
         "It's fragrance-free and made without propylene glycol, drying alcohol or parabens, the usual reasons thinner skin stings. As with anything new, try it on your jawline first."),
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
     'price': '47.00', 'refill': '37.00', 'compare': '59.00', 'note': 'Temporary deal', 'gifts': []},
    {'key': '2', 'name': '2 bottles', 'variant': '2 bottles + free gifts', 'sku': 'SKF-APF-2-GIFTS',
     'price': '57.00', 'refill': '47.00', 'compare': '118.00', 'note': 'Temporary deal', 'badge': 'Best value',
     'gifts': [('blender', 'FREE Skinofab Blender', '9.00'), ('mystery', 'FREE Mystery Gift', '15.00'), ('shipping', 'FREE Shipping', None)]},
]
# default: refills are on when the page loads (the cards show the refill prices); show_box: the "Save 37% with
# Automatic Refills" box is shown (False: hidden, so every pack bought from the product page is a refill). The terms
# under the button ("You pay $37 today, then $37 every 28 days until you cancel...") always show while refills are on.
REFILL = {'interval': 'day', 'every': 28, 'name': 'Automatic Refills', 'default': True, 'show_box': False,
          'perks': ['No Commitment', 'Cancel Anytime', 'Refills every 28 days']}

# Cart drawer (Theme settings > SKINOFAB > Cart Drawer): the last step before payment is about trust and order value,
# not plan terms. Add-ons are design handles (mapped to NEXT by the catalog); the review is one the product page shows.
CART = {
    'product': 'color-changing-foundation',
    'addons': ['reverse-time-peptide-serum', 'under-eye-reset'],
    'upgrade_title': 'Upgrade to 2 bottles + free gifts',
    'upgrade_button': 'Upgrade',
    'review_text': ("I'm 53 and I've never found one that works this well on mature skin—including my own. "
                    "The way it glides over texture instead of settling into it is remarkable."),
    'review_name': 'Deborah, 53 · Verified purchase',
}

# Product gallery order on NEXT (first 10 are uploaded): the 45+ women and the "goes on white" demo up front.
# Entries are file-name prefixes from the product snapshot's image list.
GALLERY = [
    'KoreanColorChangingFoundation-Productimages_1_',   # black bottle packshot
    '2_221c6006',                                        # woman 55+ with the bottle
    '21_7a5d845a',                                       # 58, silver hair, bottle at temple (persona)
    '22_ed20463f',                                       # white dots turning into skin (persona)
    'ColorChangingFoundation-Productimagesphotos_412bfd2c',  # Adapts to your skin (persona infographic)
    'ColorChangingFoundation-Productimagesphotos_5',     # daylight before / after
    '6_d0973846',                                        # What's inside
    'ColorChangingFoundation-Productimagesphotos_2_1791540a',  # results panel
    '8_87ca3242',                                        # skinofab vs. others
    '24_e2816f7f',                                       # 55, medium-deep skin (persona)
]
