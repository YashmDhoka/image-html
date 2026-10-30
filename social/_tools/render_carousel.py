"""Render Instagram carousel slides (1080x1350) in Anekant's site style."""
import json, sys, pathlib
from playwright.sync_api import sync_playwright

FONT = str((pathlib.Path(__file__).parent / "fonts").resolve())
OUT = pathlib.Path(sys.argv[2])
OUT.mkdir(parents=True, exist_ok=True)
deck = json.loads(pathlib.Path(sys.argv[1]).read_text())

CSS = f"""
@font-face{{font-family:M;src:url(file://{FONT}/Manrope-Regular.woff2);font-weight:400}}
@font-face{{font-family:M;src:url(file://{FONT}/Manrope-Medium.woff2);font-weight:500}}
@font-face{{font-family:M;src:url(file://{FONT}/Manrope-SemiBold.woff2);font-weight:600}}
@font-face{{font-family:M;src:url(file://{FONT}/Manrope-Bold.woff2);font-weight:700}}
@font-face{{font-family:M;src:url(file://{FONT}/Manrope-ExtraBold.woff2);font-weight:800}}
:root{{--paper:#EFECE4;--deep:#E3DFD3;--ink:#0D0D0D;--mute:#6B675E;--signal:#FF4415}}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:1080px;height:1350px;font-family:M;color:var(--ink);background:var(--paper);
  padding:84px 88px;display:flex;flex-direction:column;position:relative;overflow:hidden}}
body.dark{{background:var(--ink);color:var(--paper)}}
.top{{display:flex;justify-content:space-between;align-items:center;font-size:28px;font-weight:700;
  letter-spacing:.08em;text-transform:uppercase;padding-bottom:28px;border-bottom:3px solid currentColor}}
.dot{{display:inline-block;width:16px;height:16px;border-radius:50%;background:var(--signal);margin-left:6px;vertical-align:middle}}
.mid{{flex:1;display:flex;flex-direction:column;justify-content:center;gap:40px}}
.kicker{{font-size:30px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--signal)}}
h1{{font-size:128px;font-weight:800;line-height:.98;letter-spacing:-.035em}}
h2{{font-size:88px;font-weight:800;line-height:1.04;letter-spacing:-.03em}}
p{{font-size:44px;font-weight:500;line-height:1.42;color:var(--mute)}}
body.dark p{{color:#9A968C}}
.num{{font-size:220px;font-weight:800;line-height:.8;color:var(--signal);letter-spacing:-.05em}}
.card{{border:3px solid var(--ink);background:#fff8;box-shadow:10px 10px 0 var(--ink);padding:40px 44px}}
.card p{{color:var(--ink)}}
.foot{{display:flex;justify-content:space-between;align-items:center;font-size:24px;font-weight:600;
  padding-top:28px;border-top:3px solid currentColor}}
.swipe{{color:var(--signal);font-weight:800}}
.cta{{display:inline-block;background:var(--signal);color:var(--ink);font-weight:800;font-size:40px;
  padding:26px 40px;border:3px solid var(--paper);box-shadow:10px 10px 0 var(--paper)}}
.rows{{display:flex;flex-direction:column;gap:34px}}
.row{{display:flex;gap:24px;font-size:44px;font-weight:600;line-height:1.3;align-items:baseline}}
.row b{{color:var(--signal);font-weight:800;min-width:56px}}
.bar{{position:absolute;right:0;top:0;width:22px;height:100%;background:var(--signal)}}
"""

def page(s, i, n):
    dark = s.get("dark", False)
    foot_r = '<span class="swipe">SWIPE →</span>' if i < n - 1 else "anekant.tech"
    return f"""<html><head><style>{CSS}</style></head><body class="{'dark' if dark else ''}">
<div class="top"><span>Anekant<span class="dot"></span></span><span>{deck['tag']}</span></div>
<div class="mid">{s['html']}</div>
<div class="foot"><span>{i+1:02d} / {n:02d}</span>{foot_r}</div>
{'<div class="bar"></div>' if i == 0 else ''}
</body></html>"""

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1080, "height": 1350})
    n = len(deck["slides"])
    for i, s in enumerate(deck["slides"]):
        hp = OUT / f"_tmp{i}.html"; hp.write_text(page(s, i, n))
        pg.goto(f"file://{hp.resolve()}", wait_until="load")
        pg.evaluate("document.fonts.ready")
        pg.wait_for_timeout(150)
        pg.screenshot(path=str(OUT / f"{deck['slug']}-{i+1:02d}.jpg"), type="jpeg", quality=92)
    b.close()
print("rendered", n)
