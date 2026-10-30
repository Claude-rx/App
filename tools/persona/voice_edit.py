"""Change or remove words in a video's soundtrack, in the speaker's own voice, on the video's own timeline.

New words are spoken by Chatterbox (Resemble AI, MIT licence, so fine in an ad) cloning the speaker from a clean stretch
of her own speech in the same video. It says a whole sentence (--say), so the words get the intonation they have in
it; only the new words (--take) are cut from it, fitted to the slot of the words they replace (rubberband, keeping the
pitch), optionally set to their loudness and pitch, and crossfaded in at quiet points. Everything else in the
soundtrack stays the original, sample for sample, and nothing moves: lips and cuts after the edit still line up.

usage: <venv>/bin/python voice_edit.py <video or audio> <out.wav> --ref r0,r1[,r2,r3...] --say "<sentence>"
                                       --take "<new words>" --edit e0,e1 [--seeds 1,2,3] [--match-level] [--match-pitch]
                                       [--cfg 0.5] [--exaggeration 0.5] [--reuse]
       <venv>/bin/python voice_edit.py <video or audio> <out.wav> --mute e0,e1 --tone t0,t1
- ref: the speaker's own speech to clone (pairs of seconds, joined; about 10 s of her talking, no other sound)
- edit: the span of the words to replace, from a quiet point to a quiet point; the new words fill it from 10 ms after
  its start to 30 ms before its end
- --cfg, --exaggeration: Chatterbox's pacing and expressiveness (0.3 for a quick talker, as its makers advise)
- --match-level: the new words get the speech level of the words they replace (their 20 ms frames within 25 dB of the
  loudest, so pauses don't count), within 6 dB; --match-pitch: their median pitch, within 3 semitones
- each seed is a take, written as <out stem>-s<seed>.wav and read back by faster-whisper (the 4 s around the edit);
  of the takes that read as --take (90 % alike or more), the one copied to out.wav has the old words' intonation
  (the shape of their pitch over time, Praat's tracker, in semitones around its median: a falling end stays falling)
  and was changed least (stretch and pitch shift); all three are costs in semitones' worth of log ratio. Every take's
  reading is printed, so a person can listen and pick another; --reuse scores the takes already made again
- mute: the words in e0,e1 are taken out and the span filled with the room's own quiet, from t0,t1 (a pause), looped
- out.wav: the whole soundtrack at the source's rate and channels (new words are mono, in every channel)
needs: torch + torchaudio (CPU wheels), chatterbox-tts, faster-whisper, praat-parselmouth, ffmpeg with rubberband
(tools/persona/setup_voice_tools.sh builds it); Chatterbox's English weights (3.2 GB) from Hugging Face on first use
"""
import difflib, re, shutil, subprocess, sys
from pathlib import Path
import numpy as np

SRC, OUT = sys.argv[1], Path(sys.argv[2])
args = sys.argv[3:]
opt = lambda k, d=None: args[args.index(k) + 1] if k in args else d
secs = lambda k: [float(v) for v in opt(k).split(',')]
FADE, LEAD, TAIL = 0.02, 0.01, 0.03


def probe(entries):
    return subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'a:0', '-show_entries', f'stream={entries}',
                           '-of', 'csv=p=0', SRC], check=True, capture_output=True, text=True).stdout.strip().split(',')


SR, CH = (int(v) for v in probe('sample_rate,channels'))


def pcm(path, sr, ch):
    cmd = ['ffmpeg', '-v', 'error', '-i', str(path), '-vn', '-ac', str(ch), '-ar', str(sr), '-f', 'f32le', '-']
    return np.frombuffer(subprocess.run(cmd, check=True, capture_output=True).stdout, np.float32).reshape(-1, ch)


def ff(x, sr_in, sr_out, af=None):
    """Run mono float samples through ffmpeg: resample, and the audio filter af if given."""
    flt = (af + ',' if af else '') + f'aresample={sr_out}:resampler=soxr'
    p = subprocess.run(['ffmpeg', '-v', 'error', '-f', 'f32le', '-ar', str(sr_in), '-ac', '1', '-i', '-', '-af', flt,
                        '-f', 'f32le', '-'], input=np.ascontiguousarray(x, np.float32).tobytes(), check=True, capture_output=True)
    return np.frombuffer(p.stdout, np.float32)


