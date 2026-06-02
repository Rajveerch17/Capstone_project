from pathlib import Path

import pandas as pd
import requests

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"

AMFI_CODES = [125497, 119551, 120503, 118632, 119092, 120841]


def fetch_nav(amfi_code: int) -> Path:
    """Fetch live NAV history from mfapi.in and save as raw CSV."""
    url = f"https://api.mfapi.in/mf/{amfi_code}"
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    payload = response.json()

    nav_df = pd.DataFrame(payload.get("data", []))
    output_path = RAW_DIR / f"nav_{amfi_code}.csv"
    nav_df.to_csv(output_path, index=False)
    print(f"Saved {len(nav_df)} rows to {output_path}")
    return output_path


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    for code in AMFI_CODES:
        try:
            fetch_nav(code)
        except Exception as exc:  # noqa: BLE001
            print(f"Failed for {code}: {exc}")


if __name__ == "__main__":
    main()
