# python main.py (--dry-run)

import argparse
import json
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

import requests
from bs4 import BeautifulSoup

# ---------------------------------------------------------------------------
# Configuration — edit these to match your case
# ---------------------------------------------------------------------------
RECEIPT_NUMBER = "IOE1234567890"
DATE_OF_BIRTH = "2000-01-01"
ALIEN_NUMBER = ""

# Date range to scan (inclusive)
# Weekends are automatically skipped
SCAN_START = "2026-03-13"
SCAN_END = "2026-06-30"

# Time slots to try for each date, don't change
TIME_SLOTS = [
    "08:00", "09:00", "10:00", "11:00", "12:00",
    "13:00", "14:00", "15:00", "16:00", "17:00",
]

# Use only places near your mailing address
# to reduce search complexity, 3 is sufficient
ASC_CODES = [
    "XAA",  # USCIS ANCHORAGE
    "XAB",  # USCIS BIRMINGHAM
    "XAC",  # USCIS ATLANTA
    "XAD",  # USCIS CHARLOTTE
    "XAE",  # USCIS CHARLESTON, SC
    "XAF",  # USCIS RALEIGH
    "XAG",  # USCIS GREER
    "XAI",  # USCIS FORT BENNING
    "XBA",  # USCIS BALTIMORE
    "XBB",  # USCIS GLENMONT
    "XBC",  # USCIS SALISBURY
    "XBD",  # USCIS BOSTON
    "XBE",  # USCIS HARTFORD
    "XBF",  # USCIS PROVIDENCE
    "XBG",  # USCIS MANCHESTER
    "XBH",  # USCIS BUFFALO
    "XBI",  # USCIS ALBANY
    "XBJ",  # USCIS SYRACUSE
    "XBK",  # USCIS LAWRENCE
    "XBO",  # USCIS BOSTON-MOBILE
    "XCA",  # USCIS NORRIDGE
    "XCB",  # USCIS CHICAGO-SOUTH
    "XCC",  # USCIS SALT LAKE CITY CLINC
    "XCD",  # USCIS NAPERVILLE
    "XCE",  # USCIS WAUKEGAN
    "XCF",  # USCIS MICHIGAN CITY
    "XCG",  # USCIS INDIANAPOLIS
    "XCH",  # USCIS MILWAUKEE
    "XCI",  # USCIS CLEVELAND
    "XCJ",  # USCIS CINCINNATI
    "XCK",  # USCIS COLUMBUS
    "XDA",  # USCIS DALLAS NORTH
    "XDB",  # USCIS FORT WORTH
    "XDC",  # USCIS LUBBOCK
    "XDD",  # USCIS OKLAHOMA CITY
    "XDE",  # USCIS ALEXANDRIA
    "XDF",  # USCIS NORFOLK
    "XDG",  # USCIS DENVER
    "XDH",  # USCIS GRAND JUNCTION
    "XDI",  # USCIS CASPER
    "XDJ",  # USCIS SALT LAKE CITY
    "XDK",  # USCIS DETROIT
    "XDL",  # USCIS DALLAS SOUTH
    "XDM",  # USCIS GRAND RAPIDS
    "XDN",  # USCIS FORT SILL
    "XEA",  # USCIS EL PASO
    "XEC",  # USCIS ALBUQUERQUE
    "XFB",  # USCIS OAKLAND
    "XFC",  # USCIS SANTA ROSA
    "XFD",  # USCIS SALINAS
    "XFE",  # USCIS SACRAMENTO
    "XFF",  # USCIS MODESTO
    "XFG",  # USCIS FRESNO
    "XFI",  # USCIS BAKERSFIELD
    "XGA",  # USCIS NOME
    "XGB",  # USCIS KODIAK
    "XGD",  # USCIS FAIRBANKS
    "XGE",  # USCIS JUNEAU
    "XGF",  # USCIS KETICHIKAN
    "XGG",  # USCIS DUTCH HARBOR
    "XGI",  # USCIS WILMINGTON
    "XHA",  # USCIS MCALLEN
    "XHB",  # USCIS HARLINGEN
    "XHC",  # USCIS HELENA
    "XHD",  # USCIS BOISE
    "XHE",  # USCIS IDAHO FALLS
    "XHF",  # USCIS HONOLULU
    "XHG",  # USCIS GUAM
    "XHH",  # USCIS HOUSTON SOUTHEAST
    "XHI",  # USCIS HOUSTON SOUTHWEST
    "XHJ",  # USCIS HOUSTON NORTHWEST
    "XHS",  # USCIS SAIPAN
    "XIP",  # USCIS MAUI
    "XIT",  # USCIS KONA
    "XJX",  # USCIS LAREDO
    "XKA",  # USCIS KANSAS CITY
    "XKB",  # USCIS WICHITA
    "XKC",  # USCIS ST LOUIS
    "XKE",  # USCIS DODGE CITY
    "XLB",  # USCIS POMONA
    "XLC",  # USCIS EL MONTE
    "XLD",  # USCIS GARDENA
    "XLE",  # USCIS SAN FERNANDO
    "XLF",  # USCIS BELLFLOWER
    "XLG",  # USCIS LA BREA
    "XLH",  # USCIS TUSTIN
    "XLI",  # USCIS BUENA PARK
    "XLJ",  # USCIS RIVERSIDE
    "XLK",  # USCIS OXNARD
    "XLM",  # USCIS WILSHIRE
    "XMA",  # USCIS CENTRAL MIAMI
    "XMB",  # USCIS NORTH MIAMI
    "XMC",  # USCIS KENDALL
    "XMD",  # USCIS FT LAUDERDALE
    "XME",  # USCIS ORLANDO
    "XMF",  # USCIS TAMPA
    "XMG",  # USCIS JACKSONVILLE
    "XMH",  # USCIS WEST PALM BEACH
    "XMJ",  # USCIS FORT MYERS
    "XNA",  # USCIS NEW ORLEANS
    "XNB",  # USCIS FORT SMITH
    "XNC",  # USCIS JACKSON
    "XND",  # USCIS MEMPHIS
    "XNE",  # USCIS NASHVILLE
    "XNF",  # USCIS LOUISVILLE
    "XNG",  # USCIS PORT CHESTER
    "XNI",  # USCIS BROOKLYN
    "XNJ",  # USCIS BRONX
    "XNK",  # USCIS MANHATTAN
    "XNL",  # USCIS HAUPPAUGE
    "XNM",  # USCIS QUEENS/JAMAICA
    "XNN",  # USCIS LONG ISLAND CITY
    "XNO",  # USCIS ELIZABETH
    "XNP",  # USCIS HACKENSACK
    "XNQ",  # USCIS HOLTSVILLE
    "XOA",  # USCIS OMAHA
    "XOB",  # USCIS DES MOINES
    "XPA",  # USCIS PHILADELPHIA
    "XPB",  # USCIS PITTSBURGH
    "XPC",  # USCIS CHARLESTON, WV
    "XPD",  # USCIS DOVER
    "XPE",  # USCIS YORK
    "XPF",  # USCIS LAS VEGAS
    "XPG",  # USCIS TUCSON
    "XPH",  # USCIS RENO
    "XPI",  # USCIS YUMA
    "XPJ",  # USCIS PORTLAND, ME
    "XPK",  # USCIS BURLINGTON
    "XPL",  # USCIS PORTLAND, OR
    "XPM",  # USCIS SAN JUAN
    "XPO",  # USCIS ST THOMAS
    "XPP",  # USCIS ST CROIX
    "XPQ",  # USCIS PHOENIX
    "XPS",  # USCIS CENTER CITY
    "XPT",  # USCIS OREGON MOBILE 
    "XSA",  # USCIS SAN ANTONIO
    "XSB",  # USCIS SAN DIEGO
    "XSC",  # USCIS SAN MARCOS
    "XSD",  # USCIS IMPERIAL
    "XSE",  # USCIS SEATTLE
    "XSF",  # USCIS SPOKANE
    "XSH",  # USCIS YAKIMA
    "XSI",  # USCIS ST PAUL
    "XSJ",  # USCIS RAPID CITY
    "XSK",  # USCIS FARGO
    "XSL",  # USCIS SIOUX FALLS
    "XSM",  # USCIS DULUTH
    "XSN",  # USCIS AUSTIN
    "XTD",  # USCIS SAN FRANCISCO
    "XTE",  # USCIS SAN JOSE
    "XWA",  # USCIS KAUAI
    "XWC",  # USCIS WATFORD CITY
]

