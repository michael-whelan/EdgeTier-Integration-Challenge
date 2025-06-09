import logging
import time
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

import requests

FORMAT = "%(asctime)s | %(levelname)-5s | %(message)s"

logging.basicConfig(format=FORMAT, datefmt="%I:%M:%S %p")
logger = logging.getLogger()
logger.setLevel(logging.INFO)
POLL_INTERVAL_SECONDS = 5


BIG_CHAT_API = "http://localhost:8267"
OUR_API = "http://localhost:8266"


def fetch_events(start_time: datetime) -> Optional[Dict[str, Any]]:
    """Fetch events from Big Chat API."""
    try:
        params = {"start_at": start_time.isoformat()}
        response = requests.get(f"{BIG_CHAT_API}/events", params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Error fetching events: {e}")
        return None


def run_sync_loop() -> None:
    logger.info("Starting Big Chat → Our API sync loop...")
    last_checked = datetime.now(timezone.utc) - timedelta(seconds=30)

    while True:
        events_data = fetch_events(last_checked)
        now = datetime.now(timezone.utc)

        print(events_data)
        last_checked = now
        time.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    run_sync_loop()
