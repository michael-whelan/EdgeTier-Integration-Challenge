import logging
import time
from datetime import datetime, timedelta, timezone

import requests

FORMAT = "%(asctime)s | %(levelname)-5s | %(message)s"

logging.basicConfig(format=FORMAT, datefmt="%I:%M:%S %p")
logger = logging.getLogger()
logger.setLevel(logging.INFO)
POLL_INTERVAL_SECONDS = 5


BIG_CHAT_API = "http://localhost:8267"
OUR_API = "http://localhost:8266"


def fetch_events(start_time):
    try:
        params = {"start_at": start_time.isoformat()}
        response = requests.get(f"{BIG_CHAT_API}/events", params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Error fetching events: {e}")
        return None


def run_sync_loop():
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
    # # Get events from BigChat.
    # parameters = {"start_at": (datetime.now() - timedelta(seconds=10))}
    # events = requests.get(f"{BIG_CHAT_API}/events", params=parameters)

    # # TODO: This is just an example, feel free to change however you want:
    # for event in events.json()["events"]:
    #     if event["event_name"] == "START":
    #         # Create a chat.
    #         data = {
    #             "external_id": str(event["conversation_id"]),
    #             "started_at": datetime.now().isoformat(),
    #         }
    #         chat = requests.post(f"{OUR_API}/chats", json=data)
    #         logger.info(f"Created chat {chat.json()['chat_id']}.")
