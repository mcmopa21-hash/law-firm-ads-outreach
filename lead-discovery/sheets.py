#!/usr/bin/env python3
"""
Google Sheets manager for the law firm outreach pipeline.

Sheet name: "Law Firm Outreach Pipeline"
Tab name:   "Leads"

Columns A-R:
  A  Date Added        B  Firm Name          C  Website
  D  Practice Area     E  City/State         F  Size Signal
  G  Discovery Signal  H  Ad Count           I  Decision Maker
  J  Title             K  LinkedIn URL       L  Status
  M  Areas of Oppty    N  Competitor Intel   O  LinkedIn Message
  P  Loom Script       Q  Loom Done          R  LinkedIn Sent

Usage:
  python3 sheets.py init
  python3 sheets.py check-exists <website>
  python3 sheets.py add-lead '<json>'
  python3 sheets.py get-new-leads
  python3 sheets.py update-row <website> '<json>'

Setup (one time):
  1. Go to console.cloud.google.com → New project → enable Google Sheets API + Google Drive API
  2. APIs & Services → Credentials → Create OAuth client ID → Desktop app → Download JSON
  3. Save as ~/.claude/skills/lead-discovery/credentials.json
  4. Run: python3 sheets.py init
     (browser popup → authorize → token cached at token.json → fully automated from here)
"""

import sys
import json
import os
from datetime import date

SHEET_NAME = "Law Firm Outreach Pipeline"
TAB_NAME = "Leads"
SKILLS_DIR = os.path.expanduser("~/.claude/skills/lead-discovery")
CREDS_FILE = os.path.join(SKILLS_DIR, "credentials.json")
TOKEN_FILE = os.path.join(SKILLS_DIR, "token.json")

HEADERS = [
    "Date Added", "Firm Name", "Website", "Practice Area", "City/State",
    "Size Signal", "Discovery Signal", "Ad Count",
    "Decision Maker", "Title", "LinkedIn URL", "Status",
    "Areas of Opportunity", "Competitor Intel",
    "LinkedIn Message", "Loom Script",
    "Loom Done", "LinkedIn Sent",
]

COL = {h: i + 1 for i, h in enumerate(HEADERS)}

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
]


def _auth():
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request

    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDS_FILE):
                print(json.dumps({
                    "error": "credentials.json not found",
                    "path": CREDS_FILE,
                    "setup": "See sheets.py docstring for setup instructions",
                }))
                sys.exit(1)
            flow = InstalledAppFlow.from_client_secrets_file(CREDS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "w") as f:
            f.write(creds.to_json())

    return creds


def _get_worksheet():
    import gspread
    from google.auth.transport.requests import Request

    creds = _auth()
    gc = gspread.authorize(creds)

    try:
        sh = gc.open(SHEET_NAME)
    except gspread.exceptions.SpreadsheetNotFound:
        sh = gc.create(SHEET_NAME)

    try:
        ws = sh.worksheet(TAB_NAME)
    except gspread.exceptions.WorksheetNotFound:
        ws = sh.add_worksheet(TAB_NAME, rows=2000, cols=len(HEADERS))
        ws.append_row(HEADERS)
        ws.format("A1:R1", {
            "textFormat": {"bold": True},
            "backgroundColor": {"red": 0.18, "green": 0.34, "blue": 0.68},
        })

    return ws, sh.url


def _normalize_domain(website):
    return (website.lower()
            .replace("https://", "").replace("http://", "")
            .replace("www.", "").rstrip("/").split("/")[0])


def cmd_init():
    ws, url = _get_worksheet()
    print(json.dumps({"status": "ok", "sheet_url": url, "tab": TAB_NAME}))


def cmd_check_exists(website):
    ws, _ = _get_worksheet()
    target = _normalize_domain(website)
    all_vals = ws.col_values(COL["Website"])
    for v in all_vals[1:]:
        if _normalize_domain(v) == target:
            print(json.dumps({"exists": True}))
            return
    print(json.dumps({"exists": False}))


def cmd_add_lead(lead_json):
    lead = json.loads(lead_json)
    ws, url = _get_worksheet()

    target = _normalize_domain(lead.get("website", ""))
    existing = ws.col_values(COL["Website"])
    for v in existing[1:]:
        if target and _normalize_domain(v) == target:
            print(json.dumps({"status": "skipped", "reason": "already in sheet", "firm": lead.get("firm_name", "")}))
            return

    row = [""] * len(HEADERS)
    row[COL["Date Added"] - 1]       = str(date.today())
    row[COL["Firm Name"] - 1]        = lead.get("firm_name", "")
    row[COL["Website"] - 1]          = lead.get("website", "")
    row[COL["Practice Area"] - 1]    = lead.get("practice_area", "")
    row[COL["City/State"] - 1]       = lead.get("city_state", "")
    row[COL["Size Signal"] - 1]      = lead.get("size_signal", "")
    row[COL["Discovery Signal"] - 1] = lead.get("discovery_signal", "")
    row[COL["Ad Count"] - 1]         = str(lead.get("ad_count", ""))
    row[COL["Decision Maker"] - 1]   = lead.get("decision_maker", "")
    row[COL["Title"] - 1]            = lead.get("title", "")
    row[COL["LinkedIn URL"] - 1]     = lead.get("linkedin_url", "")
    row[COL["Status"] - 1]           = "new"

    ws.append_row(row)
    print(json.dumps({"status": "added", "firm": lead.get("firm_name", ""), "sheet_url": url}))


def cmd_get_new_leads():
    ws, url = _get_worksheet()
    all_rows = ws.get_all_records()
    new_leads = [r for r in all_rows if r.get("Status", "").lower() == "new"]
    print(json.dumps({"leads": new_leads, "count": len(new_leads), "sheet_url": url}))


def cmd_update_row(website, data_json):
    data = json.loads(data_json)
    ws, url = _get_worksheet()

    target = _normalize_domain(website)
    all_rows = ws.get_all_records()

    row_idx = None
    for i, row in enumerate(all_rows, start=2):
        if _normalize_domain(row.get("Website", "")) == target:
            row_idx = i
            break

    if row_idx is None:
        print(json.dumps({"error": f"No row found for: {website}"}))
        return

    field_map = {
        "opportunities":     "Areas of Opportunity",
        "competitor_intel":  "Competitor Intel",
        "linkedin_message":  "LinkedIn Message",
        "loom_script":       "Loom Script",
        "status":            "Status",
    }

    updates = []
    for key, col_name in field_map.items():
        if key in data:
            col_letter = chr(64 + COL[col_name])
            updates.append({
                "range": f"{col_letter}{row_idx}",
                "values": [[data[key]]]
            })

    if updates:
        ws.batch_update(updates)

    print(json.dumps({"status": "updated", "row": row_idx, "firm": website, "sheet_url": url}))


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""

    if cmd == "init":
        cmd_init()
    elif cmd == "check-exists" and len(sys.argv) > 2:
        cmd_check_exists(sys.argv[2])
    elif cmd == "add-lead" and len(sys.argv) > 2:
        cmd_add_lead(sys.argv[2])
    elif cmd == "get-new-leads":
        cmd_get_new_leads()
    elif cmd == "update-row" and len(sys.argv) > 3:
        cmd_update_row(sys.argv[2], sys.argv[3])
    else:
        print("Usage: python3 sheets.py <init|check-exists|add-lead|get-new-leads|update-row>")
        sys.exit(1)
