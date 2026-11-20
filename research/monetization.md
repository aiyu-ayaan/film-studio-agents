# Making money with this stack

Checked 2026-11-20. Prices come from vendor and marketplace pages: treat as rough ranges, check live listings before quoting.

## Where the money is (ranked by our judgment)

| # | Offer | Skills | Why it sells | Typical price seen |
|---|---|---|---|---|
| 1 | SaaS / app launch and promo video, 15-60 s, from real UI | Shotcraft (Ink Press), Motionmaxxing, HyperFrames, Earshot | Every launch (Product Hunt, X, landing page) needs one. Founders pay fast. Your output is code, so revisions are cheap | Fiverr guide: animated explainers USD 168-1,260. AI-assisted launch studio (Flowjam): USD 245-995 for 15-60 s, 2-6 days. Mid studios: under USD 10,000 |
| 2 | Social cutdowns: 9:16 and 1:1 versions of the same film, captions | HyperFrames (`embedded-captions`) | Upsell on #1, near-zero extra work | Add 30-50% per extra format (our suggestion) |
| 3 | Narrated explainers in a distinct style (docs, onboarding, courses) | Lemo-Opuscar, Kokoro VO | 99 looks, original music from sample libraries, no stock costs | Same explainer range as #1 |
| 4 | 3D product or STEM visuals | 3DViz Pro Max | Fewer sellers, higher price | Premium over 2D (verify on live listings) |
| 5 | Own YouTube channel (STEM, tech explainers) | Lemo-Opuscar, 3DViz, HyperFrames | Slow to pay; risky under YouTube rules (below) | Ad revenue after YPP |

Our take: start with #1 and #2 as a service. It pays per job, builds a portfolio, and is not exposed to YouTube policy. Run #5 on the side only with real research in each video.

## 30-day start plan

1. Week 1: install the skills (`bin/setup-skills.sh all`). Make 3 spec launch videos for real open-source or indie products (label them "concept"). Different looks: Ink Press, a motionmaxxing idea film, a lemo style.
2. Week 2: post them on X/LinkedIn and a one-page portfolio. Open Fiverr and Contra gigs: "AI-crafted SaaS launch video, 48 h". Three tiers, e.g. 15 s / 30 s / 60 s.
3. Week 3: DM 20 founders a day who just launched (Product Hunt, X "launching today", Indie Hackers) with a 5 s preview made from their own site.
4. Week 4: raise prices after 3 reviews. Offer a monthly retainer (4 feature-update videos per month).

## Speed is the edge

- A HyperFrames/Shotcraft film is code: a revision is an edit, not a re-render from scratch. Offer unlimited small text revisions.
- Keep one `assets/brand/<client>/` per client so the next video starts at 50%.
- Track hours per project in `BRIEF.md` to find your real hourly rate.

## YouTube rules (if you run your own channel)

- YouTube's monetization policy page (<https://support.google.com/youtube/answer/1311392>) calls "inauthentic content" mass-produced or repetitive: "content that looks like it's made with a template with little to no variation across videos, or content that's easily replicable at scale". This includes "AI-generated content made with generic templates ... without adding the creator's original, authentic insights or perspective".
- Renamed from "repetitious content" around 2025-07-15. A July 2026 clarification (TechCrunch, 2026-07-20) lists three non-monetizable types: generic/repetitive/template content, off-putting or distressing content, and AI personas discussing sensitive topics like health and finance. Channels made of this content are removed from YPP.
- Disclose realistic synthetic content (YouTube "altered or synthetic content" setting).
- Rules for this studio: change the visual style between videos, write original research and a point of view into every script, no AI persona on health/finance, disclose synthetic voice when it sounds like a real person.

## Sources

- <https://www.fiverr.com/resources/guides/costs/2d-animation> (Fiverr cost guide)
- <https://www.flowjam.com/blog/affordable-launch-video-agency>, <https://www.flowjam.com/blog/saas-launch-video> (vendor pricing)
- <https://clutch.co/profile/studio-monday?page=2>
- <https://support.google.com/youtube/answer/1311392>
- <https://techcrunch.com/2026/07/20/youtube-clarifies-policies-around-ai-slop-and-upsetting-videos/>
- <https://techcrunch.com/2025/07/09/youtube-prepares-crackdown-on-mass-produced-and-repetitive-videos-as-concern-over-ai-slop-grows>
