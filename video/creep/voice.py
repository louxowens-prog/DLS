"""Voices with Kokoro-82M v1.0 (Apache-2.0) through onnxruntime: the whispering narrator (a blend of af_nicole and
af_bella), the Voice of the AI (a blend of bf_emma and af_heart), Nora, a dispatcher, the doctor, and the whisperer
(am_onyx pitched down, then turned to breath: its spectrum kept, its pitch replaced by noise).

Weights and voices come from npm mirrors (see ../odyssey/setup.sh). Each line is synthesized whole (natural
prosody), trimmed of edge silence and cached on disk. Caption timing inside a line is estimated from
phoneme counts, anchored on the pauses the model actually leaves at punctuation. `pitch` shifts a voice by
resampling (a child's voice, the tiny workers), which also shortens it - the timeline measures the result.
"""
import hashlib
import os
import re

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
MODEL = os.path.join(HERE, ".models", "kokoro-v1.0-fp32.onnx")
VOICES = os.path.join(HERE, ".models", "voices")
CACHE = os.path.join(HERE, "build", "voice")
SR = 24000
_sess = _tok = None


def _load():
    global _sess, _tok
    if _sess is None:
        import onnxruntime as ort
        from kokoro_onnx.tokenizer import Tokenizer
        so = ort.SessionOptions()
        so.intra_op_num_threads = 4
        _sess, _tok = ort.InferenceSession(MODEL, so), Tokenizer()
    return _sess, _tok


def phonemes(text):
    return _load()[1].phonemize(text, "en-us")


def speak(text, voice="af_heart", speed=1.0):
    key = hashlib.sha1(f"fp32|{voice}|{speed}|{text}".encode()).hexdigest()[:16]
    path = os.path.join(CACHE, key + ".npy")
    if os.path.exists(path):
        return np.load(path)
    sess, tok = _load()
    ids = tok.tokenize(tok.phonemize(text, "en-us"))
    style = _style(voice)
    wav = sess.run(None, {"input_ids": np.array([[0, *ids, 0]], np.int64),
                          "style": style[min(len(ids), 509)][None],
                          "speed": np.array([speed], np.float32)})[0][0].astype(np.float32)
    if not np.isfinite(wav).all():
        raise RuntimeError(f"TTS produced non-finite samples for: {text!r}")
    loud = np.where(np.abs(wav) > 0.015)[0]
    if len(loud):
        wav = wav[max(0, loud[0] - 1440): loud[-1] + 1800]          # a long pre-roll: whispered onsets ("sh", "h") are quiet
    os.makedirs(CACHE, exist_ok=True)
    np.save(path, wav)
    return wav


def _style(voice):
    """A voice, or a blend of voices written 'af_nicole*0.6+af_bella*0.4' (the style vectors mixed)."""
    out = 0
    for part in voice.split("+"):
        name, _, w = part.partition("*")
        out = out + float(w or 1.0) * np.fromfile(os.path.join(VOICES, name + ".bin"), dtype=np.float32).reshape(-1, 256)
    return out


GANG = [("af_bella", 0.0), ("af_heart", 0.0), ("bf_emma", 0.0), ("am_michael", 0.0), ("am_puck", 0.0), ("af_sarah", 0.0)]


