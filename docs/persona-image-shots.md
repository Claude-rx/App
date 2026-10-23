# Persona image shot list

New lifestyle images for the two products, ready to generate as soon as an image route works:
- **Higgsfield cloud:** credits needed; Nano Banana 2.1 costs 2 credits per 2K image.
- **Higgsfield Studio on the 4SToken key:** its Vercel Blob store must be unsuspended first.

Generate each shot with the product reference images below, review it against the checklist, and retry until every
item passes. Then swap it into its slot (tools/persona/apply_persona.py images or brush_assets.py) and rebuild.

## The customer in every image

- Women 45 to 70: the SKINOFAB buyer. Mix of white, Black, Latina and East Asian women across the set.
- Real aging, shown kindly: fine lines, crow's feet, softer jawline, some grey hair. No airbrushing, no 25-year-old
  models, no beauty filter.
- Real places in daylight: kitchen, bathroom vanity, bedroom window, living room, car, garden.
- Photographed by someone else or on a tripod. No mirror shots, no flipped images: all text on the product reads
  normally.

## Holding the product the right way

**Adaptive Peptide Foundation**
- 30 mL matte black airless bottle with a black pump.
- White SKINOFAB wordmark printed vertically, "ADAPTIVE PEPTIDE FOUNDATION", "PDRN", "30 mL / 1.01 fl oz".
- About 11 cm tall: it fits inside one hand.
- Held upright, fingers around the lower half, thumb in front below the logo, pump on top.
- The label faces the camera and the logo is never covered.
- Or: one pump dispensed onto the fingertips, bottle in the other hand.

**The Lymphatic Brush**
- Half-moon wooden handle with brown wood grain, soft amber bristles in a curved row, clear SKINOFAB travel case.
- Held by the wooden back, bristles toward the skin.
- Swept from the center of the face outward and down toward the neck: under the eyes toward the temples, along the jaw
  toward the ear, down the neck.
- Light touch, on dry skin. No oil, no water.

**Every shot**
- Exact product: same shape, color, cap or pump, logo and label text as the references.
- Five fingers per hand.
- No extra or invented text in the image.

## References

| Product | Reference images |
|---|---|
| Foundation | https://cdn.29next.store/media/skinofab/images/products/2026/10/01-front-778e8a.jpg (front), …/03-three-quarter-right-3ce670.jpg, …/09-pump-detail-46dc44.jpg; brand/adaptive-peptide-foundation/composites/label-detail.jpg |
| Brush | brand/lymphatic-brush/card.jpg (brush and SKINOFAB case), brand/lymphatic-brush/compare-ours.jpg (in hand) |

## Shots

| # | Slot | Shot |
|---|---|---|
| F1 | Foundation gallery 2 | 58-year-old woman, silver bob, cream knit, kitchen window light. Holds the bottle at chest height, label to camera, soft smile |
| F2 | Foundation gallery 3 | Close-up of a 52-year-old woman's fingertips after one pump, white drop of foundation; bottle upright in her other hand, logo readable |
| F3 | Foundation gallery 4 | Blending on the cheek of a 61-year-old Black woman, half of the face done, visibly more even tone, bottle on the vanity behind |
| F4 | Foundation gallery 5 | 49-year-old Latina woman, bathroom vanity, bottle in hand, looking at camera (not into a mirror) |
| F5 | Homepage hero | 55-year-old woman laughing at home, natural skin, bottle held low at waist height, label readable |
| F6 | Homepage foundation section | 63-year-old East Asian woman in a garden chair, bottle in hand, calm confident look |
| F7 | Problem section | 57-year-old woman frowning at an old foundation that settled into her lines (no SKINOFAB product in this shot) |
| F8 | Solution section | Same woman, even skin, holding the SKINOFAB bottle, relaxed smile |
| F9 | Two-bottle pack | Two bottles side by side on a linen surface, a 50-something woman's hand reaching for one |
| F10 | Cart drawer / empty bag | Bottle alone, studio, soft shadow (packshot; replaces any old bottle art) |
| B1 | Brush gallery 1 (now a product-only hero, `brand/lymphatic-brush/hero.jpg`) | 54-year-old woman sweeping the brush from under her eye toward her temple, eyes closed, morning light, case on the counter |
| B2 | Brush gallery 2, new slot after the hero (jaw) | 60-year-old woman sweeping along the jaw toward the ear |
| B3 | Brush gallery 3, new slot (neck); also the routine section's poster | 52-year-old woman sweeping down the neck toward the collarbone |
| B4 | Brush homepage card | Brush resting on its open SKINOFAB case on a bathroom shelf, soft daylight |
| B5 | Brush + foundation | Morning routine flat lay: brush, case and foundation bottle, both logos readable |

## Review before swapping

- [ ] The face is 45 or older and looks like a real person.
- [ ] Skin texture is natural, not plastic.
- [ ] The product matches the references exactly: shape, color, pump or case, logo, label.
- [ ] The product is held as described above.
- [ ] Hands are correct: five fingers, natural grip.
- [ ] No mirror, no flipped text, no added text.
- [ ] The crop works at the slot's aspect ratio, on desktop and on mobile.

## Home hero (4K, from the approved photo)

The home slide's photo (woman with the foundation, `skinofab-color-changing-foundation-hero-4096w-*.jpg` in the
persona image set) existed only at 2000 x 853. The layout draws it far wider than the screen: 349vw on phones (a 3x
phone needs ~4,100 px across it) and 150vw on desktops. Only 1800 px reached browsers, so phones stretched it
about 3.6 times. With no credits and the Studio's storage suspended, it was rebuilt locally from the same photo:

1. **Upscale 4x** on the CPU (`tools/persona/upscale.py`), with two models blended: 4x_NMKD-Siax_200k (lashes, hair, real
   skin texture) and RealESRGAN_x4plus (calmer skin, so the upscale doesn't deepen her lines).
2. **Real label** (`tools/persona/hero_label.py`): the AI product swap had garbled the small print ("PEPTIOE", and
   "PDRN" read like another word). That was barely visible when blurry and impossible to miss once sharp. The old
   print is erased and the label of the real front render (`skf-apf-01-front.jpg`) is drawn on the bottle, fitted
   to its 4.25° tilt and to the old wordmark's size.
3. **Master** at 4096 px, saved in the persona image set under the same name. `apply_persona.py faster_home` cuts it
   into a phone file and a desktop file. Each keeps the part its layout shows (phones 64–92% of the width, desktops
   the right two thirds) and flattens the rest, which is never on screen. The CDN serves each screen its width
   (`optimize_theme.py` steps up to 3600 px).

```bash
S=<work dir>; sr=$S/srenv/bin/python
$sr tools/persona/upscale.py 4x_NMKD-Siax_200k.pth hero-2000.jpg siax.png
$sr tools/persona/upscale.py RealESRGAN_x4plus.pth hero-2000.jpg resrgan.png
$sr tools/persona/upscale.py --blend siax.png resrgan.png 0.4 blend.png
python3 -I tools/persona/hero_label.py blend.png skf-apf-01-front.jpg labelled.png
# then: resize to 4096 px wide, save as the persona hero file (JPEG q92), run tools/build_store.sh
```

When an image route works again, a fresh 4K shot (Nano Banana Pro at 21:9, 4K) can replace it. Keep the same
framing: face in the right third, bottle in the left hand, the left third free for the headline.
