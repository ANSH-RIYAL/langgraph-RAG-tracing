#!/usr/bin/env python3
import argparse
import csv
import gzip
import io
import json
import os
import pathlib
import sys
import time
from typing import List

import requests


DEFAULT_TICKERS = [
    "AAPL","MSFT","GOOGL","AMZN","META","TSLA","NVDA","BRK-B","JPM","V",
    "UNH","XOM","JNJ","PG","MA","HD","AVGO","BAC","PFE","COST"
]


def ensure_dir(p: pathlib.Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def fetch_stooq_csv(session: requests.Session, ticker: str) -> bytes:
    # Stooq symbol mapping
    sym = ticker.lower()
    if sym == "brk-b":
        sym = "brk-b.us"
    elif "." not in sym:
        sym = f"{sym}.us"
    url = f"https://stooq.com/q/d/l/?s={sym}&i=d"
    r = session.get(url, timeout=60)
    r.raise_for_status()
    return r.content


def validate_csv_bytes(data: bytes) -> bool:
    try:
        s = io.StringIO(data.decode("utf-8", errors="replace"))
        reader = csv.reader(s)
        rows = list(reader)
        if len(rows) < 2:
            return False
        header = rows[0]
        return len(header) >= 5 and any(r for r in rows[1:] if len(r) >= 2)
    except Exception:
        return False


def fetch_fred_series(session: requests.Session, api_key: str, series_id: str) -> bytes:
    url = "https://api.stlouisfed.org/fred/series/observations"
    params = {"series_id": series_id, "api_key": api_key, "file_type": "json", "observation_start": "1900-01-01"}
    r = session.get(url, params=params, timeout=60)
    r.raise_for_status()
    data = r.json()
    # Convert to CSV
    output = io.StringIO()
    w = csv.writer(output)
    w.writerow(["date","value"])
    for obs in data.get("observations", []):
        w.writerow([obs.get("date"), obs.get("value")])
    return output.getvalue().encode("utf-8")


def fetch_companyfacts(session: requests.Session, cik: str) -> bytes:
    ua = os.getenv("SEC_USER_AGENT", "contact@example.com")
    session.headers.update({"User-Agent": ua, "Accept": "application/json"})
    url = f"https://data.sec.gov/api/xbrl/companyfacts/{cik}.json"
    r = session.get(url, timeout=60)
    if r.status_code == 404:
        raise RuntimeError("CIK not found")
    r.raise_for_status()
    return r.content


def get_ticker_to_cik(session: requests.Session) -> dict:
    r = session.get("https://www.sec.gov/files/company_tickers.json", timeout=60)
    r.raise_for_status()
    raw = r.json()
    mapping = {}
    for _, v in raw.items():
        mapping[str(v.get("ticker", "")).upper()] = f"CIK{int(v.get('cik_str')):010d}"
    return mapping


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch a minimal, real finance dataset for 20 tickers into a flat final_docs directory")
    parser.add_argument("--tickers", nargs="*", default=DEFAULT_TICKERS, help="Tickers to fetch (default: 20 majors)")
    parser.add_argument("--out", default="real_data/final_docs", help="Flat output directory")
    parser.add_argument("--fred-series", nargs="*", default=["UNRATE","DGS10","GDP"], help="FRED series to include")
    args = parser.parse_args()

    out_dir = pathlib.Path(args.out)
    ensure_dir(out_dir)

    sess = requests.Session()
    # Apply a global User-Agent (SEC requires this; reuse for all requests)
    ua = os.getenv("SEC_USER_AGENT", "contact@example.com")
    sess.headers.update({"User-Agent": ua})

    # 1) Market prices (Stooq CSV) per ticker
    for t in args.tickers:
        try:
            data = fetch_stooq_csv(sess, t)
            if not validate_csv_bytes(data):
                print(f"Skipping {t}: invalid/empty CSV from Stooq", file=sys.stderr)
                continue
            with open(out_dir / f"market_{t.upper()}.csv", "wb") as f:
                f.write(data)
        except Exception as e:
            print(f"Stooq failed for {t}: {e}", file=sys.stderr)
        time.sleep(0.2)

    # 2) FRED macro CSVs
    fred_key = os.getenv("FRED_API_KEY")
    if fred_key:
        for sid in args.fred_series:
            try:
                data = fetch_fred_series(sess, fred_key, sid)
                if not validate_csv_bytes(data):
                    print(f"Skipping FRED {sid}: invalid/empty", file=sys.stderr)
                    continue
                with open(out_dir / f"fred_{sid}.csv", "wb") as f:
                    f.write(data)
            except Exception as e:
                print(f"FRED failed for {sid}: {e}", file=sys.stderr)
            time.sleep(0.2)
    else:
        print("FRED_API_KEY not set; skipping FRED", file=sys.stderr)

    # 3) SEC CompanyFacts JSON (subset for tickers that resolve)
    try:
        ticker_to_cik = get_ticker_to_cik(sess)
    except Exception as e:
        print(f"Failed to load SEC ticker->CIK: {e}", file=sys.stderr)
        ticker_to_cik = {}

    delay_ms = int(os.getenv("SEC_DELAY_MS", "200"))
    for t in args.tickers:
        cik = ticker_to_cik.get(t.upper())
        if not cik:
            continue
        try:
            data = fetch_companyfacts(sess, cik)
            # minimal JSON sanity
            _ = json.loads(data.decode("utf-8", errors="replace"))
            with open(out_dir / f"sec_companyfacts_{cik}.json", "wb") as f:
                f.write(data)
        except Exception as e:
            print(f"CompanyFacts failed for {t} ({cik}): {e}", file=sys.stderr)
        time.sleep(max(0, delay_ms) / 1000.0)

    print(f"Done. Files in {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


