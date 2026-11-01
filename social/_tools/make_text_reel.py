"""Build a 1080x1920 text-scene Reel in Anekant's style, with motion and an original soundtrack.

Usage: python3 make_text_reel.py scenes.json out.mp4 [seed]
scenes.json: {"scenes": [{"kicker": "...", "headline": "...", "body": "...", "seconds": 2.5, "dark": true,
                          "image": "/abs/path.png (optional, framed card)",
                          "timer": 2.5 (optional: animated orange counter 0.0 s -> N s with a filling bar)}]}
Scene 1 is the hook: it must stop the scroll within the first second (a bold claim, question or number).
Motion: slow push-in on every scene, 0.3 s crossfades, thin progress bar at the top.
Writes out.mp4 (with audio) and out.jpg (cover = scene 1).
"""
import json, sys, pathlib, subprocess, tempfile, html as H
from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import sync_playwright

TOOLS = pathlib.Path(__file__).parent.resolve()
sys.path.insert(0, str(TOOLS))
from soundtrack import make as make_audio  # noqa: E402

FONT = TOOLS / "fonts"
spec = json.loads(pathlib.Path(sys.argv[1]).read_text())
out = pathlib.Path(sys.argv[2]).resolve()
seed = int(sys.argv[3]) if len(sys.argv) > 3 else 3
tmp = pathlib.Path(tempfile.mkdtemp())
W, Hh, FPS, FADE = 1080, 1920, 30, 0.3
SIG = (255, 68, 21)

CSS = f"""
@font-face{{font-family:M;src:url(file://{FONT}/Manrope-Medium.woff2);font-weight:500}}
@font-face{{font-family:M;src:url(file://{FONT}/Manrope-Bold.woff2);font-weight:700}}
@font-face{{font-family:M;src:url(file://{FONT}/Manrope-ExtraBold.woff2);font-weight:800}}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:1080px;height:1920px;font-family:M;background:#EFECE4;color:#0D0D0D;padding:200px 84px 260px;
  display:flex;flex-direction:column;justify-content:center;gap:48px}}
body.dark{{background:#0D0D0D;color:#EFECE4}}
body.timer{{padding-bottom:520px}}
.k{{color:#FF4415;font-size:38px;font-weight:800;letter-spacing:.08em;text-transform:uppercase}}
h1{{font-size:112px;font-weight:800;line-height:1.0;letter-spacing:-.035em}}
p{{font-size:50px;font-weight:500;line-height:1.4;color:#6B675E}}
body.dark p{{color:#9A968C}}
.img{{border:4px solid currentColor;box-shadow:14px 14px 0 #FF4415;overflow:hidden}}
.img img{{width:100%;display:block}}
.brand{{position:absolute;left:84px;bottom:150px;font-size:40px;font-weight:800}}
.brand i{{display:inline-block;width:20px;height:20px;border-radius:50%;background:#FF4415;margin-left:8px}}
"""

scenes = spec["scenes"]
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": W, "height": Hh})
    for i, s in enumerate(scenes):
        img = f'<div class="img"><img src="file://{s["image"]}"></div>' if s.get("image") else ""
        cls = " ".join(c for c in ("dark" if s.get("dark") else "", "timer" if s.get("timer") else "") if c)
        doc = f"""<html><head><style>{CSS}</style></head><body class="{cls}">
{f'<div class="k">{H.escape(s["kicker"])}</div>' if s.get("kicker") else ''}
{img}<h1>{s.get("headline","")}</h1>{f'<p>{s["body"]}</p>' if s.get("body") else ''}
<div class="brand">anekant.tech<i></i></div></body></html>"""
        f = tmp / f"s{i}.html"; f.write_text(doc)
        pg.goto(f"file://{f}"); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(150)
        pg.screenshot(path=str(tmp / f"s{i}.png"))
    b.close()

stills = [Image.open(tmp / f"s{i}.png").convert("RGB") for i in range(len(scenes))]
durs = [float(s.get("seconds", 2.5)) for s in scenes]
total = sum(durs)
starts = [sum(durs[:i]) for i in range(len(durs))]
try:
    big = ImageFont.truetype(str(TOOLS / "fonts" / "Manrope-Bold.ttf"), 230)
except OSError:
    big = ImageFont.load_default()


def scene_img(i, local):
    s, im = scenes[i], stills[i]
    z = 1 + 0.035 * (local / durs[i])
    w, h = int(W * z), int(Hh * z)
    im = im.resize((w, h), Image.BILINEAR).crop(((w - W) // 2, (h - Hh) // 2, (w - W) // 2 + W, (h - Hh) // 2 + Hh))
    if s.get("timer"):
        d = ImageDraw.Draw(im)
        v = min(float(s["timer"]), local / max(0.1, durs[i] - 0.4) * float(s["timer"]))
        d.text((84, 1330), f"{v:0.1f} s", font=big, fill=SIG)
        d.rectangle((84, 1610, 84 + int((W - 168) * v / float(s["timer"])), 1634), fill=SIG)
        d.rectangle((84, 1610, W - 84, 1634), outline=SIG, width=3)
    return im


ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{Hh}",
                       "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "19",
                       "-pix_fmt", "yuv420p", str(tmp / "v.mp4")], stdin=subprocess.PIPE)
for n in range(int(total * FPS)):
    t = n / FPS
    i = max(k for k in range(len(scenes)) if starts[k] <= t)
    im = scene_img(i, t - starts[i])
    if i + 1 < len(scenes) and t > starts[i + 1] - FADE:
        a = (t - (starts[i + 1] - FADE)) / FADE
        im = Image.blend(im, scene_img(i + 1, 0), a)
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, int(W * t / total), 10), fill=SIG)
    ff.stdin.write(im.tobytes())
ff.stdin.close(); ff.wait()

make_audio(total, tmp / "a.wav", seed=seed, hits=starts[1:])
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(tmp / "v.mp4"), "-i", str(tmp / "a.wav"), "-c:v", "copy",
                "-c:a", "aac", "-b:a", "160k", "-af", "loudnorm=I=-15:TP=-1.5", "-shortest", "-movflags", "+faststart", str(out)], check=True)
stills[0].save(out.with_suffix(".jpg"), quality=92)
print("reel", out, f"{total:.1f}s")
