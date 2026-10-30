# Anekant Tech — Instagram playbook (@anekant.tech)

Account owner: Yash Dhoka, founder of Anekant Tech (https://anekant.tech), Pune, India.
Anekant builds bespoke websites (incl. 3D / scrollytelling product pages), Flutter apps, custom software,
custom ERP, custom CRM, headless CMS and UI/UX design systems, with zero vendor lock-in.

**Goal:** inbound leads from the **US and Europe** (founders, ops leads, marketing heads at brands and
mid-size businesses). Every post ends with a soft DM call to action ("DM us “ERP”", "DM us “SCROLL”"…).

## Test month: 2 Nov – 29 Nov 2026
3 posts a week (Tue / Thu / Sat), all created in Metricool as **drafts** (`"draft": true`) for Yash to approve.
Variables being tested — keep them balanced so the month-end review can compare:
- **Format:** Reels vs carousels (aim ~1 Reel + 2 carousels a week).
- **Time (IST):** 18:30 (UK/EU afternoon, US East morning) vs 21:30 (UK/EU evening, US East lunchtime).
- **Topic cluster:** showcase/craft · decision guides (ERP, CRM, CMS, apps) · web performance & SEO.

| Week | Tue | Thu | Sat |
|---|---|---|---|
| 1 (3–7 Nov) ✅ done | Reel: Emerald Earring, 210 frames — 18:30 | Carousel: Custom ERP build vs buy, 5 questions — 21:30 | Carousel: What is scrollytelling? — 18:30 |
| 2 (10–14 Nov) | Carousel: Flutter vs React Native — 21:30 | Reel (text): Core Web Vitals, "your site has 2.5 seconds" — 18:30 | Carousel: How to write a software brief — 21:30 |
| 3 (17–21 Nov) | Carousel: Headless CMS vs WordPress — 18:30 | Carousel: WhatsApp Business API inside your CRM — 21:30 | Reel: Emerald Earring "how a frame sequence works" (frames + text scenes) — 18:30 |
| 4 (24–28 Nov) | Reel (text): 5 signs your website is losing buyers — 21:30 | Carousel: App maintenance after launch — 18:30 | Carousel: Zero vendor lock-in, what you should own — 21:30 |

Source material: the Insights articles at https://anekant.tech/insights (also in the private repo
YashmDhoka/anekant_website under web/insights/<slug>/index.html). Showcase: only the **Emerald Earring**
demo is live (https://anekant.tech/samples/emerald-earring); Berry Soda, Perfume, Ring and House now redirect
to /samples — do not promote them. Emerald frames: anekant_website/assets/emerald_earring/ezgif-frame-001…210.png
(1280x720). They carry a small sparkle mark bottom-right — always crop it out (centre crop x=280..1000).
Posts that use these frames are set `isAiGenerated: true`.

## Visual style (matches the website)
Paper #EFECE4, ink #0D0D0D, muted #6B675E, signal orange #FF4415, font Manrope (ExtraBold 800 for
headlines). Neo-brutalist: 3px rules, hard offset shadows, big orange numbers, dark final CTA slide.
- Carousels: `python3 _tools/render_carousel.py deck.json outdir` → 1080x1350 JPGs. See `_tools/example-*.json`
  (deck = {slug, tag, slides:[{html, dark?}]}; classes: kicker, h1, h2, p, num, card, rows/row, cta).
  6–8 slides: cover hook → one idea per slide → dark CTA slide.
- Text Reels: `python3 _tools/make_text_reel.py scenes.json out.mp4` → 1080x1920 MP4 + out.jpg cover.
  4–6 scenes, 2–3 s each, 10–18 s total.
- Always look at a contact sheet of the rendered output before uploading.

## Hosting + scheduling
1. Put media in this repo under `social/YYYY-MM-wN/`, commit and push to `main`.
2. Public URL: `https://raw.githubusercontent.com/YashmDhoka/image-html/main/social/<folder>/<file>` (curl it to confirm 200).
3. Metricool brand id **7751624**, timezone **Asia/Kolkata**. `createScheduledPost` with `draft: true`,
   providers `[{"network":"instagram"}]`, `instagramData.type` POST (carousel) or REEL (+ `videoThumbnailUrl`).
   Metricool copies the media to its own storage.

## Captions
120–220 words. Strong first line with one emoji, short paragraphs, a "Swipe for…" line on carousels,
"link in bio" instead of links, a DM keyword CTA, "Save this" where useful, 8–10 hashtags at the end
(mix of broad and niche, always #anekanttech). Plain, specific, honest. Never invent client names,
numbers, results or anecdotes.
Don't talk about "frames" or frame counts when describing the scroll pages; describe them as smooth and scroll-driven (Yash's preference).
