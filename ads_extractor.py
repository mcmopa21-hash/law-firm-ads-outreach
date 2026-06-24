#!/usr/bin/env python3
"""
Google Ads Transparency Center extractor for law firm outreach.

Usage:
  python ads_extractor.py domain <domain>
  python ads_extractor.py search "<practice area> <city>" [--count N]
  python ads_extractor.py competitors "<practice area> <city>" [--exclude <domain>]
"""

import sys
import json
import gzip
import base64
import re
import argparse
from urllib.parse import parse_qs, urlparse, unquote

try:
    import requests
except ImportError:
    print(json.dumps({"error": "requests not installed. Run: pip install requests"}))
    sys.exit(1)

HEADERS = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "accept-language": "en-US,en;q=0.9",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}
BASE = "https://adstransparency.google.com"


def get_session():
    s = requests.Session()
    s.headers.update(HEADERS)
    s.get(BASE, timeout=10)
    return s


# ---------- Ad content decoding ----------

def decode_ad_param(url):
    """Decode overlay= or assets= param from a preview URL (gzip + base64 encoded protobuf)."""
    if not url:
        return []
    params = parse_qs(urlparse(url).query)
    for key in ["overlay", "assets"]:
        vals = params.get(key)
        if not vals:
            continue
        raw_val = unquote(vals[0]).lstrip("=")
        padded = raw_val.replace("-", "+").replace("_", "/")
        padded += "==" * ((4 - len(padded) % 4) % 4)
        try:
            raw = gzip.decompress(base64.b64decode(padded))
            strings = re.findall(rb"[\x20-\x7e]{4,}", raw)
            results = []
            for sv in strings:
                t = sv.decode("ascii", errors="ignore").strip()
                if (
                    len(t) >= 4
                    and "%" not in t
                    and not re.match(r"^[A-Za-z0-9+/=]{20,}$", t)
                    and sum(c.isalpha() for c in t) > len(t) * 0.3
                ):
                    results.append(t)
            return results
        except Exception:
            continue
    # Fallback: try ad= param (RSA variant)
    ad_param = params.get("ad", [None])[0]
    if ad_param:
        try:
            raw = base64.b64decode(ad_param + "==")
            strings = re.findall(rb"[\x20-\x7e]{4,}", raw)
            results = []
            for sv in strings:
                t = sv.decode("ascii", errors="ignore").strip()
                if len(t) >= 4 and sum(c.isalpha() for c in t) > len(t) * 0.3:
                    results.append(t)
            return results
        except Exception:
            pass
    return []


def clean_text_elements(elements):
    """Filter raw decoded strings into meaningful ad copy vs. metadata."""
    skip_patterns = [
        r"^P[0-9A-Za-z]{1,3}P",   # binary artifacts
        r"^https?://lh",            # Google profile image URLs
        r"_[a-z]+$",                # snake_case category tags
        r"^[A-Z0-9]{2,}$",         # all-caps codes
        r"[<>{}\[\]]",              # HTML fragments
    ]
    cleaned = []
    for t in elements:
        t = t.replace("&amp;", "&").replace('"', "").strip()
        if any(re.search(p, t) for p in skip_patterns):
            continue
        if len(t) < 5:
            continue
        cleaned.append(t)
    return cleaned


def parse_ad_elements(elements):
    """Separate decoded elements into ad copy, attributes, and practice areas."""
    lsa_attribute_keys = {
        "family_owned", "locally_owned", "new_clients", "professional_service",
        "speaks_spanish", "speaks_english", "woman_owned", "veteran_owned",
        "background_checked", "licensed", "insured",
    }
    practice_area_keys = {
        "asylum", "citizenship", "deportation", "family_based_immigration",
        "green_card", "immigration_attorney", "auto_accidents", "bicycle_accidents",
        "catastrophic_injuries", "dog_bites", "motorcycle_accidents", "pedestrian_accidents",
        "product_liability", "slip_fall", "wrongful_death", "personal_injury",
        "criminal_defense", "dui", "bankruptcy", "chapter_7", "chapter_13",
        "estate_planning", "wills", "trusts", "probate", "divorce",
        "family_law", "child_custody", "drug_charges", "assault",
    }
    badges = {"GOOGLE SCREENED", "GOOGLE GUARANTEED", "Verified", "Google Screened"}

    ad_copy, attributes, practice_areas, ad_badges = [], [], [], []
    for t in elements:
        tl = t.lower().replace(" ", "_").strip()
        if t in badges:
            ad_badges.append(t)
        elif tl in lsa_attribute_keys or ('"' in t and any(k in tl for k in lsa_attribute_keys)):
            clean = re.sub(r'"$', "", t).strip()
            if clean not in attributes:
                attributes.append(clean)
        elif tl in practice_area_keys:
            if t not in practice_areas:
                practice_areas.append(t)
        elif not t.startswith("http") and len(t) > 8:
            ad_copy.append(t)

    return ad_copy, attributes, practice_areas, ad_badges