# Delay between requests, don't change
DELAY_BETWEEN_REQUESTS = 0.5  

# ---------------------------------------------------------------------------
# Paths & URLs
# ---------------------------------------------------------------------------
COOKIES_PATH = Path("my.uscis.gov_cookies.json")
OUTPUT_PATH = Path("uscis_appointment_results.json")
BASE = "https://my.uscis.gov"
API_URL = f"{BASE}/accounts/accounts-data/api/biometrics-rescheduling/find-appointment"

UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36"
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_cookies() -> list[dict]:
    with open(COOKIES_PATH) as f:
        return json.load(f)


def build_session(raw_cookies: list[dict]) -> requests.Session:
    s = requests.Session()
    s.trust_env = False
    s.headers.update({
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    })
    for c in raw_cookies:
        s.cookies.set(c["name"], c["value"],
                      domain=c.get("domain", "my.uscis.gov"),
                      path=c.get("path", "/"))
    return s


def get_csrf(session: requests.Session) -> str:
    print("[*] Fetching page for CSRF token ...")
    url = f"{BASE}/accounts/biometrics/reschedule/find-appointment"
    r = session.get(url, timeout=30, allow_redirects=True)
    print(f"    Status: {r.status_code}  URL: {r.url}")
    if "login" in r.url.lower() or "sign" in r.url.lower():
        print("    ** Redirected to login — cookies expired. Re-export and retry. **")
        sys.exit(1)
    soup = BeautifulSoup(r.text, "html.parser")
    meta = soup.find("meta", attrs={"name": "csrf-token"})
    token = meta["content"] if meta else None
    if token:
        print(f"    CSRF: {token[:40]}...")
    else:
        print("    WARNING: no CSRF token found")
    return token


