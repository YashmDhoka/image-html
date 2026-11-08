# Anekant Tech — Instagram playbook (@anekant.tech)

Account owner: Yash Dhoka, founder of Anekant Tech (https://anekant.tech), Pune, India.
Anekant builds bespoke websites (incl. 3D / scrollytelling product pages), Flutter apps, custom software,
custom ERP, custom CRM, headless CMS and UI/UX design systems, with zero vendor lock-in.

**Goal:** inbound leads from the **US and Europe** (founders, ops leads, marketing heads at brands and
mid-size businesses). Every post ends with a soft DM call to action ("DM us “ERP”", "DM us “SCROLL”"…).

## Test month: 31 Oct – 29 Nov 2026
**Exactly 3 posts a week — one each on Saturday, Tuesday and Thursday, never on other days and never two on the same day** (Yash, 6 Nov). Each "week" below runs Sat → Thu.
**Since 6 Nov all posts PUBLISH AUTOMATICALLY** (`"draft": false`). Yash chose this after week 1's drafts were
never approved and nothing went out. The Sunday task messages him the coming posts so he can ask for changes
or cancel one before it's due.
Variables being tested — keep them balanced so the month-end review can compare:
- **Format:** Reels vs carousels (aim ~1 Reel + 2 carousels a week).
- **Time (IST):** 18:30 (UK/EU afternoon, US East morning) vs 21:30 (UK/EU evening, US East lunchtime).
- **Topic cluster:** showcase/craft · decision guides (ERP, CRM, CMS, apps) · web performance & SEO.

| Week | Sat | Tue | Thu |
|---|---|---|---|
| 1 (31 Oct, 3 & 5 Nov) | Reel: Emerald Earring, "Smooth. Scroll-driven." — 18:30 (published; 32 views) | ⚠️ not published (drafts never approved) | ⚠️ not published |
| 2 (7, 10 & 12 Nov) ✅ scheduled | Trial Reel v3 "This product page has no video in it" (phone mockup, sound) — 18:30 (⚠️ FAILED: Trial Reel follower requirement) | Carousel: Flutter vs React Native — 18:30 | Trial Reel (text, motion + sound): Core Web Vitals, "your site has 2.5 seconds" — 21:30 |
| 3 (14, 17 & 19 Nov) ✅ scheduled | Carousel: Custom ERP build vs buy, 5 questions — 18:30 | Carousel: What is scrollytelling? — 21:30 | Carousel: How to write a software brief — 21:30 |
| 4 (21, 24 & 26 Nov) | Carousel: Headless CMS vs WordPress — 21:30 | Trial Reel (text): 5 signs your website is losing buyers — 18:30 | Carousel: WhatsApp Business API inside your CRM — 21:30 |
| 5 (28 Nov, 1 & 3 Dec) | Carousel: Zero vendor lock-in, what you should own — 18:30 | Trial Reel (text): App maintenance after launch, what nobody budgets for — 21:30 | Fresh topic |

Source material: the Insights articles at https://anekant.tech/insights (also in the private repo
YashmDhoka/anekant_website under web/insights/<slug>/index.html). Showcase: only the **Emerald Earring**
demo is live (https://anekant.tech/samples/emerald-earring); Berry Soda, Perfume, Ring and House now redirect
to /samples — do not promote them. Emerald frames: anekant_website/assets/emerald_earring/ezgif-frame-001…210.png
(1280x720). They carry a small sparkle mark bottom-right — always crop it out (centre crop x=280..1000).
Posts that use these frames are set `isAiGenerated: true`.

## Reach rules (added 1 Nov after the first Reel got ~30 views)
The account is new (≈10 followers), so Instagram has little signal on who to show posts to.
- ⚠️ **8 Nov:** the 7 Nov Trial Reel failed in Metricool: "The instagram account does not meet the trial reel follower
  requirement to create trial reels." The 12 Nov Trial Reel will fail the same way. Reported to Yash; awaiting his call on
  switching Reels to `instagramData.type: "REEL"` until the account qualifies.
- **Every Reel is a Trial Reel** (`instagramData.type: "TRIAL_REEL"`): Instagram shows it to non-followers first.
  Yash can share a well-performing one to his followers from the Instagram app.
- **Hook in the first second.** Scene 1 / frame 1 must stop the scroll: a bold claim, question or number in big
  text, over the most striking visual (finished product, never a slow build-up). No logo intros.
- **Every Reel has sound.** Library music via Metricool is blocked until @anekant.tech is linked to a Facebook
  Page (API returns 403), so Reels carry an original ambient soundtrack (`_tools/soundtrack.py`, used
  automatically by `make_text_reel.py`; vary the seed per Reel). If Yash links a Facebook Page, add
  `instagramData.audioConfiguration.audioId` with a search term instead.
- **Motion, not slideshows:** text Reels use the slow push-in + progress bar + optional `timer` counter built
  into `make_text_reel.py`. Showcase Reels use the phone mockup with a scroll gesture
  (`_tools/reel_phone/make_phone_reel.py`), so "scroll-driven" is obvious without sound or captions.
- **12–16 s**, ending on a clear DM keyword card.
- **Search-friendly captions:** first two lines and on-screen text use phrases buyers type
  ("luxury product page", "Shopify jewellery website", "custom ERP", "website speed"); hashtags are secondary.

## Visual style (matches the website)
Paper #EFECE4, ink #0D0D0D, muted #6B675E, signal orange #FF4415, font Manrope (ExtraBold 800 for
headlines). Neo-brutalist: 3px rules, hard offset shadows, big orange numbers, dark final CTA slide.
- Carousels: `python3 _tools/render_carousel.py deck.json outdir` → 1080x1350 JPGs. See `_tools/example-*.json`
  (deck = {slug, tag, slides:[{html, dark?}]}; classes: kicker, h1, h2, p, num, card, rows/row, cta).
  6–8 slides: cover hook → one idea per slide → dark CTA slide.