def chorus(text, speed=1.0):
    """A gang shout: six voices on the same words, each re-timed to the same length, a few ms apart."""
    lens = {v: len(speak(text, v, speed)) for v, _ in GANG}
    target = sorted(lens.values())[len(lens) // 2]
    parts = []
    for i, (v, _) in enumerate(GANG):
        sp = speed * lens[v] / target                                    # faster voices slowed, slower ones sped up
        w = speak(text, v, round(sp, 3))
        w = w / (np.sqrt((w ** 2).mean()) + 1e-9)
        parts.append(np.concatenate([np.zeros(int(SR * 0.006 * i), np.float32), w]))
    n = max(len(p) for p in parts)
    out = sum(np.pad(p, (0, n - len(p))) for p in parts) / len(parts)
    return (out * 0.09 / (np.sqrt((out ** 2).mean()) + 1e-9)).astype(np.float32)


def speak_fx(text, voice="af_heart", speed=1.0, pitch=0.0):
    """speak(), then shift up by `pitch` semitones by resampling (faster and higher, like a tape sped up)."""
    wav = chorus(text, speed) if voice == "chorus" else speak(text, voice, speed)
    if abs(pitch) < 1e-3:
        return wav
    from scipy import signal
    r = 2 ** (pitch / 12)
    n = int(round(len(wav) / r))
    return signal.resample(wav, n).astype(np.float32)


def pauses(wav, min_len=0.12):
    """(start, end) seconds of internal silences, used to anchor word timing."""
    hop = int(SR * 0.01)
    env = np.sqrt(np.convolve(wav ** 2, np.ones(hop * 3) / (hop * 3), mode="same"))[::hop]
    quiet = env < 0.012
    out, i = [], 0
    while i < len(quiet):
        if quiet[i]:
            j = i
            while j < len(quiet) and quiet[j]:
                j += 1
            if (j - i) * 0.01 >= min_len and i > 5 and j < len(quiet) - 5:
                out.append((i * 0.01, j * 0.01))
            i = j
        else:
            i += 1
    return out


def word_times(text, wav):
    """Estimated (word, start, end) for each word of `text` in `wav` (seconds)."""
    words = text.split()
    dur = len(wav) / SR
    weights = []
    for w in words:
        core = re.sub(r"[^\w'’-]", "", w)
        p = re.sub(r"[ˈˌː\s]", "", phonemes(core)) if core else ""
        weights.append(max(1, len(p)))
    # words ending in punctuation that normally gets a pause: anchor them to detected silences
    brk = [i for i, w in enumerate(words[:-1]) if re.search(r"[,.;:?!…—]$", w)]
    sil = pauses(wav)
    segs, start_w, t0 = [], 0, 0.0
    sil_iter = list(sil)
    for i in brk:
        if not sil_iter:
            break
        # expected time for this break from proportions
        frac = sum(weights[: i + 1]) / sum(weights)
        exp = frac * dur
        k = min(range(len(sil_iter)), key=lambda k: abs(sil_iter[k][0] - exp))
        if abs(sil_iter[k][0] - exp) < 0.45:
            s, e = sil_iter.pop(k)
            segs.append((start_w, i + 1, t0, s))
            start_w, t0 = i + 1, e
            sil_iter = [x for x in sil_iter if x[0] > e]
    segs.append((start_w, len(words), t0, dur))
    out = []
    for a, b, s, e in segs:
        tot = sum(weights[a:b])
        t = s
        for j in range(a, b):
            d = (e - s) * weights[j] / tot
            out.append((words[j], t, t + d))
            t += d
    return out


def whisper(wav, keep=0.12, seed=3):
    """Breath instead of voice: the short-time spectrum kept (so the words survive), the phase randomised (so the
    pitch is gone), with a trace of the voiced original underneath like a growl."""
    from scipy import signal
    f, t, Z = signal.stft(wav, SR, nperseg=512, noverlap=384)
    rng = np.random.default_rng(seed)
    ph = np.exp(2j * np.pi * rng.random(Z.shape))
    tilt = np.clip((f / 2500.0) ** 0.35, 0.6, 1.6)[:, None]              # breath is brighter than voice
    _, y = signal.istft(np.abs(Z) * ph * tilt, SR, nperseg=512, noverlap=384)
    y = y[: len(wav)]
    y = y * np.sqrt((wav ** 2).mean() / ((y ** 2).mean() + 1e-12))
    return ((1 - keep) * y + keep * wav).astype(np.float32)


_HA = {}


def cackle(voice, seed=0, n=7, lo=3.0, hi=7.5, end=2.0):
    """A built witch's cackle: a breath in, then staccato 'ha' bursts (40-60 ms apart) whose pitch climbs and falls
    back, a crescendo and decrescendo, and a long trailing 'haaa'. Made from the voice's own 'Ha!' at several pitches."""
    rng = np.random.default_rng(seed)
    out = []
    t = np.arange(int(0.28 * SR)) / SR                                   # the breath in
    br = np.random.default_rng(seed + 1).normal(0, 1, len(t))
    from scipy import signal
    br = signal.sosfilt(signal.butter(2, [900 / (SR / 2), 4500 / (SR / 2)], "band", output="sos"), br)
    out.append((br * (t / t[-1]) ** 2 * 0.05).astype(np.float32))
    for k in range(n + 1):
        u = k / n
        p = lo + (hi - lo) * np.sin(np.pi * min(1.0, u * 1.25)) if k < n else end
        p = round(p * 2) / 2
        if p not in _HA:
            _HA[p] = speak_fx("Ha!", voice, 1.12, p)
        w = _HA[p]
        env = np.abs(w)
        on = int(np.where(env > 0.05 * env.max())[0][0])
        d = rng.uniform(0.08, 0.17) if k < n else 0.42
        seg = w[on:on + int(d * SR)].copy()
        fi, fo = int(0.005 * SR), int((0.03 if k < n else 0.25) * SR)
        seg[:fi] *= np.linspace(0, 1, fi)
        seg[-fo:] *= np.linspace(1, 0, fo) ** 1.5
        amp = 0.55 + 0.45 * np.sin(np.pi * min(1.0, u * 1.1)) if k < n else 0.7
        out.append((seg * amp).astype(np.float32))
        out.append(np.zeros(int(rng.uniform(0.035, 0.075) * SR), np.float32))
    y = np.concatenate(out)
    return (y / (np.abs(y).max() + 1e-9) * 0.9).astype(np.float32)
