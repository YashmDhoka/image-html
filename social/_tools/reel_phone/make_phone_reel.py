"""Reel v3: hook on finished earrings -> phone mockup with thumb scrolling the page -> rewind -> CTA end card."""
import pathlib, subprocess
from PIL import Image, ImageDraw, ImageFilter
from playwright.sync_api import sync_playwright

HERE = pathlib.Path(__file__).parent
E = pathlib.Path("/home/claude/anekant_website/assets/emerald_earring")
F = "/home/claude/anekant_website/web/fonts/manrope"
L = HERE / "v3layers"; L.mkdir(exist_ok=True)
W, H, FPS = 1080, 1920, 30
INK, PAPER, SIG = (13, 13, 13), (239, 236, 228), (255, 68, 21)

CSS = f"""@font-face{{font-family:M;src:url(file://{F}/Manrope-Medium.woff2);font-weight:500}}
@font-face{{font-family:M;src:url(file://{F}/Manrope-Bold.woff2);font-weight:700}}
@font-face{{font-family:M;src:url(file://{F}/Manrope-ExtraBold.woff2);font-weight:800}}
*{{margin:0;padding:0;box-sizing:border-box}} html,body{{background:transparent}}
body{{font-family:M;color:#EFECE4;width:{W}px}}
.k{{color:#FF4415;font-size:36px;font-weight:800;letter-spacing:.08em;text-transform:uppercase;margin-bottom:22px}}
h1{{font-size:96px;font-weight:800;line-height:1.02;letter-spacing:-.035em}}
.pad{{padding:0 72px}}"""

def layer(name, html, h):
    p = L / f"{name}.html"
    p.write_text(f"<html><head><style>{CSS}</style></head><body style='height:{h}px'>{html}</body></html>")
    pg.goto(f"file://{p}"); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(120)
    pg.set_viewport_size({"width": W, "height": h})
    pg.screenshot(path=str(L / f"{name}.png"), omit_background=True)
    return Image.open(L / f"{name}.png").convert("RGBA")

with sync_playwright() as pw:
    b = pw.chromium.launch(); pg = b.new_page()
    hook = layer("hook", "<div class='pad' style='padding-top:150px'><div class='k'>Emerald Earring · anekant.tech</div>"
                 "<h1>This product page has no video in it.</h1></div>", 560)
    t1 = layer("t1", "<div class='pad' style='padding-top:130px'><div class='k'>Watch the thumb</div>"
               "<h1>Your scroll<br>builds it.</h1></div>", 440)
    t2 = layer("t2", "<div class='pad' style='padding-top:130px'><div class='k'>Now scroll up</div>"
               "<h1>It rewinds.<br>Smoothly.</h1></div>", 440)
    end = layer("end", "<div class='pad' style='padding-top:170px'><div class='k'>Scroll-driven product pages</div>"
                "<h1>For brands whose product is the hero.</h1>"
                "<p style='font-size:46px;font-weight:500;color:#9A968C;margin-top:34px;line-height:1.4'>Jewellery · fragrance · architecture · devices</p></div>"
                "<div class='pad' style='position:absolute;top:1480px'>"
                "<div style='display:inline-block;background:#FF4415;color:#0D0D0D;font-weight:800;font-size:54px;padding:30px 46px;box-shadow:12px 12px 0 #EFECE4'>DM us “SCROLL”</div>"
                "<div style='margin-top:58px;font-size:46px;font-weight:800'>anekant.tech <span style=\"display:inline-block;width:22px;height:22px;border-radius:50%;background:#FF4415\"></span></div></div>", H)
    # page chrome inside the phone screen (600 x 1260)
    pg.set_viewport_size({"width": 600, "height": 1260})
    p = L / "chrome.html"
    p.write_text(f"""<html><head><style>{CSS} body{{width:600px;height:1260px;position:relative}}
    .bar{{position:absolute;top:0;left:0;right:0;height:150px;padding:78px 34px 0;display:flex;justify-content:space-between;
         font-size:22px;font-weight:800;letter-spacing:.08em;color:#EFECE4;background:linear-gradient(#0b1a12ee,#0b1a1200)}}
    .bot{{position:absolute;bottom:0;left:0;right:0;padding:0 34px 70px;background:linear-gradient(#0b1a1200,#0b1a12f0 40%)}}
    .bot h2{{font-size:46px;font-weight:800;letter-spacing:-.02em;color:#EFECE4;padding-top:90px}}
    .bot p{{font-size:24px;font-weight:500;color:#b9c4b8;margin-top:10px}}
    .pill{{display:inline-block;margin-top:24px;border:2px solid #EFECE4;color:#EFECE4;font-size:20px;font-weight:800;padding:12px 22px;letter-spacing:.06em}}
    .notch{{position:absolute;top:22px;left:50%;width:150px;height:38px;margin-left:-75px;background:#000;border-radius:20px}}
    </style></head><body><div class='bar'><span>ANEKANT <span style='color:#FF4415'>●</span></span><span>MENU</span></div>
    <div class='bot'><h2>Emerald Earring</h2><p>Fine jewellery scrollytelling</p><span class='pill'>SCROLL TO EXPLORE ↓</span></div>
    <div class='notch'></div></body></html>""")
    pg.goto(f"file://{p}"); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(120)
    pg.screenshot(path=str(L / "chrome.png"), omit_background=True)
    chrome = Image.open(L / "chrome.png").convert("RGBA")
    b.close()

