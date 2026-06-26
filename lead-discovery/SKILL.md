# Law Firm Lead Discovery Skill

## Trigger
- "find law firm leads"
- "run lead discovery"
- "prospect for law firms"
- "/lead-discovery"

---

## Context

This skill feeds the law-firm-outreach skill. It finds mid-to-large U.S. law firms likely to benefit from Camila Parodi's Revenue Leak Audit ($3,500 / 7 days), then populates the Google Sheet **"Law Firm Outreach Pipeline"** with firm details and decision maker contacts.

**Ideal prospect signals (any one qualifies):**
1. **High ad volume** — 30+ active Google Ads (large budget = the money is already there)
2. **Hiring for marketing** — job posting for Marketing Director/Manager/Coordinator (has budget, has pain)
3. **Marketing complaints** — partner or firm publicly expressing dissatisfaction with marketing ROI, lead quality, or ad performance
4. **Large established firm** — 10+ attorneys, active Google presence, but thin or poorly structured ad footprint

**Target practice areas:** immigration, criminal defense, personal injury, family law, bankruptcy, estate planning, DUI, employment law

**Target markets:** major U.S. cities — Atlanta, Miami, Houston, Dallas, Phoenix, Los Angeles, Chicago, New York, Seattle, Denver, Las Vegas, San Diego, Tampa, Philadelphia, Boston

---

## Tools

**ads_extractor.py** — verifies ad presence and volume:
```bash
/tmp/gads-test/bin/python3 ~/.claude/skills/law-firm-outreach/ads_extractor.py domain <domain>
```

**sheets.py** — all Google Sheet operations:
```bash
/tmp/gads-test/bin/python3 ~/.claude/skills/lead-discovery/sheets.py <command>
```

If venv is missing:
```bash
source ~/.local/bin/env && uv venv --clear /tmp/gads-test && /tmp/gads-test/bin/pip install requests gspread google-auth-oauthlib google-auth-httplib2 -q
```

---

## One-Time Google Sheets Setup

This only needs to be done once. After that, the token is cached and runs automatically.

1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Create a new project (or reuse one)
3. Enable **Google Sheets API** and **Google Drive API**
4. Go to **APIs & Services → Credentials → Create Credentials → OAuth client ID → Desktop app**
5. Download the JSON file → save it as `~/.claude/skills/lead-discovery/credentials.json`
6. Run `python3 ~/.claude/skills/lead-discovery/sheets.py init` — a browser tab will open to authorize
7. After authorizing, a `token.json` is saved. The sheet URL is printed.
8. Share the sheet URL with yourself and bookmark it.

---

## Execution — Step by Step

**Default batch: 10 new leads per run**
- 5 from Signal 1 (high ad volume via geographic search)
- 3 from Signal 2 (firms hiring for marketing)
- 2 from Signal 3 (marketing complaints or pain signals)

Adjust the mix based on what's available that day.

---

### STEP 1 — Ensure sheet is initialized

```bash
/tmp/gads-test/bin/python3 ~/.claude/skills/lead-discovery/sheets.py init
```

If it returns an error about credentials, prompt the user to complete the one-time setup above.

---

### STEP 2 — Signal 1: Geographic + practice area search

Run 3–4 WebSearches across different cities and practice areas. Rotate through cities and practice areas each run so you're not always hitting the same markets.

Example searches (pick 3–4 per run):
- `top immigration law firms atlanta georgia 10+ attorneys`
- `best criminal defense law firm houston texas large`
- `personal injury law firm miami florida established`
- `top family law attorneys dallas texas`
- `estate planning law firm chicago 2026`
- `immigration attorney los angeles established firm`
- `DUI defense attorney phoenix arizona`
- `employment law firm new york 2026`

For each search result, extract 3–5 firm websites. Then for each domain:

```bash
/tmp/gads-test/bin/python3 ~/.claude/skills/lead-discovery/sheets.py check-exists <domain>
```

If `{"exists": true}` — skip it.

If `{"exists": false}` — run:
```bash
/tmp/gads-test/bin/python3 ~/.claude/skills/law-firm-outreach/ads_extractor.py domain <domain>
```

