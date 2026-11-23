"""Website-scroll Reel: a real anekant.tech page scrolling inside a phone, with captions above and a DM end card.

Usage: python3 make_site_reel.py spec.json out.mp4 SEED
spec.json:
{
  "page": "/abs/path/full_page_screenshot.png",   # full-page screenshot at 390 css px wide, deviceScaleFactor 2
  "hook_seconds": 2.8,                            # phone holds at the top while the hook shows
  "captions": [{"kicker": "...", "headline": "...", "body": "...", "start": 0, "end": 2.8, "scroll_to": 0}],
  "end": {"kicker": "...", "headline": "DM us “X”.", "body": "...", "seconds": 3.6}
}
Each caption's scroll_to is the page position (css px) the phone eases to by the caption's end.
Make the page screenshot by serving anekant_website/web locally (python3 -m http.server) and capturing
with Playwright at viewport 390x844, deviceScaleFactor 2, full_page=True.
Writes out.mp4 (with original soundtrack) and out.jpg (cover = first frame).
"""
import json, sys, pathlib, subprocess, tempfile, math
from PIL import Image, ImageDraw, ImageFilter
from playwright.sync_api import sync_playwright

TOOLS = pathlib.Path(__file__).parent.resolve()
sys.path.insert(0, str(TOOLS))
from soundtrack import make as make_audio  # noqa: E402

FONT = TOOLS / "fonts"
spec = json.loads(pathlib.Path(sys.argv[1]).read_text())
out = pathlib.Path(sys.argv[2]).resolve()
seed = int(sys.argv[3]) if len(sys.argv) > 3 else 5
tmp = pathlib.Path(tempfile.mkdtemp())
W, H, FPS, FADE = 1080, 1920, 30, 0.25
PAPER, INK, SIG = (239, 236, 228), (13, 13, 13), (255, 68, 21)

# Phone geometry
SW = 600                       # screen width on canvas
SCALE = SW / 780               # page png is 780 px wide (390 css @2x)
PX, PY = (W - SW) // 2, 720    # screen top-left
SH = H - PY + 200              # screen runs off the bottom edge on purpose
BEZ = 22

CSS = f"""
@font-face{{font-family:M;src:url(file://{FONT}/Manrope-Medium.woff2);font-weight:500}}
@font-face{{font-family:M;src:url(file://{FONT}/Manrope-ExtraBold.woff2);font-weight:800}}
*{{margin:0;padding:0;box-sizing:border-box}} html,body{{background:transparent}}
body{{font-family:M;width:{W}px;padding:150px 84px 0;color:#0D0D0D}}
body.dark{{color:#EFECE4}}
.k{{color:#FF4415;font-size:36px;font-weight:800;letter-spacing:.08em;text-transform:uppercase;margin-bottom:24px}}
h1{{font-size:96px;font-weight:800;line-height:1.02;letter-spacing:-.035em}}
p{{font-size:42px;font-weight:500;line-height:1.35;color:#6B675E;margin-top:22px}}
body.dark h1{{font-size:112px}} body.dark p{{color:#9A968C;font-size:50px;margin-top:40px}}
"""

caps = spec["captions"]
endc = spec["end"]


def render(pg, name, c, dark=False, h=640):
    body = (f"<div class='k'>{c.get('kicker','')}</div><h1>{c.get('headline','')}</h1>"
            + (f"<p>{c['body']}</p>" if c.get("body") else ""))
    f = tmp / f"{name}.html"
    f.write_text(f"<html><head><style>{CSS}</style></head><body class='{'dark' if dark else ''}'>{body}</body></html>")
    pg.set_viewport_size({"width": W, "height": h})
    pg.goto(f"file://{f}"); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(150)
    pg.screenshot(path=str(tmp / f"{name}.png"), omit_background=True)
    return Image.open(tmp / f"{name}.png").convert("RGBA")


with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page()
    cap_imgs = [render(pg, f"c{i}", c) for i, c in enumerate(caps)]
    end_img = render(pg, "end", endc, dark=True, h=H)
    b.close()

