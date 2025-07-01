import os
from datetime import datetime, timedelta

import requests


def daily_ranges(back_years=5):
    """Yield start and end dates (same day) for each day over the past `back_years`."""
    today = datetime.now().date()
    start_date = today - timedelta(days=back_years * 365)
    current = start_date
    while current <= today:
        yield current, current  # start and end are the same for daily range
        current += timedelta(days=1)


def download_excel(start_date, end_date, session=None):
    base_url = "https://kamis.kilimo.go.ke/site/market_search"
    params = {"start": start_date.isoformat(), "end": end_date.isoformat(), "per_page": 3000, "export": "excel"}

    filename = f"data/kamis/market_prices/kamis_{start_date}.xlsx"
    if os.path.exists(filename):
        print(f"⏩ Skipping existing file: {filename}")
        return

    s = session or requests
    try:
        with s.get(base_url, params=params, stream=True, timeout=30) as resp:
            resp.raise_for_status()
            with open(filename, "wb") as f:
                for chunk in resp.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        f.write(chunk)
        print(f"✅ Saved: {filename}")
    except Exception as e:
        print(f"❌ Failed to download {start_date}: {e}")


def main():
    sess = requests.Session()
    for start, end in daily_ranges():
        print(f"⏳ Downloading data for {start}")
        download_excel(start, end, session=sess)


if __name__ == "__main__":
    main()
