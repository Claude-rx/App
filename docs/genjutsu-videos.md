# The homepage videos: SKINOFAB's bottle in place of the old one

Seven of the homepage's eight videos showed the old pink SMOOCHE foundation. In each, Higgsfield Genjutsu (object swap,
720p) replaced it with the Adaptive Peptide Foundation bottle from the owner's product sheet
(`skinofab-product-sheet-text-and-size.pdf`, 21 Oct 2026): the matte black cylinder, 103 × 32.5 mm (3.17 : 1), flat top
with the pump slot and nozzle ring, the vertical SKINOFAB wordmark (S at the top) and only ADAPTIVE PEPTIDE FOUNDATION /
PDRN / 30 mL / 1.01 fl oz under it. The women, their hands, the rooms, the camera and the soundtrack are the originals'.
The eighth video (a bag of lip products, no foundation) is unchanged.

## The seven videos

| Video (source file prefix) | Length | What changed |
|---|---|---|
| `b705ce67` blonde woman, grey robe | 10.0 s | the bottle in every frame; at the pump close-up (about 1 s) the top keeps the old bottle's rounded shape in black |
| `41b77ec4` woman in black, brushes | 21.5 s | the bottle in every frame; at the end (19.2 s on) she held the bottle and its pink SMOOCHE box: that shot was re-made so she holds two SKINOFAB bottles (the 2-bottle pack), spliced in at the cut |
| `43e0f648` blonde woman, navy top | 60.3 s | the bottle in the first and last 20 s (Genjutsu parts, joined frame-exact); the middle 20 s shows no bottle and is the original, because Genjutsu had also wiped the white foundation dots off her face there (the "goes on white, adapts to your skin" demo). Her voice: she says "This is by SKINOFAB", not "Smooch", her lips moving with it, and the sentence "It contains vitamin E and SPF 15" is taken out (below) |
| `88d49199` silver-haired woman | 22.5 s | the bottle in every frame |
| `de65acac` dark-haired woman, striped shirt | 8.2 s | the bottle in every frame; Genjutsu also made her pink lip pencil black |
| `f8efa52f` dark-haired woman, cream cardigan | 11.6 s | the bottle in every frame; Genjutsu also made her white lip gloss black |
| `2ff54da7` woman in a tank top | 10.7 s → 9.7 s | Higgsfield's content filter rejected this clip five times (whole, cropped, tightly cropped), so the first second, the only one showing the old pink tube, is cut; the burned-in "SMOOCHE" caption is replaced with "SKINOFAB" frame by frame (`caption_swap.py`), fading in like the original |

The lip pencil and lip gloss are the old range's products (no longer sold); in black they carry no old branding.

## Her voice in the 60 s video (`43e0f648`)

| When | She said | Now |
|---|---|---|
| 6.27–7.07 s, to camera | "This is by Smooch." | "This is by SKINOFAB." (said skin-o-fab), in her own voice, her lips moving with it |
| 32.61–35.60 s, voiceover while she applies it (lips closed) | "It contains vitamin E and SPF 15." | taken out: the foundation has no SPF (the FAQ says so), so the sentence was false for it. The 3 s are the room's own quiet |

The rest of the soundtrack is the original, sample for sample, and nothing moved: the video is 60.309 s as before,
every later word and lip movement where it was. The other videos with speech (`41b77ec4`) name no brand and claim no
SPF; the rest are music.

1. **Voice** (`tools/persona/voice_edit.py`): Chatterbox clones her voice from 10.6 s of her own speech in the video
   (0–5.55 s, 7.30–12.60 s) and says "This is by Skin-o-fab." in six takes. The tool cuts the name out of each, fits it
   to the old word's slot (6.27–7.23 s: from the old "S" to just before her next word, which starts at 7.30 s;
   rubberband, the pitch kept), gives it the old word's loudness and pitch, and crossfades it in over 20 ms. Five takes
   read back (Whisper) as the name; the tool keeps the one whose intonation is closest to hers: take 3, high on
   "Skin" and falling to a low "fab" (242 → 165 Hz) as her "Smooch" did (226 → 162 Hz), stretched by 7 % (0.90 s to 0.96 s).
   `--mute` takes the SPF sentence out and loops the pause after it (−61 dB) in its place.