page = Image.open(spec["page"]).convert("RGB")
page = page.resize((SW, int(page.height * SCALE)), Image.LANCZOS)

# phone body + shadow, drawn once
phone = Image.new("RGBA", (W, H), (0, 0, 0, 0))
d = ImageDraw.Draw(phone)
d.rounded_rectangle((PX - BEZ + 18, PY - BEZ + 18, PX + SW + BEZ + 18, PY + SH + BEZ), 70, fill=SIG)  # hard offset shadow
d.rounded_rectangle((PX - BEZ, PY - BEZ, PX + SW + BEZ, PY + SH + BEZ), 70, fill=INK)
mask = Image.new("L", (SW, SH), 0)
ImageDraw.Draw(mask).rounded_rectangle((0, 0, SW, SH), 52, fill=255)

cap_total = max(c["end"] for c in caps)
total = cap_total + float(endc.get("seconds", 3.5))


def ease(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def scroll_at(t):
    pos, prev_end, prev = 0.0, 0.0, 0.0
    for c in caps:
        target = float(c.get("scroll_to", prev))
        s = max(prev_end, c["start"] + 0.2)
        if t <= c["end"]:
            return prev + (target - prev) * ease((t - s) / max(0.1, c["end"] - s - 0.3))
        prev, prev_end = target, c["end"]
    return prev


def frame(t):
    if t >= cap_total:
        im = Image.new("RGBA", (W, H), INK + (255,))
        im.alpha_composite(end_img, (0, 0))
        # vertically centre end card text
        im2 = Image.new("RGBA", (W, H), INK + (255,))
        bbox = end_img.getbbox() or (0, 0, W, 600)
        im2.alpha_composite(end_img, (0, (H - (bbox[3] - bbox[1])) // 2 - bbox[1]))
        d2 = ImageDraw.Draw(im2)
        return im2
    im = Image.new("RGBA", (W, H), PAPER + (255,))
    # gentle push-in on the whole phone, plus scrolled screen content
    y = int(scroll_at(t) * 2 * SCALE)
    y = max(0, min(page.height - SH, y))
    scr = page.crop((0, y, SW, y + SH))
    lift = int(40 * (1 - ease(t / 0.6)))  # phone rises in during the first 0.6 s (hook text is there from frame 1)
    im.alpha_composite(phone, (0, lift))
    im.paste(scr, (PX, PY + lift), mask)
    for i, c in enumerate(caps):
        if c["start"] - FADE <= t < c["end"]:
            a = 1.0 if i == 0 and t < c["end"] - FADE else min(1, (t - c["start"] + FADE) / FADE, (c["end"] - t) / FADE)
            a = max(0.0, min(1.0, a))
            if i == 0 and t < FADE:
                a = 1.0
            layer = cap_imgs[i].copy()
            layer.putalpha(Image.eval(layer.getchannel("A"), lambda v: int(v * a)))
            im.alpha_composite(layer, (0, 0))
    return im


ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                       "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "19",
                       "-pix_fmt", "yuv420p", str(tmp / "v.mp4")], stdin=subprocess.PIPE)
n_frames = int(total * FPS)
for n in range(n_frames):
    t = n / FPS
    im = frame(t)
    if cap_total - FADE <= t < cap_total:
        im = Image.blend(im, frame(cap_total), (t - (cap_total - FADE)) / FADE)
    im = im.convert("RGB")
    ImageDraw.Draw(im).rectangle((0, 0, int(W * t / total), 10), fill=SIG)
    if n == 0:
        im.save(out.with_suffix(".jpg"), quality=92)
    ff.stdin.write(im.tobytes())
ff.stdin.close(); ff.wait()

hits = [c["start"] for c in caps[1:]] + [cap_total]
make_audio(total, tmp / "a.wav", seed=seed, hits=hits)
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(tmp / "v.mp4"), "-i", str(tmp / "a.wav"), "-c:v", "copy",
                "-c:a", "aac", "-b:a", "160k", "-af", "loudnorm=I=-15:TP=-1.5", "-shortest", "-movflags", "+faststart",
                str(out)], check=True)
print("reel", out, f"{total:.1f}s")
