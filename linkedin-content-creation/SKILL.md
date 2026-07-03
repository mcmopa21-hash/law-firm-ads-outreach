# LinkedIn Content Creation Skill

## Trigger
Use this skill when asked to:
- "write a linkedin post"
- "create linkedin content"
- "draft a post about [topic]"
- "turn this into a linkedin post"
- "/linkedin-content"

---

## Context: Who You're Writing For

You are writing LinkedIn content for **Camila Parodi** (camilaparodi.com), a digital advertising consultant who runs **Revenue Leak Audits** for U.S. law firms ($3,500 / 7 days). Her audience is law firm owners, managing partners, and marketing directors — people who control (or influence) the ad budget.

Her proof points (pull from these, don't fabricate new ones):

| Practice Area | Result | Key Number |
|---|---|---|
| Bankruptcy | 5.2x → 9.8x ROI, same spend (~$2,380/mo) | October 2025: 15.9x ROI |
| Estate Planning | 17 → 47 signed clients (+176%), ad spend -22.9%, CPL $223 → $76 | Revenue +162.5% |
| Criminal Defense | 1.97x → 12.99x ROAS, same ~$1,770/mo spend | +557% ad-attributed revenue |

Content pillars to draw from: Google Ads Transparency Center findings (what law firms get wrong publicly), the Revenue Leak Audit methodology, myths about legal marketing ROI, behind-the-scenes of client work (anonymized unless case study is named above), and reactions to what she's seeing in the law firm ads outreach / lead discovery work itself.

---

## Core Content Principles (non-negotiable — check every draft against these)

These are the rules the writing process is built around. Do not skip them for the sake of speed.

### 1. POV storytelling beats industry takes
A disengaged "here's what's happening in legal marketing" take loses to a specific point of view told through a story. Every post must **educate (without boring), inspire, or entertain** — pick one primary lane. If a draft doesn't make the reader feel something (curious, seen, validated, provoked), it's not ready.

### 2. Content is a bank account — deposit before you withdraw
- **Deposit** = educate, inspire, entertain. Pure value, no ask.
- **Withdrawal** = the pitch, the offer, the ask to book a call.
- All-withdrawal posts put the account in debt with the audience. All-deposit posts leave opportunity on the table. Balance is the strategy.
- Classify every post into the funnel before writing:
  - **TOFU** (top of funnel) — pure deposit. Broad-audience reach content. No CTA beyond engagement (a question, an invite to share their view).
  - **MOFU** (middle) — deposit-heavy but ties the lesson back to Camila's methodology or a named result. Soft CTA (follow, save, "DM me if X").
  - **BOFU** (bottom) — the withdrawal. Case study + direct offer (book the audit / discovery call).
- Default cadence unless told otherwise: **roughly 4 TOFU/MOFU deposits for every 1 BOFU withdrawal.**

### 3. Write reach content first, not ICP-only content
Content written narrowly for "law firm managing partners" often never reaches law firm managing partners — the algorithm and the audience both need broader pull-in first. TOFU and MOFU posts should be framed so a wider marketing/business audience finds them relatable (e.g., "why most professional services firms waste ad spend"), with the law-firm specificity woven in as the proof, not the gate. Let the right people self-select in comments/DMs rather than writing only to a narrow ICP from line one.

### 4. Engagement is not optional
Posting alone does not drive growth — the algorithm rewards reciprocity, and so do people. Every time this skill produces a post, also produce:
- 3–5 **target accounts/threads to engage with** that day (competitors' followers, law firm marketing groups, relevant hashtags) with a note on what angle to comment with.
- This is a required output, not an afterthought — treat it as part of "the post," not a separate task that gets skipped.

### 5. The hook is everything
Nine times out of ten, an underperforming post is a hook problem — not the topic, not the timing, not "the algorithm." The first line must:
- Create a curiosity gap, a bold/contrarian claim, or an immediate stake — never a generic scene-setter ("Let's talk about...", "I've been thinking about...").
- Be readable and complete before the "see more" cutoff (~2 lines / ~200 characters).
- Get rewritten 3+ ways before picking the final one. Always present at least 2 hook alternatives when drafting.

### 6. The ending matters as much as the hook (bookend structure)
Never close with a flat, low-effort prompt like "Thoughts?" Structure every post like a TED talk:
1. **Open with the story** (the hook/scene).
2. **Build to the point** (the lesson, the number, the reframe).
3. **Return to the story at the end** — close the loop opened in the hook, then land the CTA or takeaway inside that closure.
Start strong, close stronger — the ending is where the ask or the memorable line lives, not a throwaway sign-off.

### 7. This only works with a system — don't rely on inspiration
Never draft from a blank page in the moment. The workflow below (idea capture → funnel classification → draft → engagement plan) exists specifically so that "showing up when inspiration strikes" is never the strategy. If there's no idea backlog, build one before writing (see Step 1).

---

## Tools Available

**WebSearch** — for sourcing timely law firm marketing news, competitor moves, or trend hooks to react to.

**Idea backlog:** `~/.claude/skills/linkedin-content-creation/content_ideas.json` — running list of raw ideas, observations, and story fragments collected between writing sessions. Check this first before starting from scratch.

**Content log:** `~/.claude/skills/linkedin-content-creation/content_log.json` — tracks every post drafted: date, funnel stage (TOFU/MOFU/BOFU), hook used, and status (drafted/posted). Used to keep the funnel ratio balanced and avoid repeating angles.

---

## Step-by-Step Execution

### STEP 1 — Idea capture (system, not inspiration)
Check `content_ideas.json` for unused ideas. If empty or thin, generate 5–10 raw ideas from: recent law firm ads outreach findings (this repo's other skills), a WebSearch on current legal marketing pain points, or a specific topic the user provides. Log new ideas even if not used today — the backlog is the system.

### STEP 2 — Classify the funnel stage
For the idea being written today, decide TOFU / MOFU / BOFU per the definitions in Principle 2. Check `content_log.json` to see the last several posts' stages — if the last 3–4 were all deposits with no withdrawal (or vice versa), let that inform today's pick.

### STEP 3 — Draft the hook (2–3 alternatives)
Write 2–3 candidate first lines per Principle 5. Flag which one is strongest and why.

### STEP 4 — Draft the body using the bookend structure
Story → point → return to story → close (Principle 6). Educate, inspire, or entertain — pick the primary lane and don't blend all three thinly. If MOFU/BOFU, tie the point to Camila's methodology or a named case study — never fabricate a number not in the table above.

### STEP 5 — Write the CTA appropriate to the funnel stage
- TOFU: engagement-only (a real question, not "thoughts?").
- MOFU: soft CTA (follow/save/DM).
- BOFU: direct offer (Revenue Leak Audit / discovery call), one clear next step.

### STEP 6 — Produce the engagement plan
Per Principle 4, list 3–5 specific accounts/posts/communities to engage with the day this posts, with the angle for each comment.

### STEP 7 — Log it
Append the post (funnel stage, hook, topic, date) to `content_log.json`, and remove the used idea from `content_ideas.json`.

### STEP 8 — Output
Present:
1. The 2–3 hook options with a recommendation
2. The full post (using the recommended hook)
3. Funnel stage classification
4. The engagement plan (3–5 targets + angle)

---

## Quality Rules

1. **Every post must pick a lane**: educate, inspire, or entertain. If it tries to do all three shallowly, cut it back to one.
2. **Never skip the deposit/withdrawal check.** A BOFU post with no recent deposits posted is not ready — flag it.
3. **Never write a generic hook or a "Thoughts?" close.** Both are automatic rewrite triggers.
4. **Never fabricate case study numbers.** Only use the results in the table above, or clearly-labeled anonymized/hypothetical framing if no real data fits.
5. **Never skip the engagement plan.** It ships with the post, every time — not optional, not a follow-up task.
6. **Broad-reach framing for TOFU/MOFU.** Don't write narrowly to "law firm partners" in the hook — let the specificity live in the proof, not the gate.
7. **Log every post.** The system (backlog + log) is what makes this repeatable — skipping it defeats Principle 7.