# ---------- API calls ----------

def extract_preview_url(creative):
    """Extract preview/content URL from a creative object using multiple key paths."""
    for path in [("1", "4"), ("2", "4"), ("3", "2"), ("4",)]:
        try:
            obj = creative
            for k in path:
                obj = obj[k]
            if obj and isinstance(obj, str):
                if 'src="' in obj:
                    obj = obj.split('src="')[1].split('"')[0]
                return obj
        except (KeyError, TypeError):
            continue
    return ""


def get_creative_detail(session, advertiser_id, creative_id):
    """Fetch and parse a single ad creative."""
    data = {"f.req": json.dumps({"1": advertiser_id, "2": creative_id, "5": {"1": 1}})}
    try:
        r = session.post(
            f"{BASE}/anji/_/rpc/LookupService/GetCreativeById",
            params={"authuser": "0"},
            data=data,
            timeout=10,
        )
        ad = r.json()["1"]
    except Exception:
        return None

    fmt_int = ad.get("8", 0)
    fmt = {1: "text", 2: "image", 3: "video"}.get(fmt_int, "unknown")

    creatives = ad.get("5", [])
    url = extract_preview_url(creatives[0]) if creatives else ""

    is_image = fmt == "image" or any(x in url for x in ["simgad", "googlesyndication", "sadbundle"])
    if is_image:
        return {"format": "image", "image_url": url}

    if fmt == "text" and url:
        elements = decode_ad_param(url)
        copy, attrs, areas, badges = parse_ad_elements(clean_text_elements(elements))
        return {
            "format": "text",
            "preview_url": url,
            "ad_copy": copy,
            "attributes": attrs,
            "practice_areas": areas,
            "badges": badges,
            "raw_elements": elements,
        }

    return {"format": fmt, "url": url}


def get_creative_ids(session, advertiser_id, count=30):
    req = {
        "2": min(count, 100),
        "3": {"12": {"1": "", "2": True}, "13": {"1": [advertiser_id]}},
        "7": {"1": 1},
    }
    try:
        r = session.post(
            f"{BASE}/anji/_/rpc/SearchService/SearchCreatives",
            params={"authuser": ""},
            data={"f.req": json.dumps(req)},
            timeout=10,
        )
        return [(ad.get("2", ""), ad.get("7", {}).get("1", "")) for ad in r.json().get("1", []) if "2" in ad]
    except Exception:
        return []


# ---------- High-level commands ----------

