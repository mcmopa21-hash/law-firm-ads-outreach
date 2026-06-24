# Law Firm Google Ads Outreach Skill

## Trigger
Use this skill when asked to:
- "find law firms for outreach"
- "run daily prospecting"
- "analyze [domain] for outreach"
- "generate loom package for [firm]"
- "law firm outreach"
- "/law-firm-outreach"

---

## Context: Who You're Working For

You are assisting **Camila Parodi** (camilaparodi.com), a digital advertising consultant who runs **Revenue Leak Audits** for U.S. law firms ($3,500 / 7 days). Her entry point for cold outreach is analyzing a firm's Google Ads via the Transparency Center, then connecting that to the full funnel (intake, follow-up, signed cases).

**Her three case studies — match to prospect's practice area:**

| Practice Area | Result | Key Number |
|---|---|---|
| Bankruptcy | 5.2x → 9.8x ROI, same spend (~$2,380/mo) | October 2025: 15.9x ROI |
| Estate Planning | 17 → 47 signed clients (+176%), ad spend -22.9%, CPL $223 → $76 | Revenue +162.5% |
| Criminal Defense | 1.97x → 12.99x ROAS, same ~$1,770/mo spend | +557% ad-attributed revenue |

**Practice area mapping for unlisted areas:**
- Immigration / Family Law → Estate Planning case study (same lifecycle/family stakes)
- Personal Injury / DUI / Drug Charges → Criminal Defense (high-stakes, urgency-driven)
- Business / Debt / Financial → Bankruptcy
- When no match: lead with methodology + combined stats ("across my law firm clients...")

**Outreach philosophy:** Lead with one specific finding from their ads. Never open with a pitch. The Loom video is the value delivery — the connection note just gets it opened.

---

## Tools Available

**ads_extractor.py** — Python script at `~/.claude/skills/law-firm-outreach/ads_extractor.py`

Always run it using the venv Python:
```bash
/tmp/gads-test/bin/python3 ~/.claude/skills/law-firm-outreach/ads_extractor.py <command> <args>
```

If the venv doesn't exist, create it:
```bash
source ~/.local/bin/env && uv venv /tmp/gads-test && /tmp/gads-test/bin/pip install requests -q
```

Commands:
- `domain <domain>` → full ad analysis for one firm
- `search "<practice area> <city>"` → find firms by keyword
- `competitors "<practice area> <city>" --exclude <domain>` → find competitors

**WebSearch** — for finding decision makers and firm details

**Tracking log:** `~/.claude/skills/law-firm-outreach/outreach_log.json`
- Check before processing a firm (skip if already contacted or analyzed today)
- Append after generating each package

---

## Modes

### Mode 1: Analyze a specific domain
Triggered by: "analyze [domain]" or "generate loom package for [domain]"

### Mode 2: Daily prospecting batch
Triggered by: "find law firms for outreach", "run daily prospecting"
- Ask for: practice area + city (if not provided)
- Default batch size: 5 firms per run

---

## Step-by-Step Execution

### STEP 1 — Ensure extractor is ready

```bash
/tmp/gads-test/bin/python3 -c "import requests; print('ok')" 2>/dev/null || (source ~/.local/bin/env && uv venv /tmp/gads-test && /tmp/gads-test/bin/pip install requests -q && echo "installed")
```

---

### STEP 2 — Discover firms (Mode 2 only)

Ask Camila for practice area and city if not provided. Then run:

```bash
/tmp/gads-test/bin/python3 ~/.claude/skills/law-firm-outreach/ads_extractor.py search "<practice area> attorney <city>" --count 20
```

Filter results:
- `total_ads >= 5` — proxy for meaningful spend
- `last_active` within last 30 days (or unknown — include if uncertain)
- Skip any domain already in `outreach_log.json`

Select the 5 best candidates (highest ad count = highest spend signal).

For Mode 1 (specific domain), skip to Step 3 directly.

---

### STEP 3 — Full ad analysis (per firm)

```bash
/tmp/gads-test/bin/python3 ~/.claude/skills/law-firm-outreach/ads_extractor.py domain <domain>
```

