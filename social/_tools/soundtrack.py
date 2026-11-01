"""Generate a soft, original ambient soundtrack (royalty-free, made from scratch) for Reels.

Usage:  python3 soundtrack.py DURATION_SECONDS out.wav [seed] [hit_times_comma_separated]
   or:  from soundtrack import make; make(13.0, "out.wav", seed=3, hits=[2.0, 7.2])
`hits` are moments (scene changes) that get a soft whoosh. Different seeds pick different chord
progressions and tempos so consecutive Reels don't sound identical.
"""
import sys, wave
import numpy as np

PROGS = [
    [[110, 164.81, 196, 246.94, 261.63], [87.31, 130.81, 174.61, 220, 261.63], [130.81, 196, 246.94, 329.63], [98, 146.83, 196, 293.66]],
    [[130.81, 196, 246.94, 293.66], [110, 164.81, 220, 261.63], [87.31, 130.81, 174.61, 261.63], [98, 146.83, 196, 246.94]],
    [[146.83, 220, 261.63, 349.23], [116.54, 174.61, 233.08, 293.66], [130.81, 196, 261.63, 329.63], [110, 164.81, 220, 277.18]],
]


def make(T, out, seed=3, hits=()):
    rng = np.random.default_rng(seed)
    sr = 44100
    t = np.arange(int(sr * T)) / sr

    def env(a, r, s=0, e=T):
        return np.clip((t - s) / a, 0, 1) * np.clip((e - t) / r, 0, 1)

    def pad(fr, s, e):
        x = np.zeros_like(t)
        for f in fr:
            for det in (-0.6, 0, 0.6):
                x += np.sin(2 * np.pi * (f + det) * t + rng.random() * 6.28) + 0.25 * np.sin(2 * np.pi * 2 * (f + det) * t)
        return x * env(1.2, 1.2, s, e) * 0.5 / len(fr)

    prog = PROGS[seed % len(PROGS)]
    seg = T / len(prog)
    x = sum(pad(c, max(0, i * seg - 0.8), min(T, (i + 1) * seg + 0.8)) for i, c in enumerate(prog))
    beat = 60 / (84 + 8 * (seed % 3))
    for n in range(int(1.5 / beat), int((T - 0.6) / beat)):
        t0 = n * beat; m = (t >= t0) & (t < t0 + .35); tt = t[m] - t0
        x[m] += 0.55 * np.sin(2 * np.pi * (55 + 40 * np.exp(-tt * 25)) * tt) * np.exp(-tt * 9)
    notes = [659.25, 783.99, 880, 987.77, 1174.66]
    for n in range(int((T - 3) / 0.74)):
        t0 = 1.6 + n * 0.74; m = (t >= t0) & (t < t0 + 1.2); tt = t[m] - t0
        x[m] += 0.10 * np.sin(2 * np.pi * notes[(n * 2 + seed) % 5] * tt) * np.exp(-tt * 3.5)
    for t0 in hits:
        m = (t >= t0 - .4) & (t < t0 + .4)
        if m.sum() < 50: continue
        nz = np.convolve(rng.standard_normal(m.sum()), np.ones(40) / 40, "same")
        x[m] += 0.45 * nz * np.hanning(m.sum())
    d = np.zeros_like(x)
    for dl, g in ((0.031, .35), (0.047, .3), (0.071, .25), (0.113, .2), (0.167, .15)):
        s = int(dl * sr); d[s:] += x[:-s] * g
    x = (x + d) * env(0.4, 1.0)
    x = x / np.max(np.abs(x)) * 0.7
    st = np.stack([x, np.roll(x, int(0.011 * sr))], 1)
    with wave.open(str(out), "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes((st * 32767).astype("<i2").tobytes())


if __name__ == "__main__":
    hits = [float(h) for h in sys.argv[4].split(",")] if len(sys.argv) > 4 else []
    make(float(sys.argv[1]), sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 3, hits)
