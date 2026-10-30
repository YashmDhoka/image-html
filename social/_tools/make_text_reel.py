"""Build a 1080x1920 text-scene Reel in Anekant's style.

Usage: python3 make_text_reel.py scenes.json out.mp4
scenes.json: {"scenes": [{"kicker": "...", "headline": "...", "body": "...", "seconds": 2.5, "dark": true,
                          "image": "/abs/path.png (optional, shown in a framed card)"}]}
Each scene is a still card; scenes are joined with short crossfades. Also writes out.jpg (cover = scene 1).
"""
import json, sys, pathlib, subprocess, tempfile, html as H
from playwright.sync_api import sync_playwright

FONT = (pathlib.Path(__file__).parent / "fonts").resolve()
spec = json.loads(pathlib.Path(sys.argv[1]).read_text())
out = pathlib.Path(sys.argv[2]).resolve()
tmp = pathlib.Path(tempfile.mkdtemp())

CSS = f"""
@font-face{{font-family:M;src:url(file://{FONT}/Manrope-Medium.woff2);font-weight:500}}
@font-face{{font-family:M;src:url(file://{FONT}/Manrope-Bold.woff2);font-weight:700}}
@font-face{{font-family:M;src:url(file://{FONT}/Manrope-ExtraBold.woff2);font-weight:800}}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:1080px;height:1920px;font-family:M;background:#EFECE4;color:#0D0D0D;padding:200px 84px 260px;
  display:flex;flex-direction:column;justify-content:center;gap:48px}}
body.dark{{background:#0D0D0D;color:#EFECE4}}
.k{{color:#FF4415;font-size:38px;font-weight:800;letter-spacing:.08em;text-transform:uppercase}}
h1{{font-size:112px;font-weight:800;line-height:1.0;letter-spacing:-.035em}}
p{{font-size:50px;font-weight:500;line-height:1.4;color:#6B675E}}
body.dark p{{color:#9A968C}}
.img{{border:4px solid currentColor;box-shadow:14px 14px 0 #FF4415;overflow:hidden}}
.img img{{width:100%;display:block}}
.brand{{position:absolute;left:84px;bottom:150px;font-size:40px;font-weight:800}}
.brand i{{display:inline-block;width:20px;height:20px;border-radius:50%;background:#FF4415;margin-left:8px}}
"""

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1080, "height": 1920})
    for i, s in enumerate(spec["scenes"]):
        img = f'<div class="img"><img src="file://{s["image"]}"></div>' if s.get("image") else ""
        doc = f"""<html><head><style>{CSS}</style></head><body class="{'dark' if s.get('dark') else ''}">
{f'<div class="k">{H.escape(s["kicker"])}</div>' if s.get("kicker") else ''}
{img}<h1>{s.get("headline","")}</h1>{f'<p>{s["body"]}</p>' if s.get("body") else ''}
<div class="brand">anekant.tech<i></i></div></body></html>"""
        f = tmp / f"s{i}.html"; f.write_text(doc)
        pg.goto(f"file://{f}"); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(150)
        pg.screenshot(path=str(tmp / f"s{i}.png"))
    b.close()

fade = 0.35
scenes = spec["scenes"]
cmd = ["ffmpeg", "-y", "-loglevel", "error"]
for i, s in enumerate(scenes):
    cmd += ["-loop", "1", "-t", str(s.get("seconds", 2.5) + fade), "-i", str(tmp / f"s{i}.png")]
fc, last, offset = [], "[0:v]", 0.0
for i in range(1, len(scenes)):
    offset += scenes[i - 1].get("seconds", 2.5)
    fc.append(f"{last}[{i}:v]xfade=transition=fade:duration={fade}:offset={offset:.2f}[x{i}]")
    last = f"[x{i}]"
fc.append(f"{last}format=yuv420p,fps=30[v]")
cmd += ["-filter_complex", ";".join(fc), "-map", "[v]", "-c:v", "libx264", "-preset", "veryfast",
        "-crf", "19", "-movflags", "+faststart", "-an", str(out)]
subprocess.run(cmd, check=True)
subprocess.run(["cp", str(tmp / "s0.png"), str(out.with_suffix(".png"))], check=True)
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(out.with_suffix(".png")), "-q:v", "2", str(out.with_suffix(".jpg"))], check=True)
print("reel", out)