def api_headers(csrf: str) -> dict:
    return {
        "User-Agent": UA,
        "Accept": "*/*",
        "Content-Type": "application/json",
        "Cache-Control": "no-cache",
        "Origin": BASE,
        "Referer": f"{BASE}/accounts/biometrics/reschedule/find-appointment",
        "x-csrf-token": csrf,
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
    }


def make_body(date: str, time_slot: str, asc: str) -> dict:
    return {
        "appointment": {
            "receiptNumber": RECEIPT_NUMBER,
            "alienNumber": ALIEN_NUMBER,
            "appointmentDate": date,
            "appointmentTime": time_slot,
            "dateOfBirth": DATE_OF_BIRTH,
            "asc": asc,
        }
    }


def post_find_appointment(session: requests.Session, csrf: str,
                          date: str, time_slot: str, asc: str) -> requests.Response:
    body = make_body(date, time_slot, asc)
    return session.post(API_URL, json=body, headers=api_headers(csrf), timeout=15)


def date_range(start: str, end: str):
    current = datetime.strptime(start, "%Y-%m-%d")
    last = datetime.strptime(end, "%Y-%m-%d")
    while current <= last:
        if current.weekday() < 5:  # Mon-Fri only
            yield current.strftime("%Y-%m-%d")
        current += timedelta(days=1)


# ---------------------------------------------------------------------------
# Dry-run mode
# ---------------------------------------------------------------------------

def run_dry(session: requests.Session, csrf: str):
    print("\n" + "=" * 65)
    print("  DRY RUN — single request with hardcoded date/time")
    print("=" * 65)

    date = "2026-03-14"
    time_slot = "10:00"
    asc = ASC_CODES[0]
    body = make_body(date, time_slot, asc)

    print(f"\n  >>> POST {API_URL}")
    hdrs = api_headers(csrf)
    for k, v in hdrs.items():
        print(f"      {k}: {v}")
    print(f"\n      Body:\n{json.dumps(body, indent=6)}")

    r = post_find_appointment(session, csrf, date, time_slot, asc)

    print(f"\n  <<< {r.status_code} {r.reason}  ({len(r.text)} bytes)")
    print(f"      Content-Type: {r.headers.get('Content-Type', '?')}")
    try:
        data = r.json()
        formatted = json.dumps(data, indent=2)
        print(f"      JSON body:\n{formatted[:5000]}")
        if len(formatted) > 5000:
            print(f"      ... ({len(formatted)} chars total)")
    except Exception:
        print(f"      Raw body:\n{r.text[:3000]}")

    with open(OUTPUT_PATH, "w") as f:
        json.dump({"dry_run": {"date": date, "time": time_slot, "asc": asc,
                                "status": r.status_code, "body": r.text}},
                  f, indent=2)
    print(f"\n  Saved to {OUTPUT_PATH}")


