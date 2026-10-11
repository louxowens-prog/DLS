"""Re-voicing a line without moving it: a new reading placed on the original reading's timeline.

The two readings are aligned by dynamic time warping on log-spectral frames; every phrase of the new reading that
has a counterpart in the original then starts exactly where the original's did and plays at its own speed (WSOLA,
waveform-similarity overlap-add, squeezes a phrase only if it would overrun). The line keeps its start, its end and
its phrase onsets, so the edit, the caption chunks and the cues stay put. timeline.py uses this for the
pronunciation fixes in script.SAY.
"""
import numpy as np
from scipy import signal
from scipy.spatial.distance import cdist

SR = 24000
HOP = 240                                    # 10 ms analysis frames
NFFT = 1024


def _feats(x, edges):
    f, _, Z = signal.stft(x, SR, nperseg=NFFT, noverlap=NFFT - HOP, boundary=None, padded=False)
    p = np.abs(Z) ** 2
    idx = np.searchsorted(f, edges)
    bands = np.stack([p[idx[i]:max(idx[i] + 1, idx[i + 1])].mean(0) for i in range(len(edges) - 1)])
    return np.log(bands + 1e-7).T                                         # (frames, bands)


def _dtw(A, B):
    """Slope-constrained symmetric DTW (Sakoe-Chiba P=1). Returns the path as (i in A, j in B) pairs."""
    C = cdist(A, B)
    n, m = C.shape
    D = np.full((n, m), np.inf)
    P = np.zeros((n, m), np.int8)
    D[0, 0] = 2 * C[0, 0]
    for i in range(1, n):
        cand = np.full((3, m), np.inf)
        cand[1, 1:] = D[i - 1, :-1] + 2 * C[i, 1:]                       # diagonal
        cand[0, 2:] = D[i - 1, :-2] + 2 * C[i, 1:-1] + C[i, 2:]          # one row, two columns
        if i >= 2:
            cand[2, 1:] = D[i - 2, :-1] + 2 * C[i - 1, 1:] + C[i, 1:]    # two rows, one column
        P[i] = np.argmin(cand, axis=0)
        D[i] = cand[P[i], np.arange(m)]
    i, j = n - 1, m - 1
    path = [(i, j)]
    while i > 0 or j > 0:
        c = P[i, j]
        if c == 1:
            i, j = i - 1, j - 1
        elif c == 0:
            path.append((i, j - 1))
            i, j = i - 1, j - 2
        else:
            path.append((i - 1, j))
            i, j = i - 2, j - 1
        if i < 0 or j < 0:
            break
        path.append((i, j))
    return np.array(path[::-1])


