# Roadmap: grow on Instagram Reels and YouTube (Shorts + long-form)

Researched 2026-11-21. Star counts and dates come from the GitHub API on that day.
No skill can promise a viral video. These skills raise the odds and make the feedback loop faster.

## 1. The four skills you sent, compared

| Skill | What it is | Stars / last push | Licence | Real tools (not just prompts) | Verdict |
|---|---|---|---|---|---|
| [Jakeschincariol/instagram-agent-skill](https://github.com/Jakeschincariol/instagram-agent-skill) | 13 skills: `/ig-reel`, `/ig-viral`, `/ig-caption`, `/ig-carousel`, `/ig-story`, `/ig-profile`, `/ig-plan`, `/ig-human`, `/ig-comment`, `/ig-reply`, `/ig-dm`, `/ig-repurpose`, `/ig-audit` | 7,795 / 2026-09-13 | MIT | `hookscore.py` (26 hook formulas, scored), `beats.py` (beat sheet timed at 165 wpm, flags hook > 3 s, beats > 4 s, missing loop), `caption.py` (shows the 125-char feed window, 5-hashtag cap), `swipe.py`, `humanize.py`/`detect.py` | **Install.** Best IG pack. Offline, no API key, never posts for you. |
| [jakeschincariol/youtube-agent-skill](https://github.com/jakeschincariol/youtube-agent-skill) | 11 skills: `/yt-script`, `/yt-package`, `/yt-edit`, `/yt-comment`, `/yt-plan`, `/yt-viral`, `/yt-retention`, `/yt-shorts`, `/yt-seo`, `/yt-chapters`, `/yt-audit` | 6,709 / 2026-09-16 | MIT | `hookscore.py` (21 formulas), `title.py` (title + thumbnail linted as a pair), `retention.py` (reads your retention CSV, finds the exact leave points), `deadair.py`, `chapters.py`, `swipe.py` | **Install.** Best YT pack. Honest about limits (says the hook scorer is a heuristic and tags barely matter). |
| [vyralcontent/content-skills](https://github.com/vyralcontent/content-skills) (the mcpservers.org link; that page returns 403, so the repo was read directly) | 7 knowledge skills: `viral-instagram-reels`, `viral-youtube-shorts`, `viral-tiktok-content`, `viral-hooks`, `viral-captions-and-ctas`, `viral-short-form`, `viral-short-form-ideas` | 270 / 2026-06-22 | MIT | None; reference docs only | **Install the two platform skills.** Best write-up of the 2026 Reels signals: sends per reach, Trial Reels, Original Content rules, 30-day recovery window. Fills a gap in Jake's IG pack. Install: `npx skills add vyralcontent/content-skills --skill viral-instagram-reels` (same for `viral-youtube-shorts`). |
| [agricidaniel/claude-youtube](https://github.com/agricidaniel/claude-youtube) | 1 orchestrator + 14 sub-skills (`/youtube audit, seo, script, hook, thumbnail, strategy, calendar, shorts, analyze, repurpose, monetize, competitor, metadata, ideate`) and 9 reference guides | 831 / 2026-04-10 | MIT | YouTube Data API scripts (channel stats, analytics via OAuth, competitor search), quota tracker, optional DataForSEO and NanoBanana MCPs | **Optional.** Overlaps Jake's YT pack. Worth it later for `/youtube strategy`, `/youtube monetize` and the `shorts-playbook.md` benchmarks. Needs an API key for live data. Its NanoBanana thumbnail option uses Gemini; keep it off unless you accept that. |

Others found by search, not recommended over the above: `aiskillstore/marketplace` `ai-social-media-content` (generic, multi-platform), `viral-reel-generator` (script only), Opus Clip clones on GitHub (clip long videos; we make originals, so less useful).

**Pick:** both Jake packs as the working tools, plus vyral's `viral-instagram-reels` and `viral-youtube-shorts` as the rulebook. Copy into `.agents/skills/` and symlink, per the "Add a new skill" steps in `CLAUDE.md`. They do not make video, so they sit before stage 1 (idea, hook, script) and after stage 8 (caption, title, posting, review) of `/film-studio`.

## 2. What the platforms reward (2026, as these skills report it)

Instagram Reels (from vyral `viral-instagram-reels` and Jake `/ig-*`):
- Watch time is the biggest signal. The first 3 seconds decide the seed test.
- **Sends per reach** buys new audience. A DM share counts roughly 3 to 5 times a like. End with "send this to the friend who ...", not "follow for more".
- Original content is enforced. No TikTok or CapCut watermarks. Reposts are cut from cold reach.
- Hashtags do not add reach. Use 3 to 5 at most. Keywords go in the caption's first line and on screen.
- Trial Reels (accounts over 1,000 followers) test a Reel on non-followers first. Use them for every risky idea.
- Only about 125 caption characters show before "... more".
- Reels is a discovery surface. Write every Reel for a stranger.

YouTube Shorts (from claude-youtube `shorts-playbook.md` and Jake `/yt-shorts`):
- Completion of 70% or more triggers wide promotion. "Viewed vs swiped away" below 50% means the hook is broken. 75% or more is good.
- Loops and replays are weighted heavily. End on a line that the first line answers.
- Change the picture about every 3 seconds. Hook in the first 1 to 3 seconds.
- Length peaks at about 13 s and 60 s. Tips: 15 to 20 s.
- Title: 4 to 6 words, 20 to 40 characters. Thumbnails do not matter in the Shorts feed.
- A Short can take off as late as day 4. Do not delete early.

YouTube long-form (Jake `/yt-package`, `/yt-retention`):
- Title and thumbnail are one unit. They must not say the same thing twice.
- Retention cliffs show you what to cut next time. Read the CSV after every upload.
- Channels that post both Shorts and long-form grow faster, though audience overlap is only about 10%.

## 3. Rules for this studio's films

- Our films are code-made, with synthetic voices (Kokoro / Pocket TTS). That counts as original content, but mark it: YouTube "altered or synthetic content" when realistic, and credit Kyutai for Pocket TTS. See `research/monetization.md`.
- Vertical master for Reels and Shorts: 1080x1920, 15 to 30 s, captions burned in through `/film-captions` (most people watch with sound off).
- First frame carries the on-screen hook text. No logo intro, no title card, no "hey guys".
- Last beat loops into the first line.
- Vary the look per video (the YouTube rule in `CLAUDE.md`). A recognisable series format is fine; identical templates are not. Since July 2026 YouTube demonetizes generic, repetitive, template content (`research/CLAUDE.md`, point 8), so every film needs its own research or human angle.
- Never automate the posting with browser bots or scraping. Jake's skills never post for you, and `/ig-viral` forbids crawlers. Posting by official API is covered in the earlier note (YouTube Data API, Instagram Graph API).

## 4. The roadmap

### Week 0: setup (1 day)
1. Install the two Jake packs and the two vyral skills into `.agents/skills/`, symlink them, and add registry rows to `CLAUDE.md` plus cards in `research/skills/`.
2. Fill `voice.md` once (Jake's template). Both packs read it. Save it at `~/.claude/instagram/voice.md` and `~/.claude/youtube/voice.md`.
3. Pick **one niche** and one promise ("3D explainers of how machines work in 30 seconds", for example). Niche clarity drives follows per view.
4. Run `/ig-profile` (scored out of 100) and fix the bio, name field and pinned posts. Set up the YouTube channel banner and description with `/yt-seo`.

### Weeks 1 to 2: research before making anything
1. Run `/ig-viral` and `/yt-viral` on 6 to 12 accounts: 4 direct, 4 adjacent, 2 to 4 big ones (big ones for format only). Stay within about 10x of your own size.
2. Rank by **outlier multiple** (views divided by that account's median). Keep only 3x and above. Copy the formula, never the video.
3. Output: a swipe file of 20 to 30 proven hook/structure patterns in your niche. Run it again monthly.

### Weeks 1 to 4: the production loop (each video)
1. **Idea:** pick one row from the swipe file.
2. **Hook:** `/ig-reel` or `/yt-script` writes 3 to 5 hooks. Keep the top scorer from `hookscore.py`, and only if it scores STRONG.
3. **Script:** time it with `beats.py --target 30`. Fix any beat over 4 s. Make sure the end loops.
4. **Make it:** `/film-studio` with the script, vertical master, captions on. Earshot and loudness gate as usual.
5. **Package:** `/ig-caption` (keyword in the first 125 characters, one send-prompt, 3 to 5 hashtags). `/yt-package` for the Shorts title. `/ig-human` on all text.
6. **Post:** Instagram as a Trial Reel first once over 1,000 followers. Same video to YouTube Shorts. Optionally TikTok.
7. **Engage:** for the first hour, `/ig-reply` and `/yt-comment` handle the comment threads. Pin one comment.

Cadence target: 5 Shorts/Reels a week plus 1 long-form every 1 to 2 weeks (Jake's `/yt-plan`: "one anchor, one cheap one, three Shorts"). A 30-second film from this studio is the bottleneck, so build reusable scene templates in week 1.

### Weekly review (30 minutes, every Sunday)
1. `/ig-audit`: rank posts by outlier multiple against your own median, and by sends per reach (not views).
2. `/yt-retention` on each YouTube export: where people left, and what was on screen at that second.
3. Write down one change for next week. One, not ten.

Numbers to watch:

| Metric | Healthy | Action if low |
|---|---|---|
| YT Shorts viewed vs swiped away | 75% or more | Below 50%: rewrite the first line and first frame |
| YT Shorts average % viewed | 70% or more | Cut the length; shorten the slowest beat |
| IG 3-second hold / skip rate | Low skip rate | Rewrite on-screen hook text |
| IG sends per reach | Rising | Rewrite the payoff so it is "for" one specific person |
| Follows per 1,000 views | Rising | Niche not legible in the first second; state the topic on screen |

### Months 2 to 3: double down
1. Remake your top 3 outliers with a new angle ("part 2", the same formula on a new topic). Winners repeat.
2. `/yt-shorts` and `/ig-repurpose`: cut long-form into Shorts with new first lines.
3. Add `/ig-carousel` posts from your best scripts. Carousels earn saves and sends cheaply.
4. Start long-form on the topics where Shorts got the best follows per view.
5. Optional: add agricidaniel's `/youtube strategy` and `/youtube monetize` once the channel has data. YouTube Partner Program starts at 1,000 subscribers plus 4,000 watch hours or 10 million Shorts views in 90 days (check the current rules in `research/monetization.md`).

### Month 3 onward: automate the boring parts
1. Script the upload step with the official APIs (YouTube Data API `videos.insert`, Instagram Graph API Reels container flow). Keep a human "ship it?" check before each post.
2. Keep the monthly `/ig-viral` / `/yt-viral` refresh. Formulas last about a season.

## 5. What this roadmap does not promise

- No view numbers. Most posts will be average. Growth comes from the few outliers, and the loop above is how you find and repeat them.
- Benchmarks above are the skills' claims, not verified against platform docs. Re-check them every quarter and date any change here.