- Text Reels: `python3 _tools/make_text_reel.py scenes.json out.mp4 SEED` → 1080x1920 MP4 with soundtrack
  + out.jpg cover. 5–6 scenes, 2.4–3 s each, 12–16 s total. Optional `"timer": N` on a scene animates a counter.
  Example: `2026-11-w2/cwv-v2.json`.
- Showcase Reels (Emerald Earring): adapt `_tools/reel_phone/make_phone_reel.py` (hook on finished earrings →
  phone with thumb scrolling → rewind → DM card), then add sound with `_tools/soundtrack.py` + ffmpeg.
- Re-uploading a changed file: use a NEW filename (raw.githubusercontent.com caches old versions for minutes).
- Always look at a contact sheet of the rendered output before uploading.

## Hosting + scheduling
1. Put media in this repo under `social/YYYY-MM-wN/`, commit and push to `main`.
2. Public URL: `https://raw.githubusercontent.com/YashmDhoka/image-html/main/social/<folder>/<file>` (curl it to confirm 200).
3. Metricool brand id **7751624**, timezone **Asia/Kolkata**. `createScheduledPost` with `draft: false` (auto-publish),
   providers `[{"network":"instagram"}]`, `instagramData.type` POST (carousel) or TRIAL_REEL (+ `videoThumbnailUrl`).
   Metricool copies the media to its own storage.

## Captions
120–220 words. Strong first line with one emoji, short paragraphs, a "Swipe for…" line on carousels,
"link in bio" instead of links, a DM keyword CTA, "Save this" where useful, 8–10 hashtags at the end
(mix of broad and niche, always #anekanttech). Plain, specific, honest. Never invent client names,
numbers, results or anecdotes.
Don't talk about "frames" or frame counts when describing the scroll pages; describe them as smooth and scroll-driven (Yash's preference).