# ---------------------------------------------------------------------------
# Response classification
# ---------------------------------------------------------------------------

RESP_CAPTCHA = "CAPTCHA"
RESP_DENIED = "DENIED_403"

def classify_response(status: int, body: str) -> str | None:
    """Return a bad-response tag if this is CAPTCHA or 403, else None."""
    if status == 403 or "Access Denied" in body:
        return RESP_DENIED
    if "<!doctype html>" in body.lower() or "captcha" in body.lower():
        return RESP_CAPTCHA
    return None


# ---------------------------------------------------------------------------
# Resume support
# ---------------------------------------------------------------------------

def load_previous_results() -> tuple[dict[str, list[str]], set[str]]:
    """
    Load response_groups from a previous run.
    Returns (response_groups, already_queried_set).
    Strips out CAPTCHA and DENIED groups so they get re-queried.
    """
    if not OUTPUT_PATH.exists():
        return {}, set()

    try:
        with open(OUTPUT_PATH) as f:
            prev = json.load(f)
    except (json.JSONDecodeError, KeyError):
        return {}, set()

    if "response_groups" not in prev:
        return {}, set()

    response_groups: dict[str, list[str]] = {}
    already_queried: set[str] = set()

    for resp_key, info in prev["response_groups"].items():
        queries = info.get("queries", [])
        tag = classify_response(0, resp_key)
        if tag == RESP_CAPTCHA or tag == RESP_DENIED:
            # Don't restore bad responses — these need to be re-queried
            continue
        response_groups[resp_key] = queries
        already_queried.update(queries)

    return response_groups, already_queried


# ---------------------------------------------------------------------------
# Enumerate mode
# ---------------------------------------------------------------------------

def print_response_summary(response_groups: dict):
    """Print a live summary: for each distinct response, show first query and count."""
    lines = []
    lines.append("")
    lines.append("  ┌─ Response groups ─────────────────────────────────────────")
    for resp_key, queries in response_groups.items():
        first = queries[0]
        lines.append(f"  │ response: {resp_key} query: {first} [and {len(queries):>4d} queries] ")
    lines.append("  └─────────────────────────────────────────────────────────────")
    print("\033[J" + "\n".join(lines), end="", flush=True)


def save_results(response_groups: dict, count: int, errors: list):
    """Save the response→queries dict to disk."""
    output = {
        "config": {
            "receipt": RECEIPT_NUMBER, "dob": DATE_OF_BIRTH,
            "asc_codes": ASC_CODES, "range": [SCAN_START, SCAN_END],
        },
        "total_scanned": count,
        "total_errors": len(errors),
        "response_groups": {
            resp: {"count": len(queries), "first": queries[0], "queries": queries}
            for resp, queries in response_groups.items()
        },
        "errors": errors,
    }
    with open(OUTPUT_PATH, "w") as f:
        json.dump(output, f, indent=2, default=str)


