# Law Firm Google Ads Outreach Skill

A Claude Code skill that automates the research and package-generation phase of cold outreach to U.S. law firms via Google Ads analysis.

Built for a Revenue Leak Audit consulting practice targeting law firms spending $10K+/month on marketing.

---

## What It Does

For each target law firm, this skill:

1. **Pulls their Google Ads** from the public Transparency Center — no API key required
2. **Decodes their actual ad content** — search headlines, descriptions, LSA attributes (Speaks Spanish, Google Verified, etc.), practice areas advertised
3. **Finds local competitors** and analyzes their ads too — gives you the comparison angle
4. **Identifies the decision maker** (managing partner / marketing director) via LinkedIn
5. **Generates a ready-to-record Loom script** — 3 minutes, timestamped, referencing their specific ads and a matched case study
6. **Writes the LinkedIn connection note** — one specific finding, one result reference, under 300 characters
7. **Logs every firm** to `outreach_log.json` so you never contact the same firm twice

**Minimum standard:** at least 10 ads analyzed per package (target firm + competitors combined) before generating anything.

---

## Files

| File | Purpose |
|---|---|
| `SKILL.md` | The Claude Code skill — orchestrates the full 8-step pipeline |
| `ads_extractor.py` | Python tool that queries the Google Ads Transparency Center |
| `requirements.txt` | Python dependencies (`requests`) |
| `outreach_log.example.json` | Schema for the tracking log |

---

## Installation

### 1. Install Python dependency

```bash
# If you have uv installed (recommended):
uv venv /tmp/gads-test
/tmp/gads-test/bin/pip install requests

# Or with pip directly:
pip install requests
```

### 2. Install uv (if needed)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.local/bin/env
```

### 3. Copy the skill to your Claude skills directory

```bash
mkdir -p ~/.claude/skills/law-firm-outreach
cp SKILL.md ads_extractor.py ~/.claude/skills/law-firm-outreach/
```

### 4. (Optional) Install the Google Ads Transparency MCP

The skill uses the Python extractor directly, but you can also add the MCP for interactive Claude sessions:

```bash
claude mcp add google-ads-transparency -- uvx google-ads-transparency-mcp
```

---

## Usage

### Analyze a specific firm

In Claude Code, run:
```
analyze tadeosilvalaw.com for outreach
```

Or invoke the extractor directly:
```bash
/tmp/gads-test/bin/python3 ads_extractor.py domain tadeosilvalaw.com
```

### Find firms by practice area and city

```
find law firms for outreach
```

Claude will ask for a practice area and city, then return 5 firms with full packages.

Or directly:
```bash
/tmp/gads-test/bin/python3 ads_extractor.py search "immigration attorney"
```

### Find competitors

```bash
/tmp/gads-test/bin/python3 ads_extractor.py competitors "immigration attorney" --exclude tadeosilvalaw.com
```

---

## Extractor Output (domain analysis)

```json
{
  "domain": "tadeosilvalaw.com",
  "name": "Tadeo & Silva, LLC",
  "total_ads": 25,
  "image_ads": 21,
  "text_ads_decoded": 2,
  "last_active": "2026-06-23",
  "lsa_attributes": ["Professional service", "Speaks Spanish"],
  "practice_areas": ["asylum", "citizenship", "deportation"],
  "badges": ["Verified"],
  "headlines": ["Marriage Based Immigration", "Family-owned & operated", "Locally-owned & operated"],
  "descriptions": ["Get an immigration consultation with Tadeo & Silva. Find out your best options today."]
}
```

---

## Technical Notes

### Why a custom extractor instead of the existing MCP?

The `block-town/google-ads-transparency-mcp` package has a silent bug in its `_extract_ad_link` function: it attempts multiple key paths to find the preview URL, but the outer `try/except` exits on the first `KeyError` without trying fallback paths. This causes all text/search ads to return empty content.

This extractor fixes that by wrapping each key path attempt individually, and also handles both `overlay=` and `assets=` encoded parameters (gzip + base64 encoded protobuf), which the original tool doesn't support.

### Ad content decoding

Google encodes search ad content in the `overlay=` or `assets=` query parameter of preview URLs. The encoding is: gzip compression → base64 (URL-safe) → URL encoding. After decompression, the binary contains length-prefixed UTF-8 strings that include ad copy, LSA attributes, practice area tags, and badge status.

---

## Tracking Log

Copy `outreach_log.example.json` to `~/.claude/skills/law-firm-outreach/outreach_log.json` to initialize tracking. The skill appends a new entry for every firm processed and skips firms already in the log on subsequent runs.

---

## Related Skills

- [linkedin-writer](https://github.com/sergebulaev/linkedin-skills) — for LinkedIn content
- [claude-skills-linkedin](https://github.com/claude-dev-code/claude-skills-linkedin) — for sending outreach messages (requires LinkupAPI)
- [sales-skills/sales](https://github.com/sales-skills/sales) — for prospect lists and enrichment