def frame(i):  # demo frame, sparkle cropped off by staying left of x=1180
    return Image.open(E / f"ezgif-frame-{i:03d}.png").convert("RGB")

SW, SH = 600, 1260
PX, PY = (W - (SW + 44)) // 2, 500          # phone outer box
phone = Image.new("RGBA", (SW + 44, SH + 44), (0, 0, 0, 0))
d = ImageDraw.Draw(phone)
d.rounded_rectangle((0, 0, SW + 43, SH + 43), 78, fill=(28, 28, 28, 255))
d.rounded_rectangle((2, 2, SW + 41, SH + 41), 76, outline=(70, 70, 70, 255), width=2)
mask = Image.new("L", (SW, SH), 0); ImageDraw.Draw(mask).rounded_rectangle((0, 0, SW - 1, SH - 1), 58, fill=255)
shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
ImageDraw.Draw(shadow).rounded_rectangle((PX + 30, PY + 40, PX + SW + 74, PY + SH + 84), 78, fill=(255, 68, 21, 120))
shadow = shadow.filter(ImageFilter.GaussianBlur(40))

def screen(i):
    f = frame(i)
    sc = Image.new("RGB", (SW, SH), (14, 32, 23))
    # vertical crop of the demo frame (centre, wide enough for both earrings) scaled to screen width
    crop = f.crop((340, 0, 940, 720)).resize((SW, 720), Image.LANCZOS)
    sc.paste(crop, (0, (SH - 720) // 2 - 40))
    # soften top/bottom seams
    g = Image.new("L", (1, SH))
    for y in range(SH):
        top, bot = (SH - 720) // 2 - 40, (SH - 720) // 2 - 40 + 720
        a = 255 if top + 60 < y < bot - 60 else (max(0, min(255, int(255 * (y - top) / 60))) if y <= top + 60 else max(0, min(255, int(255 * (bot - y) / 60))))
        g.putpixel((0, y), a)
    bg = Image.new("RGB", (SW, SH), (14, 32, 23))
    sc = Image.composite(sc, bg, g.resize((SW, SH)))
    sc = sc.convert("RGBA"); sc.alpha_composite(chrome)
    return sc

def thumb(img, y, alpha):
    o = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dd = ImageDraw.Draw(o)
    x = PX + 22 + SW * 0.72
    dd.ellipse((x - 46, y - 46, x + 46, y + 46), fill=(255, 255, 255, int(110 * alpha)), outline=(255, 255, 255, int(220 * alpha)), width=4)
    img.alpha_composite(o)

def base():
    return Image.new("RGBA", (W, H), INK + (255,))

ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                       "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p",
                       "-movflags", "+faststart", str(HERE / "out/emerald-reel-v3-silent.mp4")], stdin=subprocess.PIPE)
def emit(img): ff.stdin.write(img.convert("RGB").tobytes())

# A) 0-2.0s hook: finished earrings big, slow push-in, hook text
for k in range(60):
    i = 150 + int(k * 60 / 60)                 # 150 -> 210 (earrings settle)
    f = frame(min(i, 210)).crop((280, 0, 1000, 720))
    s = 1080 + k * 2
    f = f.resize((s, s), Image.LANCZOS).crop(((s - 1080) // 2, (s - 1080) // 2, (s - 1080) // 2 + 1080, (s - 1080) // 2 + 1080))
    img = base(); img.paste(f, (0, 620)); img.alpha_composite(hook); emit(img)

# B) 2.0-7.2s phone: scroll forward 1 -> 210 with thumb moving up
N = 156
for k in range(N):
    i = 1 + round(k * 209 / (N - 1))
    img = base(); img.alpha_composite(shadow); img.alpha_composite(phone, (PX, PY))
    img.paste(screen(i), (PX + 22, PY + 22), mask)
    img.alpha_composite(t1)
    cyc = (k % 52) / 52                        # three swipes
    thumb(img, PY + 1050 - cyc * 650, min(1, 4 * (1 - cyc)) if cyc > .75 else min(1, cyc * 8))
    emit(img)

# C) 7.2-9.4s rewind 210 -> 110 with thumb moving down
N2 = 66
for k in range(N2):
    i = 210 - round(k * 100 / (N2 - 1))
    img = base(); img.alpha_composite(shadow); img.alpha_composite(phone, (PX, PY))
    img.paste(screen(i), (PX + 22, PY + 22), mask)
    img.alpha_composite(t2)
    cyc = (k % 33) / 33
    thumb(img, PY + 400 + cyc * 650, min(1, 4 * (1 - cyc)) if cyc > .75 else min(1, cyc * 8))
    emit(img)

# D) 9.4-13s end card with finished earrings strip
fin = frame(210).crop((280, 60, 1000, 600)).resize((1080, 810), Image.LANCZOS)
for k in range(108):
    img = base(); img.paste(fin, (0, 620));
    veil = Image.new("RGBA", (W, H), INK + (150,)); img.alpha_composite(veil)
    img.alpha_composite(end); emit(img)

ff.stdin.close(); ff.wait()
print("ok")