**Threshold:** include in pipeline if `total_ads >= 10`. Prioritize `total_ads >= 30` (flag as "high volume" signal).

---

### STEP 3 — Signal 2: Firms hiring for marketing

Run 2 WebSearches:
- `"law firm" "director of marketing" OR "marketing manager" job opening 2026`
- `site:linkedin.com/jobs "law firm" marketing director OR manager 2026`

For each job posting found:
- Extract the firm name and find their website
- Run `check-exists` and `domain` extractor as above
- Set `discovery_signal` to: `"Hiring [job title] — source: [job board]"`
- Note: even firms with fewer than 10 ads qualify here — the hiring signal alone is enough (they have marketing budget intent)

---

### STEP 4 — Signal 3: Marketing pain expressions

Run 2 WebSearches:
- `site:reddit.com attorney OR "law firm" "google ads" "not working" OR "wasting money" OR "not getting calls"`
- `"law firm" marketing "ROI" OR "not converting" OR "struggling to get clients" 2025 OR 2026`

For any law firm named in results:
- Find their website
- Run `check-exists` and `domain` extractor
- Set `discovery_signal` to: `"Expressed marketing pain — source: [URL or platform]"`
- These qualify even with 0 ads (no ads + expressed pain = highest intent)

---

### STEP 5 — For each qualifying firm: find the decision maker

For each firm not already in the sheet with qualifying ad count or signal:

Run a WebSearch:
```
"[Firm Name]" managing partner OR "marketing director" site:linkedin.com
```

Also try:
```
"[Firm Name]" [city] attorney founding partner
```

Extract:
- **Decision maker name** — managing partner or marketing director (whoever controls marketing spend)
- **Title**
- **LinkedIn URL** — the direct profile URL if found

If LinkedIn URL not found, set `linkedin_url` to `"search manually: [Firm Name] LinkedIn"`

---

### STEP 6 — Write each qualifying firm to the sheet

For each firm, build the JSON and call:
```bash
/tmp/gads-test/bin/python3 ~/.claude/skills/lead-discovery/sheets.py add-lead '<json>'
```

JSON structure:
```json
{
  "firm_name": "Smith & Jones Immigration Law",
  "website": "smithjonesimmigration.com",
  "practice_area": "immigration",
  "city_state": "Atlanta, GA",
  "size_signal": "12 attorneys, established 2008",
  "discovery_signal": "38 active Google Ads — high volume signal",
  "ad_count": 38,
  "decision_maker": "James Smith",
  "title": "Founding Partner",
  "linkedin_url": "https://linkedin.com/in/jamessmith"
}
```

`discovery_signal` should be specific:
- `"38 active Google Ads — high volume"`
- `"Hiring Director of Marketing (LinkedIn, Jun 2026)"`
- `"Reddit post: 'our Google Ads are not converting' — r/legaladvice, May 2026"`
- `"10+ attorneys, 0 Google Ads presence — underinvested signal"`

---

### STEP 7 — Output summary

After the batch is complete, output:

```
LEAD DISCOVERY BATCH — [date]
================================
[N] leads added to sheet

1. [Firm Name] ([domain]) — [practice area] — [city]
   Signal: [discovery signal]
   Ads: [N] | Decision maker: [name or "search manually"]

[repeat for each lead]

Skipped (already in sheet): [N]
Not found in Transparency Center: [N]
Below threshold (< 10 ads, no other signal): [N]

Sheet: [URL]
Next: Run law-firm-outreach skill to process these leads.
```

---

## Quality Rules

1. **Never add a firm without a website.** Domain is the primary key for the outreach skill.
2. **Never fabricate ad counts.** Only report what the extractor returned.
3. **Never fabricate decision maker names.** If not found via search, write `"search manually"`.
4. **No duplicate domains.** Always `check-exists` before `add-lead`.
5. **Discovery signal must be specific.** "Large firm" is not a signal. "42 active Google Ads" is.
6. **Minimum 10 leads per batch** unless the search genuinely returns fewer qualifying firms — in that case, rotate to a different city/practice area combination.
