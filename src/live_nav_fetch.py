"""
Live NAV Fetch Module
=====================
Fetch live Net Asset Value (NAV) data from mfapi.in for selected mutual fund schemes.
Saves the historical NAV data as CSV files in the raw data directory.

This module:
- Builds a resilient HTTP session with retry logic for transient failures
- Fetches NAV data from mfapi.in REST API for 6 bluechip schemes
- Saves each scheme's NAV history as a separate CSV file
- Handles API errors and connection failures gracefully
"""

from pathlib import Path

import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"

AMFI_CODES = [125497, 119551, 120503, 118632, 119092, 120841]


def _build_session() -> requests.Session:
    """Build a requests session with retry strategy for transient API failures."""
    retry = Retry(
        total=5,
        read=5,
        connect=5,
        backoff_factor=1.0,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
    )
    adapter = HTTPAdapter(max_retries=retry)
    session = requests.Session()
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


def fetch_nav(amfi_code: int, session: requests.Session) -> Path:
    """Fetch live NAV history from mfapi.in and save as raw CSV."""
    url = f"https://api.mfapi.in/mf/{amfi_code}"
    response = session.get(url, timeout=30)
    response.raise_for_status()
    payload = response.json()

    nav_df = pd.DataFrame(payload.get("data", []))
    output_path = RAW_DIR / f"nav_{amfi_code}.csv"
    nav_df.to_csv(output_path, index=False)
    print(f"Saved {len(nav_df)} rows to {output_path}")
    return output_path


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    session = _build_session()
    success_count = 0
    failed_codes: list[int] = []
    for code in AMFI_CODES:
        try:
            fetch_nav(code, session)
            success_count += 1
        except Exception as exc:  # noqa: BLE001
            print(f"Failed for {code}: {exc}")
            failed_codes.append(code)

    print(f"\nFetch summary: {success_count}/{len(AMFI_CODES)} successful")
    if failed_codes:
        print(f"Failed AMFI codes: {failed_codes}")


if __name__ == "__main__":
    main()