def write_wav(path, a, sr):
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(sr), '-ac', str(a.shape[1]), '-i', '-',
                    '-c:a', 'pcm_s16le', str(path)], input=np.ascontiguousarray(a, np.float32).tobytes(), check=True)


def speech_db(x, sr):
    """The level of the speech in x: the mean of its 20 ms frames within 25 dB of the loudest (pauses left out)."""
    n = int(0.02 * sr); k = len(x) // n
    fr = 20 * np.log10(np.sqrt((x[:k * n].reshape(k, n) ** 2).mean(1)) + 1e-9)
    return float(fr[fr > fr.max() - 25].mean())


def pitch(x, sr):
    """The median pitch of x (Hz) and its shape: the voiced frames' pitch in semitones around that median, at 20
    points spread over the voiced part (Praat's autocorrelation tracker, 20 ms frames, 110-420 Hz)."""
    import parselmouth
    f = parselmouth.Sound(x.astype(np.float64), sr).to_pitch_ac(time_step=0.02, pitch_floor=110, pitch_ceiling=420,
                                                               very_accurate=True).selected_array['frequency']
    v = f[f > 0]
    if len(v) < 4: return float('nan'), np.zeros(20)
    med = float(np.median(v)); st = 12 * np.log2(v / med)
    return med, np.interp(np.linspace(0, len(st) - 1, 20), np.arange(len(st)), st)


def splice(out, seg, e0):
    """Fade seg (it starts FADE before e0 and ends FADE after its span) into every channel of out."""
    f = int(FADE * SR); a = int(round(e0 * SR)) - f
    w = np.ones(len(seg), np.float32); w[:2 * f] = np.linspace(0, 1, 2 * f); w[-2 * f:] = np.linspace(1, 0, 2 * f)
    out[a:a + len(seg)] = out[a:a + len(seg)] * (1 - w)[:, None] + (seg * w)[:, None]


orig = pcm(SRC, SR, CH)
mono = orig.mean(1)

# ------------------------------------------------------------------ take words out, leave the room's quiet
if '--mute' in args:
    e0, e1 = secs('--mute'); t0, t1 = secs('--tone')
    tone = mono[int(t0 * SR):int(t1 * SR)]
    n, x = int((e1 - e0 + 2 * FADE) * SR), int(0.05 * SR)            # loop the pause with 50 ms crossfades
    fill = tone.copy()
    while len(fill) < n:
        r = np.linspace(0, 1, x, dtype=np.float32)
        fill = np.concatenate([fill[:-x], fill[-x:] * (1 - r) + tone[:x] * r, tone[x:]])
    out = orig.copy(); splice(out, fill[:n], e0); write_wav(OUT, out, SR)
    print(f'{OUT}: {e0:.2f}-{e1:.2f} s taken out, filled with the quiet of {t0:.2f}-{t1:.2f} s '
          f'({speech_db(tone, SR):.0f} dB)')
    sys.exit()

# ------------------------------------------------------------------ new words in her voice
import torch, torchaudio
from chatterbox.tts import ChatterboxTTS
from faster_whisper import WhisperModel

R = secs('--ref'); SAY, TAKE = opt('--say'), opt('--take')
E0, E1 = secs('--edit'); SEEDS = [int(v) for v in opt('--seeds', '1').split(',')]
ref = np.concatenate([mono[int(a * SR):int(b * SR)] for a, b in zip(R[::2], R[1::2])])
ref_path = OUT.with_name(f'{OUT.stem}-ref.wav'); write_wav(ref_path, ref[:, None], SR)
tts = ChatterboxTTS.from_pretrained(device='cpu')
asr = WhisperModel('small', device='cpu', compute_type='int8')
norm = lambda s: re.sub(r'[^a-z]', '', s.lower())
old_pitch, old_shape = pitch(mono[int(E0 * SR):int(E1 * SR)], SR)
old_level = speech_db(mono[int(E0 * SR):int(E1 * SR)], SR)
slot = E1 - E0 - LEAD - TAIL


