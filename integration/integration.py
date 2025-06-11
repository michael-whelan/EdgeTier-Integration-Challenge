import logging
import time
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

import requests

FORMAT = "%(asctime)s | %(levelname)-5s | %(message)s"

logging.basicConfig(format=FORMAT, datefmt="%I:%M:%S %p")
logger = logging.getLogger()
logger.setLevel(logging.INFO)
POLL_INTERVAL_SECONDS = 10


BIG_CHAT_API = "http://localhost:8267"
OUR_API = "http://localhost:8266"


def fetch_events(start_time: datetime) -> Optional[Dict[str, Any]]:
    """Fetch BigChat events that occurred after the given time."""
    try:
        params = {"start_at": start_time.isoformat()}
        response = requests.get(f"{BIG_CHAT_API}/events", params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Error fetching events: {e}")
        return None


def create_chat(event: Dict[str, Any]) -> Optional[str]:
    """Create a chat in OurAPI from a BigChat START event."""

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


def end_chat(conversation_id: int) -> None:
    """Mark an existing chat as ended based on END event."""

    try:
        chat = find_chat_by_conversation_id(conversation_id)
        if chat:
            patch_data = {"ended_at": datetime.now(timezone.utc).isoformat()}
            requests.patch(f"{OUR_API}/chats/{chat['chat_id']}", json=patch_data)
            logger.info(f"Marked chat {chat['chat_id']} as ended.")
    except Exception as e:
        logger.error(f"Failed to end chat: {e}")


def transfer_chat(event: Dict[str, Any]) -> None:
    """Update the assigned agent on a chat from a TRANSFER event."""

    try:
        chat = find_chat_by_conversation_id(event["conversation_id"])
        if not chat:
            return
        new_advisor_id = event["data"].get("new_advisor_id")
        new_agent_id = get_agent_id_for_advisor(new_advisor_id)
        if new_agent_id:
            patch_data = {"agent_id": new_agent_id}
            requests.patch(f"{OUR_API}/chats/{chat['chat_id']}", json=patch_data)
            logger.info(f"Transferred chat {chat['chat_id']} to agent {new_agent_id}")
    except Exception as e:
        logger.error(f"Failed to transfer chat: {e}")


def create_message(event: Dict[str, Any]) -> None:
    """Add a customer or agent message to an existing chat."""

    try:
        chat = find_chat_by_conversation_id(event["conversation_id"])
        if not chat:
            return
        data = event.get("data", {})

        text = data.get("message")
        sender = data.get("sender")  # "agent" or "customer"
        agent_id = chat["agent_id"] if sender == "agent" else None

        payload = {
            "chat_id": chat["chat_id"],
            "text": text,
            "agent_id": agent_id,
            "sent_at": datetime.now(timezone.utc).isoformat(),
        }

        response = requests.post(
            f"{OUR_API}/chats/{chat['chat_id']}/messages", json=payload
        )
        response.raise_for_status()
        logger.info(f"Created message in chat {chat['chat_id']}: {text}")
    except Exception as e:
        logger.error(f"Failed to create message: {e}")


def find_chat_by_conversation_id(conversation_id: int) -> Optional[Dict[str, Any]]:
    """Look up a chat in OurAPI using the BigChat conversation_id."""

    try:
        resp = requests.get(
            f"{OUR_API}/chats", params={"external_id": str(conversation_id)}
        )
        resp.raise_for_status()
        chats = resp.json()
        return chats[0] if chats else None
    except Exception as e:
        logger.error(f"Failed to find chat: {e}")
        return None


def get_agent_id_for_advisor(advisor_id: int) -> Optional[str]:
    try:
        resp = requests.get(f"{OUR_API}/agents", params={"name": str(advisor_id)})
        resp.raise_for_status()
        agents = resp.json()
        if agents:
            return agents[0]["agent_id"]
    except Exception as e:
        logger.warning(f"Could not map advisor {advisor_id} to agent: {e}")
    return None


def handle_events(events: List[Dict[str, Any]]) -> None:
    """Dispatch BigChat events to the appropriate sync handler."""
    for event in events:
        event_type = event.get("event_name")
        if event_type == "START":
            create_chat(event)
        elif event_type == "END":
            end_chat(event["conversation_id"])
        elif event_type == "MESSAGE":
            # print("EVENT", event)
            create_message(event)
        elif event_type == "TRANSFER":
            transfer_chat(event)
        else:
            logger.warning(f"Unknown event type: {event_type}")


def run_sync_loop() -> None:
    """Continuously poll BigChat and sync events into OurAPI."""

    logger.info("Starting Big Chat → Our API sync loop...")
    last_checked = datetime.now(timezone.utc) - timedelta(seconds=30)

    while True:
        now = datetime.now(timezone.utc)
        events_data = fetch_events(last_checked)

        if events_data and "events" in events_data:
            handle_events(events_data["events"])
        # print(events_data["events"])
        last_checked = now
        time.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    run_sync_loop()
