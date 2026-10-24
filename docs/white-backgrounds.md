# One white for every product

Every product's photos sit on pure white (#FFFFFF), the page's own background, so the four product pages share one
look: the Adaptive Peptide Foundation, the Lymphatic Brush, the PDRN Plumping Balm and the EGF + NAD+ Firming Serum.
`tools/persona/white_bg.py` does it, three ways:

| Mode | For | How |
|---|---|---|
| `light` | Photos already on white or a pale backdrop (the generated photos, the brush's cream panels) | The backdrop's level is read from the image border; near-neutral pixels from just under it up go to white along a smooth ramp. Skin (warm) and silver hair or a white top (darker than the backdrop) keep their shading; a photo with no pale backdrop (a close-up, a bathroom scene) is left as it is |
| `flood` | A packshot on a grey sweep (the foundation's main photo) | The smooth, low-saturation area connected to the border goes white with a feathered edge; the floor shadow is kept, lighter |
| `matte` | Silver hair on a grey wall, a render on a grey gradient | A segmentation model (ISNet through rembg; the model downloads once into `~/.u2net`) gives the subject's alpha; each near-neutral pixel is lifted by (1 − alpha) × (255 − the local backdrop), so hair strands lift only as much as they are see-through and skin is never lifted, even where the model misses it. Products standing on a floor get a soft contact shadow each |

Where it runs:

- **Brush:** `brush_assets.py` saves every image through `light` (the cream #F5F4F0 becomes white), except the two
  in-hand comparison photos, whose backdrop is a real floor.
- **Balm and serum:** `product_photos.py` reads every source photo through `light` before laying it out; the serum's
  labelled photos are made white once, right after the label goes on. The results grid's backdrop is white.
  Section crops taken straight from `source/` go through `light` too (`apply_persona.crop_to(white=True)`).
- **Foundation:** `apply_persona.white_backdrops()` makes every page's copy of the gallery and section photos white by
  its own pixels (the `WHITE` table: `flood` for the packshot, `matte` for the women on grey walls, `light` for the
  panels already near white), cached in `<work_dir>/white-cache`. The problem / solution photos go through `matte`
  (`section_image`). The two black panels are rebuilt on white: "Adapts To Your Skin" keeps its type, inverted to ink
  (`ink_panel`), beside the photo with its wall made white; "skinofab vs. others" is the same board as the other
  products' (`product_photos.py foundation`), with a blank generic bottle instead of the other brand's.
  Kept as shot: the daylight before/after (a real room) and the skin close-ups.
- **Homepage cards** (the shelf, Essentials, Bundle & Save): every card image on a pale grey goes through `matte` with
  `flat=True` (lifted by the backdrop's own colour, so each product's soft shadow stays, lighter).
- **NEXT galleries** (cart and checkout thumbnails): the brush's, balm's and serum's are their white images; the
  foundation's is `brand/adaptive-peptide-foundation/next/` (`product_photos.py foundation`).

```bash
pip install rembg                    # once; the ISNet model (~180 MB) downloads on first use
python3 -I tools/persona/white_bg.py <in> <out> [light|flood|matte]
```
