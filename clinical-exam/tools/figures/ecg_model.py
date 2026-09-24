#!/usr/bin/env python3
"""Synthetic, textbook-style ECG traces for teaching schematics.

Standard paper calibration: 25 mm/s, 10 mm/mV. Output: polylines in millimetres,
(x to the right, y upward). These are *schematic* illustrations drawn from the
morphology described in the manuscript and standard references, not patient tracings.
"""
import math, random

FS = 500  # samples per second


def g(t, mu, sig, amp):
    return amp * math.exp(-((t - mu) ** 2) / (2 * sig ** 2))


def beat(t, t0, p=0.15, pr=0.16, q=-0.08, r=1.1, s=-0.25, qrs=0.08,
         st=0.0, t_amp=0.3, t_w=0.055, qt=0.38, p_w=0.025, p2=0.0,
         rprime=0.0, notch=0.0, has_p=True, has_qrs=True, delta=0.0, u=0.0):
    """Value (mV) at time t for one beat whose QRS onset is at t0."""
    v = 0.0
    if has_p and p:
        tp = t0 - pr + 0.05
        v += g(t, tp, p_w, p)
        if p2:  # bifid / biphasic P
            v += g(t, tp + 0.045, p_w, p2)
    if not has_qrs:
        return v
    k = qrs / 0.08
    if delta:  # slurred upstroke (WPW)
        v += g(t, t0 + 0.01, 0.02, delta)
    v += g(t, t0 + 0.012 * k, 0.008 * k, q)
    v += g(t, t0 + 0.035 * k, 0.011 * k, r)
    if notch:
        v += g(t, t0 + 0.06 * k, 0.012 * k, notch)
    v += g(t, t0 + 0.06 * k, 0.010 * k, s)
    if rprime:
        v += g(t, t0 + 0.085 * k, 0.012 * k, rprime)
    j = t0 + qrs
    tt = t0 + qt - 0.12
    # ST segment level: smooth ramp from J point to T wave
    if st:
        if j <= t <= tt:
            v += st
        elif j - 0.015 < t < j:
            v += st * (t - (j - 0.015)) / 0.015
        elif tt < t < tt + 0.08:
            v += st * (1 - (t - tt) / 0.08)
    v += g(t, tt, t_w, t_amp)
    if u:
        v += g(t, tt + 0.16, 0.04, u)
    return v


def strip(beats, dur, fs=FS, noise=0.0, extra=None, seed=1):
    """beats: list of (t0, kwargs). extra: f(t)->mV added (e.g. f-waves)."""
    rnd = random.Random(seed)
    pts = []
    n = int(dur * fs)
    for i in range(n + 1):
        t = i / fs
        v = sum(beat(t, t0, **kw) for t0, kw in beats if -0.5 < t - t0 < 0.9)
        if extra:
            v += extra(t)
        if noise:
            v += rnd.gauss(0, noise)
        pts.append((round(t * 25, 2), round(v * 10, 2)))
    return pts


def regular(rate, dur, start=0.25, **kw):
    rr = 60.0 / rate
    out, t = [], start
    while t < dur - 0.3:
        out.append((t, dict(kw)))
        t += rr
    return out
