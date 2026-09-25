"""Shared narration helpers: Kokoro neural TTS via sherpa-onnx, cached per line, and a
timeline builder that sizes scenes to their voice-over.

Kokoro v0.19 speakers: 0 af, 1 af_bella, 2 af_nicole, 3 af_sarah, 4 af_sky (female US),
5 bf_emma, 6 bf_isabella (female UK), 7 bm_george, 8 bm_lewis, 9 am_adam, 10 am_michael.
"""
import hashlib
import os
import subprocess
import tarfile

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(HERE, ".models", "kokoro-int8-en-v0_19")
CACHE = os.path.join(HERE, "out", "_voice")
VSR = 24000
_tts = None


def ensure_model():
    """Fetch the Apache-2.0 Kokoro export bundled in the npm package n8n-nodes-ttsbro."""
    if os.path.exists(os.path.join(MODEL_DIR, "model.int8.onnx")):
        return
    root = os.path.dirname(MODEL_DIR)
    os.makedirs(root, exist_ok=True)
    tgz = os.path.join(root, "ttsbro.tgz")
    subprocess.run(["curl", "-sSfL", "-o", tgz,
                    "https://registry.npmjs.org/n8n-nodes-ttsbro/-/n8n-nodes-ttsbro-0.1.6.tgz"], check=True)
    prefix = "package/kokoro-int8-en-v0_19/"
    with tarfile.open(tgz) as tf:
        for m in tf.getmembers():
            if m.name.startswith(prefix) and m.isfile():
                m.name = os.path.join("kokoro-int8-en-v0_19", m.name[len(prefix):])
                tf.extract(m, root)
    os.remove(tgz)


def speak(line, sid=1, speed=1.1):
    """Synthesize one line (float32 @ 24 kHz), trimmed of edge silence, cached on disk."""
    global _tts
    key = hashlib.sha1(f"{sid}|{speed}|{line}".encode()).hexdigest()[:16]
    path = os.path.join(CACHE, key + ".npy")
    if os.path.exists(path):
        return np.load(path)
    if _tts is None:
        import sherpa_onnx
        ensure_model()
        d = MODEL_DIR + "/"
        _tts = sherpa_onnx.OfflineTts(sherpa_onnx.OfflineTtsConfig(model=sherpa_onnx.OfflineTtsModelConfig(
            kokoro=sherpa_onnx.OfflineTtsKokoroModelConfig(model=d + "model.int8.onnx", voices=d + "voices.bin",
                                                           tokens=d + "tokens.txt", data_dir=d + "espeak-ng-data"),
            num_threads=4)))
    a = np.array(_tts.generate(line, sid=sid, speed=speed).samples, dtype=np.float32)
    loud = np.where(np.abs(a) > 0.02)[0]
    if len(loud):
        a = a[max(0, loud[0] - 600): loud[-1] + 2400]
    os.makedirs(CACHE, exist_ok=True)
    np.save(path, a)
    return a


class Timeline:
    """script: [(scene, lead_in, [line | (sid, line)], tail)]. Lines play back to back with `gap`."""

    def __init__(self, script, sid=1, speed=1.1, gap=0.26):
        self.lines, self.dur, self.vo = {}, {}, []
        tg = 0.0
        for key, pin, lines, pout in script:
            t, lst = pin, []
            for ln in lines:
                s, txt = ln if isinstance(ln, tuple) else (sid, ln)
                a = speak(txt, s, speed)
                d = len(a) / VSR
                lst.append((t, d, txt, s))
                self.vo.append((tg + t, a))
                t += d + gap
            self.lines[key], self.dur[key] = lst, t - gap + pout
            tg += self.dur[key]
        self.total = tg

    def start(self, key, i):
        return self.lines[key][i][0]

    def end(self, key, i):
        return self.lines[key][i][0] + self.lines[key][i][1]

    def phrases(self, key, i, parts):
        """Approximate start times of phrases inside line i (by character position)."""
        st, d, s, _ = self.lines[key][i]
        out, pos = [], 0
        for p in parts:
            k = s.find(p, pos)
            out.append(st + d * max(0, k) / len(s))
            pos = max(pos, k)
        return out

    def active(self, key, t, hold=0.2):
        for st, d, s, sid in self.lines[key]:
            if st <= t < st + d + hold:
                return s, sid
        return None

    def track(self, n, sr):
        """Mono voice track resampled to `sr`, n samples long."""
        out = np.zeros(n)
        for st, a in self.vo:
            up = np.interp(np.arange(int(len(a) * sr / VSR)) * VSR / sr, np.arange(len(a)), a)
            i = int(st * sr)
            j = min(n, i + len(up))
            if i < n:
                out[i:j] += up[: j - i]
        return out


def duck(music, voice, sr, depth=0.55):
    env = np.convolve(np.abs(voice), np.ones(sr // 10) / (sr // 10), mode="same")
    env = np.clip(env / (env.max() + 1e-9) * 4, 0, 1)
    return music * (1 - depth * env)