def words_span(wave, sr):
    """Where --take is in some speech: how much whisper's best run of words reads like it, that run (start, end in
    seconds) and all that whisper heard."""
    segs, _ = asr.transcribe(ff(wave, sr, 16000), language='en', beam_size=5, word_timestamps=True)
    ws = [w for s in segs for w in s.words]
    best = (0, None, ''.join(w.word for w in ws).strip())
    for i in range(len(ws)):
        for j in range(i, min(i + 4, len(ws))):
            r = difflib.SequenceMatcher(None, norm(''.join(w.word for w in ws[i:j + 1])), norm(TAKE)).ratio()
            if r > best[0]: best = (r, (ws[i].start, ws[j].end), best[2])
    return best


def trim(x, sr, t0, t1):
    """The words whisper put at t0-t1: from the quietest 5 ms between 60 ms before and 30 ms after t0 (the seam with
    the word before, which must not come along), to where the sound has faded 35 dB under its peak after t1."""
    n = int(0.005 * sr)
    db = lambda i: 20 * np.log10(np.sqrt(np.mean(x[i:i + n] ** 2)) + 1e-9)
    a = min(range(int(max(0, t0 - 0.06) * sr), int((t0 + 0.03) * sr), n), key=db)
    peak = max(db(i) for i in range(a, int(t1 * sr), n))
    b, stop = int(t1 * sr), min(len(x) - n, int((t1 + 0.15) * sr))
    while b < stop and db(b) > peak - 35: b += n
    return x[a:b]


results = []
for seed in SEEDS:
    said_path = OUT.with_name(f'{OUT.stem}-say-s{seed}.wav')
    if '--reuse' in args and said_path.exists():
        wav = torchaudio.load(str(said_path))[0][0].numpy()
    else:
        torch.manual_seed(seed)
        wav = tts.generate(SAY, audio_prompt_path=str(ref_path), cfg_weight=float(opt('--cfg', 0.5)),
                           exaggeration=float(opt('--exaggeration', 0.5))).squeeze(0).numpy()
        torchaudio.save(str(said_path), torch.from_numpy(wav)[None], tts.sr)
    _, span, said = words_span(wav, tts.sr)
    if span is None: print(f'seed {seed}: "{TAKE}" not found in "{said}"'); continue
    w = trim(wav, tts.sr, *span)
    k = slot / (len(w) / tts.sr)                                     # rubberband: length to the slot, pitch kept
    af = f'rubberband=tempo={1 / k:.5f}:pitch=1:transients=smooth:formant=preserved'
    p_new, _ = pitch(w, tts.sr); shift = 0.0
    if '--match-pitch' in args and np.isfinite(p_new) and np.isfinite(old_pitch):
        shift = float(np.clip(12 * np.log2(old_pitch / p_new), -3, 3))
        af = af.replace('pitch=1', f'pitch={2 ** (shift / 12):.5f}')
    word = ff(w, tts.sr, SR, af)[:int(slot * SR)]
    if '--match-level' in args: word = word * 10 ** (float(np.clip(old_level - speech_db(word, SR), -6, 6)) / 20)
    f = int(FADE * SR)
    seg = np.concatenate([np.zeros(f + int(LEAD * SR), np.float32), word,
                          np.zeros(int(round((E1 - E0) * SR)) - int(LEAD * SR) - len(word) + f, np.float32)])
    out = orig.copy(); splice(out, seg, E0)
    path = OUT.with_name(f'{OUT.stem}-s{seed}.wav'); write_wav(path, out, SR)
    c0, c1 = int(max(0, E0 - 2) * SR), int((E1 + 2) * SR)
    score, _, heard = words_span(out[c0:c1].mean(1), SR)
    p_out, shape = pitch(word, SR)
    away = float(np.sqrt(np.mean((shape - old_shape) ** 2)))
    print(f'seed {seed}: "{heard}" ({score:.2f} like "{TAKE}"); word {len(w) / tts.sr:.2f} s -> {slot:.2f} s, '
          f'pitch {p_new:.0f} -> {p_out:.0f} Hz (old words {old_pitch:.0f} Hz; shift {shift:+.1f} st), intonation '
          f'{away:.1f} st from the old words\' -> {path.name}', flush=True)
    st = np.log(2) / 12
    results.append((score >= 0.9, -(abs(np.log(k)) + abs(shift) * st + away * st), path))
best = max(results)
shutil.copy2(best[2], OUT)
print(f'{OUT}: {best[2].name}')
