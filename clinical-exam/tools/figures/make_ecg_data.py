#!/usr/bin/env python3
"""Generate schematic ECG polylines (JSON, mm) for the chapter-14 figures."""
import json, math, random, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from ecg_model import strip, regular, beat, FS
OUT = pathlib.Path(__file__).parent / "data"; OUT.mkdir(exist_ok=True)
D = 6.0   # seconds -> 150 mm
def save(name, pts): (OUT / f"{name}.json").write_text(json.dumps(pts))

N = dict()
save("normal", strip(regular(75, D), D))
save("normal_one", strip([(0.3, {})], 1.0))                       # single annotated beat
# atrial ectopic: premature beat with different P
b = regular(72, D); b.insert(4, (b[3][0] + 0.52, dict(p=-0.08)))
b = [x for i, x in enumerate(b) if not (i > 4 and False)]
b = sorted(b)[:4] + [sorted(b)[4]] + [(t + 0.25, k) for t, k in sorted(b)[5:]]
save("atrial_ectopic", strip(b, D))
# atrial fibrillation
rnd = random.Random(3); t = 0.2; af = []
while t < D - 0.3:
    af.append((t, dict(has_p=False))); t += rnd.uniform(0.42, 0.95)
fw = lambda x: 0.06 * math.sin(2 * math.pi * 6.3 * x) + 0.04 * math.sin(2 * math.pi * 8.9 * x + 1)
save("af", strip(af, D, extra=fw))
# atrial flutter 4:1 (atrial 300)
saw = lambda x: -0.18 * (((x * 5.0) % 1.0) - 0.5) * 2 * 0.6
save("flutter", strip(regular(75, D, start=0.33, has_p=False), D, extra=saw))
# junctional: no P / inverted P after QRS
save("junctional", strip(regular(50, D, has_p=False, u=-0.0), D))
# PVC
b = regular(70, D); pv = b[3][0] + 0.5
b = b[:3] + [(pv, dict(has_p=False, qrs=0.16, q=0, r=1.5, s=-0.6, t_amp=-0.5, t_w=0.08, qt=0.44))] + [(t + 0.35, k) for t, k in b[4:]]
save("pvc", strip(b, D))
# VT
save("vt", strip(regular(180, D, has_p=False, qrs=0.16, q=0, r=1.3, s=-0.9, t_amp=-0.55, t_w=0.07, qt=0.3), D))
# VF
rnd = random.Random(7)
ph = [rnd.uniform(0, 6) for _ in range(4)]
vf = lambda x: (0.35 * math.sin(2 * math.pi * 4.7 * x + ph[0]) + 0.22 * math.sin(2 * math.pi * 6.9 * x + ph[1])
                + 0.15 * math.sin(2 * math.pi * 3.1 * x + ph[2])) * (0.7 + 0.3 * math.sin(2 * math.pi * 0.4 * x))
save("vf", strip([], D, extra=vf))
# 1st degree block PR 0.30
save("block1", strip(regular(68, D, pr=0.30), D))
# Mobitz II / 2:1 : P at fixed rate, some QRS dropped
def pwaves(rate, dur, start, drop=lambda i: False, pr=0.18, prf=None):
    out = []; rr = 60 / rate; i = 0; t = start
    while t < dur - 0.3:
        prv = prf(i) if prf else pr
        if drop(i): out.append((t + prv, dict(pr=prv, has_qrs=False)))
        else: out.append((t + prv, dict(pr=prv)))
        t += rr; i += 1
    return out
save("mobitz2", strip(pwaves(80, D, 0.1, drop=lambda i: i % 4 == 3), D))
save("block21", strip(pwaves(90, D, 0.1, drop=lambda i: i % 2 == 1), D))
save("wenck", strip(pwaves(80, D, 0.1, drop=lambda i: i % 4 == 3, prf=lambda i: [0.18, 0.26, 0.33, 0.33][i % 4]), D))
# complete block: P 90/min, QRS 38/min wide, independent
ps = [(0.1 + i * 60 / 90 + 0.16, dict(pr=0.16, has_qrs=False)) for i in range(9)]
qs = [(0.5 + i * 60 / 38, dict(has_p=False, qrs=0.13, r=1.0, s=-0.35)) for i in range(4)]
save("chb", strip(ps + qs, D))
# RBBB (V1 rsR'), LBBB (V6 broad notched R)
save("rbbb", strip(regular(70, 3.0, qrs=0.13, q=0, r=0.35, s=-0.45, rprime=0.9, t_amp=-0.2), 3.0))
save("lbbb", strip(regular(70, 3.0, qrs=0.15, q=0, r=1.0, s=0, notch=0.85, st=-0.08, t_amp=-0.3), 3.0))
# hypertrophy / P waves
save("rvh_v1", strip(regular(70, 2.0, q=0, r=1.3, s=-0.2, st=-0.05, t_amp=-0.25), 2.0))
save("lvh_v5", strip(regular(70, 2.0, r=3.2, s=-0.1, st=-0.12, t_amp=-0.35, t_w=0.06), 2.0))
save("lvh_v1", strip(regular(70, 2.0, q=0, r=0.2, s=-3.0, st=0.08, t_amp=0.35), 2.0))
save("p_pulm", strip(regular(75, 2.0, p=0.32, p_w=0.022), 2.0))
save("p_mitr", strip(regular(75, 2.0, p=0.14, p2=0.15, p_w=0.022, pr=0.2), 2.0))
# ischaemia / MI patterns (single beats, 1.2 s)
one = lambda **k: strip([(0.35, k)], 1.2)
save("m_normal", one())
save("m_stemi", one(st=0.3, t_amp=0.35))
save("m_q", one(q=-0.45, r=0.6, st=0.2, t_amp=0.1))
save("m_tinv", one(q=-0.4, r=0.7, t_amp=-0.4, t_w=0.05))
save("m_old", one(q=-0.4, r=0.8))
save("m_stdep", one(st=-0.15, t_amp=0.1))
save("m_scoop", one(st=-0.12, t_amp=0.05, t_w=0.07))
save("m_strain", one(r=2.2, st=-0.1, t_amp=-0.35, t_w=0.07))
save("m_ischT", one(t_amp=-0.35, t_w=0.04))
save("hypoK", one(t_amp=0.08, st=-0.06, u=0.18))
save("hyperK", one(t_amp=0.9, t_w=0.03, p=0.05, qrs=0.11))
save("myx", strip(regular(52, 3.0, p=0.05, r=0.35, s=-0.08, q=-0.03, t_amp=0.06), 3.0))
save("peric", strip(regular(90, 3.0, st=0.2, t_amp=0.3), 3.0))
save("digoxin", one(st=-0.18, t_amp=0.08, t_w=0.08, qt=0.34))
save("aneur", one(q=-0.5, r=0.3, st=0.3, t_amp=0.3))
save("lead_neg", one(q=0, r=0.25, s=-0.9))
save("lead_pos", one())
print("ok", len(list(OUT.glob('*.json'))))