def cmd_domain(domain, session=None):
    """Full analysis of a single firm by domain."""
    s = session or get_session()

    req = {"1": domain, "2": 1, "3": {"12": {"1": domain}}, "7": {"1": 1}}
    try:
        r = s.post(
            f"{BASE}/anji/_/rpc/SearchService/SearchCreatives",
            params={"authuser": ""},
            data={"f.req": json.dumps(req)},
            timeout=10,
        )
        results = r.json().get("1")
    except Exception:
        return {"error": f"Could not reach Transparency Center for {domain}"}

    if not results:
        return {"error": f"No advertiser found for domain: {domain}"}

    adv = results[0]
    advertiser_id = adv.get("1", "")
    name = adv.get("12", "")

    id_date_pairs = get_creative_ids(s, advertiser_id, count=50)

    all_text_ads = []
    image_count = 0
    last_active = ""
    all_attributes, all_practice_areas, all_badges, all_copy, all_image_urls = [], [], [], [], []

    for cid, ts in id_date_pairs:
        detail = get_creative_detail(s, advertiser_id, cid)
        if not detail:
            continue

        # Track most recent activity (timestamps are unix epoch strings)
        if ts and (not last_active or ts > last_active):
            last_active = ts

        if detail["format"] == "image":
            image_count += 1
            img_url = detail.get("image_url", "")
            if img_url and img_url not in all_image_urls:
                all_image_urls.append(img_url)
        elif detail["format"] == "text":
            all_text_ads.append(detail)
            all_attributes.extend(a for a in detail.get("attributes", []) if a not in all_attributes)
            all_practice_areas.extend(p for p in detail.get("practice_areas", []) if p not in all_practice_areas)
            all_badges.extend(b for b in detail.get("badges", []) if b not in all_badges)
            all_copy.extend(c for c in detail.get("ad_copy", []) if c not in all_copy)

    # Deduplicate ad copy into headlines/descriptions by length heuristic
    headlines = [c for c in all_copy if len(c) <= 40]
    descriptions = [c for c in all_copy if len(c) > 40]

    import datetime
    last_active_date = ""
    if last_active:
        try:
            last_active_date = datetime.datetime.fromtimestamp(int(last_active)).strftime("%Y-%m-%d")
        except Exception:
            pass

    return {
        "domain": domain,
        "name": name,
        "advertiser_id": advertiser_id,
        "total_ads": len(id_date_pairs),
        "image_ads": image_count,
        "text_ads_decoded": len([t for t in all_text_ads if t.get("ad_copy")]),
        "last_active": last_active_date,
        "lsa_attributes": all_attributes,
        "practice_areas": all_practice_areas,
        "badges": all_badges,
        "headlines": headlines,
        "descriptions": descriptions,
        "image_urls": all_image_urls[:10],
    }


def cmd_search(query, count=15):
    """Find law firms running Google Ads matching a keyword query."""
    s = get_session()
    req = {"1": query, "2": count, "3": count}
    try:
        r = s.post(
            f"{BASE}/anji/_/rpc/SearchService/SearchSuggestions",
            params={"authuser": "0"},
            data={"f.req": json.dumps(req)},
            timeout=10,
        )
        suggestions = r.json().get("1", [])
    except Exception:
        return {"error": "Search failed"}

    results = []
    for sg in suggestions:
        if "1" in sg:
            info = sg["1"]
            name = info.get("1", "")
            adv_id = info.get("2", "")
            try:
                ad_count = int(info["4"]["2"]["2"])
            except Exception:
                ad_count = 0
            if name and adv_id:
                results.append({"name": name, "advertiser_id": adv_id, "ad_count": ad_count})
        elif "2" in sg:
            domain = sg["2"].get("1", "")
            if domain:
                detail = cmd_domain(domain, s)
                if "error" not in detail:
                    results.append({
                        "name": detail.get("name", domain),
                        "domain": domain,
                        "advertiser_id": detail.get("advertiser_id", ""),
                        "ad_count": detail.get("total_ads", 0),
                        "last_active": detail.get("last_active", ""),
                    })

    return {"query": query, "results": results[:count]}


def cmd_competitors(query, exclude_domain=""):
    """Find competitors for a practice area + city query."""
    result = cmd_search(query, count=20)
    competitors = []
    for r in result.get("results", []):
        name = r.get("name", "")
        domain = r.get("domain", "")
        if exclude_domain and exclude_domain.lower() in domain.lower():
            continue
        if exclude_domain and exclude_domain.lower().split(".")[0] in name.lower():
            continue
        competitors.append({
            "name": name,
            "domain": domain,
            "ad_count": r.get("ad_count", 0),
            "last_active": r.get("last_active", ""),
        })
    return {"query": query, "competitors": competitors[:8]}


# ---------- CLI ----------

def main():
    parser = argparse.ArgumentParser(description="Google Ads Transparency Center extractor")
    sub = parser.add_subparsers(dest="command")

    p_domain = sub.add_parser("domain", help="Analyze a specific firm by domain")
    p_domain.add_argument("domain")

    p_search = sub.add_parser("search", help="Find firms by keyword")
    p_search.add_argument("query")
    p_search.add_argument("--count", type=int, default=15)

    p_comp = sub.add_parser("competitors", help="Find competitors")
    p_comp.add_argument("query")
    p_comp.add_argument("--exclude", default="")

    args = parser.parse_args()

    if args.command == "domain":
        print(json.dumps(cmd_domain(args.domain), indent=2))
    elif args.command == "search":
        print(json.dumps(cmd_search(args.query, args.count), indent=2))
    elif args.command == "competitors":
        print(json.dumps(cmd_competitors(args.query, args.exclude), indent=2))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