def time_map(new, orig):
    """For each original frame, where the same sound sits in the new reading (in samples, frame centres).

    Where the original stops but the new reading does not (the dots in "A.G.I." used to stop it between letters),
    the map does not follow the stop: the new reading plays straight through at an even rate between the frames on
    either side, so the gap that caused the misreading is not rebuilt."""
    edges = np.geomspace(90, 8000, 41)
    A, B = _feats(new, edges), _feats(orig, edges)
    mu, sd = np.vstack([A, B]).mean(0), np.vstack([A, B]).std(0) + 1e-6
    path = _dtw((A - mu) / sd, (B - mu) / sd)
    m = len(B)
    ii = np.zeros(m)
    for j in range(m):
        ii[j] = path[path[:, 1] == j, 0].mean()
    lo, ln = np.log(np.exp(B).sum(1)), np.log(np.exp(A).sum(1))               # frame loudness (log power)
    quiet, quiet_n = lo < lo.max() - np.log(10 ** 3.5), ln < ln.max() - np.log(10 ** 3.5)
    j = 0
    while j < m:
        if not quiet[j]:
            j += 1
            continue
        k = j
        while k < m and quiet[k]:
            k += 1
        if k - j >= 6 and j > 0 and k < m:
            c = int(np.clip(round(ii[(j + k) // 2]), 0, len(A) - 1))          # where the warp put this stop
            a_n = b_n = c
            while a_n > 0 and quiet_n[a_n - 1]:
                a_n -= 1
            while b_n < len(A) - 1 and quiet_n[b_n + 1]:
                b_n += 1
            run = b_n - a_n + 1 if quiet_n[c] else 0
            if run < 8:              # the new reading has no real stop here, at most a consonant's closure: do not hold it
                a, b = max(0, j - 10), min(m - 1, k + 10)
                ii[a:b + 1] = np.linspace(ii[a], ii[b], b - a + 1)
        j = k
    k = 5
    ii = np.convolve(np.pad(ii, (k // 2, k // 2), mode="edge"), np.ones(k) / k, mode="valid")
    ii = np.maximum.accumulate(ii)
    centre = NFFT / 2
    return np.arange(m) * HOP + centre, ii * HOP + centre


def wsola(x, t_out, t_in, n_out, N=512, tol=128):
    """Render x on a new timeline: output time t_out[k] plays input time t_in[k] (both in samples)."""
    Hs = N // 2
    win = np.hanning(N + 1)[:-1]                                          # periodic: sums to 1 at 50 % overlap
    pad = N + 2 * tol
    xp = np.pad(np.asarray(x, np.float64), (pad, pad + N))
    y = np.zeros(n_out + N)
    wsum = np.zeros(n_out + N)
    prev = None
    for to in range(0, n_out, Hs):
        c = to + N / 2
        ti = int(round(np.interp(c, t_out, t_in, left=t_in[0] - (t_out[0] - c), right=t_in[-1] + (c - t_out[-1])) - N / 2))
        ti = int(np.clip(ti, -N, len(x)))
        if prev is None:
            best = ti
        else:
            ref = xp[pad + prev + Hs: pad + prev + Hs + N]
            seg = xp[pad + ti - tol: pad + ti + tol + N]
            corr = np.correlate(seg, ref, mode="valid")
            best = ti - tol + int(np.argmax(corr))
        y[to:to + N] += win * xp[pad + best: pad + best + N]
        wsum[to:to + N] += win
        prev = best
    return y[:n_out] / np.maximum(wsum[:n_out], 1e-3)


def _segments(x, min_gap=0.06):
    """Speech runs (start, end) in seconds, split at silences of at least min_gap."""
    from voice import pauses
    dur = len(x) / SR
    cuts = [(a, b) for a, b in pauses(np.asarray(x, np.float32), min_gap)]
    edges = [0.0] + [v for ab in cuts for v in ab] + [dur]
    return [(edges[i], edges[i + 1]) for i in range(0, len(edges), 2)]


def onto(new, orig):
    """The new reading on the original's timeline, matched to its loudness.

    Phrase-onset sync: every phrase of the new reading that has a counterpart in the original (found through the
    time warp) starts exactly where the original's did, and plays at its own natural speed; spare time goes into the
    pause after it (a phrase that would overrun is compressed to fit). So the captions and the mouths, which follow
    the original, stay in step phrase by phrase, and nothing the original got wrong inside a phrase (the stops
    between the letters of "A.G.I.") is rebuilt."""
    new = np.asarray(new, np.float64)
    orig = np.asarray(orig, np.float64)
    t_out, t_in = time_map(new, orig)
    so, sn = _segments(orig, 0.1), _segments(new, 0.1)                       # phrases: runs between real pauses
    anchors = [(0.0, 0.0)]
    for a, _ in so[1:]:
        m = np.interp(a * SR, t_out, t_in) / SR                               # where the warp says this phrase sits
        n = min(sn[1:], key=lambda s: abs(s[0] - m), default=None)
        if n is not None and abs(n[0] - m) < 0.1 and a > anchors[-1][0] + 0.05 and n[0] > anchors[-1][1] + 0.05:
            anchors.append((a, n[0]))
    anchors.append((len(orig) / SR, len(new) / SR))
    y = np.zeros(len(orig))
    for (o0, n0), (o1, n1) in zip(anchors[:-1], anchors[1:]):
        speech_end = max([e for s, e in sn if n0 <= s < n1] or [n1])
        piece = new[int(n0 * SR):int(min(speech_end + 0.04, n1) * SR)]
        # keep a breath before the next phrase: its own pause, up to 0.12 s, never squeezed shut
        room = int((o1 - o0) * SR) - int(max(0.02, min(n1 - speech_end, 0.12)) * SR)
        if len(piece) > room:                                                 # would overrun: compress to fit
            piece = wsola(piece, np.array([0.0, room]), np.array([0.0, len(piece)]), room)
        f = min(len(piece) // 4, int(0.005 * SR))
        if f:
            piece[:f] *= np.linspace(0, 1, f)
            piece[-f:] *= np.linspace(1, 0, f)
        i = int(o0 * SR)
        y[i:i + len(piece)] += piece[:len(y) - i]
    return (y * np.sqrt(_speech_power(orig) / (_speech_power(y) + 1e-20))).astype(np.float32)


def _speech_power(x):
    """Mean power over the 10 ms frames that are speech (within 30 dB of the loudest), not the pauses."""
    p = (x[:len(x) // HOP * HOP].reshape(-1, HOP) ** 2).mean(1)
    return p[p > p.max() * 1e-3].mean()