2. **Lips** (LatentSync 1.5 on the CPU): her mouth re-made for the new word from a 1.28 s clip (6.04–7.32 s) and the
   new soundtrack. `tools/persona/mouth_patch.py` puts it back on the original 30 fps frames between 6.20 and 7.28 s:
   each frame takes the lower face (under the nose, inside the jawline, feathered) of the synced frame for its moment
   in the sound, moved onto its own face by the eyes and nose (LatentSync works at 25 fps), fading in and out over
   0.08 s. The rest of every frame is the original.
3. **Checks**: Whisper reads the finished video back word for word as before, except "This is by SkinnoFab" and
   without the SPF sentence; the name is at the old word's level (−33.8 against −34.0 dB). Her mouth before and after:
   `docs/screenshots/video3-brand-word-lips.jpg`. Listen: `docs/audio/video3-voice-before-after.mp3` (each line
   before, then after).

Both models allow commercial use: Chatterbox is MIT (it marks what it makes with Resemble's inaudible Perth
watermark), LatentSync is Apache-2.0 code with OpenRAIL++ weights. F5-TTS was tried first and dropped: its weights are
CC-BY-NC. `tools/persona/setup_voice_tools.sh <dir>` builds both on a CPU-only machine (LatentSync patched to run
without a GPU). Cost: no credits; about 40 minutes of CPU, 25 of them for the lips. The words are said in a real
creator's voice: her agreement should cover edits of her voice and likeness before the video runs in paid ads.

## How it was made

1. **References**: the product sheet's views (front, both three-quarters, pump close-up, the label text at 4×, top,
   rear), in `brand/adaptive-peptide-foundation/sheet/`, served from the theme CDN as `skf-sheet-*.jpg`.
2. **Genjutsu** through the owner's Higgsfield Studio (`genjutsu`, object swap, 720p), the prompt in
   `tools/persona/queue/genjutsu-queue.json`. Videos over 28 s are cut into equal parts.
3. **Checks** (`tools/theme-qa/video_swap_sheet.py`): a before/after sheet of every result at the same moments, and the
   timing drift. Genjutsu returns 24 fps and runs 0.5–3 % fast (a 10 s clip comes back 9.7 s long), so lips drift up
   to 0.3 s from the soundtrack by the end.
4. **Repairs**: `tools/persona/video_patch.py` splices a re-made stretch back in on the source's timeline (whole
   frames after a cut, or a feathered region); `tools/persona/caption_swap.py` replaces a burned-in caption;
   `tools/persona/voice_edit.py` and `tools/persona/mouth_patch.py` change spoken words (above).
5. **Publishing**: `genjutsu_direct.py <queue> skinofab-theme <work_dir> --results results.json` takes the results
   (whole videos, parts, or finished files marked `"final": true`), joins parts, stretches each video back to its
   source's exact length (lip sync within one frame), lays the original soundtrack on, keeps them in
   `brand/videos/`, maps them in `tools/persona/queue/video-swaps.json` (which the build uses from then on) and
   pushes them with the homepage pointing at them.

## Checks

Before/after from the live files: `docs/screenshots/genjutsu-before-after.jpg`. Every published video is the source's
exact length with its original soundtrack, and the drift check finds the picture within one frame of the sound from
start to end. A rebuild (`tools/build_store.sh`) reproduces the same video files and homepage, from
`tools/persona/queue/video-swaps.json`.

## Cost

Higgsfield list price, 720p ($0.681 per second of input video, before the account's discount): about $106 in all, for
the seven videos, a second take of `b705ce67` ($7.49, not used: it turned her pink brush black) and the 41b77ec4 ending
($3.41). The content-filter rejections were not charged; the studio stalled on the 60 s video's second part, so it was
cancelled after its first part and the other two parts were run directly.
