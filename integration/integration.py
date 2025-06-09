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


def create_chat(event: Dict[str, Any]) -> Optional[str]:
    payload = {
        "external_id": str(event["conversation_id"]),
        "started_at": datetime.now(timezone.utc).isoformat(),
    }
    try:
        response = requests.post(f"{OUR_API}/chats", json=payload)
        response.raise_for_status()
        chat_id = response.json()["chat_id"]
        logger.info(
            f"Created chat {chat_id} from conversation {event['conversation_id']}"
        )
        return chat_id
    except Exception as e:
        logger.error(f"Failed to create chat: {e}")
        return None


def handle_events(events: List[Dict[str, Any]]) -> None:
    for event in events:
        event_type = event.get("event_name")
        if event_type == "START":
            create_chat(event)
        # elif event_type == "END":
        #     # TODO end_chat(event)
        # elif event_type == "MESSAGE":
        #     # TODO create_message(event)
        # elif event_type == "TRANSFER":
        #     # TODO transfer_chat(event)
        else:
            logger.warning(f"Unknown event type: {event_type}")


def run_sync_loop() -> None:
    logger.info("Starting Big Chat → Our API sync loop...")
    last_checked = datetime.now(timezone.utc) - timedelta(seconds=30)

    while True:
        now = datetime.now(timezone.utc)
        events_data = fetch_events(last_checked)

        if events_data and "events" in events_data:
            handle_events(events_data["events"])
        print(events_data["events"])
        last_checked = now
        time.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    run_sync_loop()