Parse the output into a structured profile:
- **Name, domain, total ads, last active**
- **Headline(s)** — what they're leading with in search
- **Description(s)** — the offer/value prop they're using
- **LSA attributes** — Google Verified, Speaks Spanish, etc.
- **Practice areas advertised**
- **Ad format mix** — note search ads vs. search ads with image extensions vs. Local Services Ads. In the Transparency Center, law firm ads showing an "image" format are almost always **search ads with image extensions** (RSAs with image assets attached), NOT Google Display Network / GDN display ads. Never label them as display ads.

---

### STEP 4 — Find and analyze competitors (MANDATORY — do not skip)

This step is required before generating any Loom package. The competitor comparison is a core part of the outreach value — it shows Camila has done real market research, not just looked at one firm in isolation.

The Transparency Center search matches advertiser *names*, not keywords — so city-specific searches often return nothing. Use a two-step approach:

**Step 4a — Find local competitors via WebSearch:**
Search: `"[practice area] attorney [city]" google ads`
Also search: `[practice area] law firm [city]` to find 3–5 local firm websites.

**Step 4b — Run the extractor on each competitor domain:**
```bash
/tmp/gads-test/bin/python3 ~/.claude/skills/law-firm-outreach/ads_extractor.py domain <competitor_domain>
```
Run this for each of the 3–5 local competitors found. Skip any that return "not found."

The extractor now returns `image_urls` in its output. For each competitor with image ads, **download and read at least 2 images** to capture their actual headline, description, and visual approach:
```bash
curl -s -L -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" "<image_url>" -o /tmp/<firm>_ad01.jpg
```
Then Read the downloaded file to see the ad creative.

**Step 4c — Fallback to national competitors if local returns < 2:**
```bash
/tmp/gads-test/bin/python3 ~/.claude/skills/law-firm-outreach/ads_extractor.py search "<practice area> attorney" --count 10
```
Pick the 2 with the highest ad counts and run `domain` on them. Note in the Loom package that these are national competitors, not local.

**What to capture for each competitor:**
- Ad count (volume vs. target firm)
- Last active date (active vs. paused)
- Headline(s) read from images
- Description copy
- Whether they show star ratings / review count
- Whether they use personal attorney photos vs. stock
- Spanish-language presence
- Any obvious messaging mistakes (e.g., using contingency pricing language for a non-contingency practice)

**Minimum to proceed:** at least 10 ads analyzed in total across the target firm and its competitors combined. If the target firm has fewer than 10 ads, analyze 3 competitors fully to reach that threshold. Never generate the Loom package with fewer than 10 total ads reviewed.

---

### STEP 5 — Find the decision maker

Web search: `"[firm name]" managing partner OR "marketing director" site:linkedin.com`

Also try: `"[firm name]" "[city]" attorney partner`

Goal: name + LinkedIn URL of the person who controls the marketing budget. For small/mid firms this is almost always the founding or managing partner. For larger firms, there may be a dedicated marketing director.

If LinkedIn URL found: note it.
If not found: note "Decision maker: search manually for [Firm Name] + LinkedIn"

---

### STEP 6 — Generate the Loom Package

Produce a clean, copy-paste-ready Loom package with these sections:

---

**FIRM: [Name] | [Domain] | [City]**
**Decision maker:** [Name, title, LinkedIn URL or "search manually"]
**Practice area:** [area]
**Matched case study:** [which one and why]

---

**AD INTELLIGENCE SUMMARY**
- Total ads: [N] ([X] standard search / [Y] search+image extension / [Z] LSA) — last active [date]
- Search headlines: [list, or "not decoded"]
- Description: [text, or "not decoded"]
- LSA attributes: [list]
- Practice areas advertised: [list]
- Google badge: [Verified / Screened / none]