def run_enumerate(session: requests.Session, csrf: str):
    print("\n" + "=" * 65)
    print("  ENUMERATING dates & times")
    print("=" * 65)
    print(f"  Receipt : {RECEIPT_NUMBER}")
    print(f"  DOB     : {DATE_OF_BIRTH}")
    print(f"  ASC     : {', '.join(ASC_CODES)}")
    print(f"  Range   : {SCAN_START} → {SCAN_END}")
    print(f"  Slots   : {len(TIME_SLOTS)} per day")
    print(f"  Delay   : {DELAY_BETWEEN_REQUESTS}s between requests\n")

    # Load previous results for resume
    response_groups, already_queried = load_previous_results()
    if already_queried:
        print(f"  Resuming: {len(already_queried)} queries loaded from previous run")
        print(f"  Existing response groups: {len(response_groups)}")

    dates = list(date_range(SCAN_START, SCAN_END))
    total = len(dates) * len(TIME_SLOTS) * len(ASC_CODES)
    remaining = total - len(already_queried)
    print(f"  Total combinations : {total}")
    print(f"  Already completed  : {len(already_queried)}")
    print(f"  Remaining          : {remaining}")
    print(f"  Estimated time     : ~{remaining * DELAY_BETWEEN_REQUESTS / 60:.0f} min\n")

    errors = []
    count = len(already_queried)
    skipped = len(already_queried)
    prev_summary_lines = 0

    for date in dates:
        for ts in TIME_SLOTS:
            for asc in ASC_CODES:
                query_label = f"{asc} {date} {ts}"

                if query_label in already_queried:
                    continue

                count += 1

                try:
                    r = post_find_appointment(session, csrf, date, ts, asc)
                except requests.RequestException as e:
                    print(f"\n  [{count}/{total}] {query_label} — ERROR: {e}")
                    errors.append({"query": query_label, "error": str(e)})
                    time.sleep(DELAY_BETWEEN_REQUESTS)
                    continue

                body_text = r.text
                status = r.status_code

                # Check for CAPTCHA or 403
                bad_tag = classify_response(status, body_text)
                if bad_tag:
                    save_results(response_groups, count, errors)
                    print(f"\n\n  [{count}/{total}] {query_label}")
                    if bad_tag == RESP_CAPTCHA:
                        print("  ** CAPTCHA / session expired detected! **")
                        print("  The server returned a login/CAPTCHA page.")
                    else:
                        print("  ** 403 Access Denied — blocked by WAF! **")
                    print(f"\n  Progress saved ({count - skipped} new queries this run).")
                    print("  To resume:")
                    print("    1. Re-export your cookies from Chrome")
                    print("    2. Run the script again — it will skip already-completed queries")
                    return

                resp_key = body_text if status == 200 else f"HTTP {status}: {body_text}"
                response_groups.setdefault(resp_key, []).append(query_label)

                if prev_summary_lines > 0:
                    sys.stdout.write(f"\033[{prev_summary_lines}A\033[J")

                sys.stdout.write(f"  [{count}/{total}] {query_label} — HTTP {status}")
                print_response_summary(response_groups)

                prev_summary_lines = len(response_groups) + 4

                save_results(response_groups, count, errors)

                time.sleep(DELAY_BETWEEN_REQUESTS)

    # Final summary
    print("\n\n" + "=" * 65)
    print(f"  COMPLETE — {count}/{total} combinations, {len(errors)} errors")
    print(f"  Distinct responses: {len(response_groups)}")
    print("=" * 65)
    for resp_key, queries in response_groups.items():
        preview = resp_key[:120] + ("..." if len(resp_key) > 120 else "")
        print(f"\n  Response ({len(queries)} queries):")
        print(f"    Preview : {preview}")
        print(f"    First   : {queries[0]}")
        if len(queries) > 1:
            print(f"    Last    : {queries[-1]}")

    print(f"\n  Full results saved to {OUTPUT_PATH}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="USCIS Biometrics Appointment Finder")
    parser.add_argument("--dry-run", action="store_true",
                        help="Single request with hardcoded date/time, print everything")
    args = parser.parse_args()

    print("=" * 65)
    print("  USCIS Biometrics Appointment Finder")
    print("=" * 65)
    print(f"  Time: {datetime.now().isoformat()}\n")

    if not COOKIES_PATH.exists():
        print(f"Cookie file not found: {COOKIES_PATH}")
        sys.exit(1)

    raw = load_cookies()
    print(f"Loaded {len(raw)} cookies")
    session = build_session(raw)
    csrf = get_csrf(session)
    if not csrf:
        print("Cannot proceed without CSRF token.")
        sys.exit(1)

    if args.dry_run:
        run_dry(session, csrf)
    else:
        run_enumerate(session, csrf)

    print("\n" + "=" * 65)
    print("  Done.")
    print("=" * 65)


if __name__ == "__main__":
    main()