**GAPS IDENTIFIED** (pick the 2-3 most specific from this list — only include what's actually supported by the data):
- [ ] Single headline visible → RSAs should test 3–5 to let Google optimize
- [ ] Generic description (no differentiator vs. competitors)
- [ ] LSA attributes (Speaks Spanish / family-owned) not reflected in search ad copy
- [ ] No urgency language for high-stakes practice area (deportation, criminal charges, etc.)
- [ ] Image extensions only on some campaigns — ads without image extensions get lower CTR and visibility in competitive markets
- [ ] Social proof (star rating / review count) showing in one language campaign but absent from the other
- [ ] No location-specific headline (city/state not in visible copy)
- [ ] Competitor [name] running [X] more ads in same market

---

**LOOM VIDEO SCRIPT (3 min)**

*[0:00–0:15] Hook*
"I spent 20 minutes looking at your Google Ads through the Transparency Center — you're actively running [N] ads. I found [one specific thing]. Wanted to share it before I moved on."

*[0:15–1:00] What I See*
"Here's what's showing up publicly for [Firm Name]... [walk through: headline, description, LSA attributes, badge status]. The headline you're leading with is '[headline]'. The description is '[description]'. A few things stood out to me..."
[Name the 2–3 gaps — specific, not generic]

*[1:00–1:45] Competitor Framing*
"I also looked at [Top Competitor Name], who's running [N] ads in the same market. They're [one specific thing they're doing differently — more ads, different copy angle, etc.]. That gap matters because [why]."

*[1:45–2:30] Case Study Bridge*
"I worked with a [matched practice area] firm with a similar setup — [case study number]. What drove that wasn't a bigger budget. It was [tracking / lead quality / intake / copy — whichever matches the gap found]. That's exactly what I look for in the audit."

*[2:30–3:00] The Offer*
"I do a 7-day Revenue Leak Audit for $3,500. It traces your full path from ad click to signed case and hands you a prioritized plan. The discovery call is free — no commitment. I have a link below."

---

**LINKEDIN CONNECTION NOTE** (≤300 characters — verify length before output)

"[First name] — noticed your search ad leads with '[headline or key observation]' but [one specific gap]. Took a [practice area] firm from [case study number]. Worth 15 min? [or: wanted to flag it either way.]"

If no headline decoded: use LSA attribute or ad count observation instead.

---

**COMPETITOR INTEL**
| Competitor | Ads | Last Active | Headline Seen | Key Observation |
|---|---|---|---|---|
| [name] | [N] | [date] | [actual headline from image] | [e.g. stock photos only, no Spanish, paused 6mo] |
| [name] | [N] | [date] | [actual headline] | [observation] |
| [name] | [N] | [date] | [actual headline] | [observation] |

**Market position summary:** note whether the target firm is the dominant advertiser by volume, or being outspent. This determines the framing in the Loom script (conversion gap vs. visibility gap).

---

### STEP 7 — Log the firm

Append to `~/.claude/skills/law-firm-outreach/outreach_log.json`:

```json
{
  "date": "YYYY-MM-DD",
  "domain": "example.com",
  "firm_name": "Firm Name",
  "practice_area": "immigration",
  "decision_maker": "Name or unknown",
  "status": "package_generated",
  "loom_done": false,
  "linkedin_sent": false
}
```

Read the file first. If it doesn't exist, create it as an empty array `[]`. Append the new entry and write back.

---

### STEP 8 — Output summary

After processing all firms in a batch, output:

```
DAILY OUTREACH BATCH — [date]
================================
[N] firms analyzed

1. [Firm Name] ([domain]) — [practice area] — [N] ads
   Decision maker: [name or "search manually"]
   Top finding: [one sentence]
   Case study match: [which]
   LinkedIn note ready: YES

[repeat for each firm]

Next: Record Loom videos, then send connection notes.
Firms logged to outreach_log.json.
```

---

## Quality Rules

1. **Never invent ad copy.** Only reference headlines/descriptions that actually decoded from the extractor. If nothing decoded, say "search ad content not decoded — reference ad count and format mix instead."
2. **Never overclaim compliance.** Say "may create a compliance consideration" not "will get you disbarred."
3. **LinkedIn note must be ≤300 characters.** Count explicitly before outputting.
4. **Match case study to practice area.** Don't use the estate planning case study for a criminal defense firm.
5. **One specific finding per connection note.** Not a list. One thing.
6. **If extractor returns an error for a domain**, skip it and note "not found in Transparency Center — may not be running Google Ads."
