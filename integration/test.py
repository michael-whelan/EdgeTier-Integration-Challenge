from datetime import datetime, timezone
from unittest.mock import patch

import pytest

from integration.integration import create_chat, fetch_events

MOCK_EVENT = {"conversation_id": 123, "event_name": "START", "event_at": 1710000000}
MOCK_EVENT_START = {
    "event_name": "START",
    "conversation_id": 123,
    "event_at": 1710000000,
}


@patch("integration.integration.requests.get")
def test_fetch_events_success(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"events": [MOCK_EVENT]}

    result = fetch_events(datetime.now(timezone.utc))
    assert "events" in result
    assert result["events"][0]["event_name"] == "START"


@patch("integration.integration.requests.get")
def test_fetch_events_failure(mock_get):
    mock_get.side_effect = Exception("Network error")
    result = fetch_events(datetime.now(timezone.utc))
    assert result is None


@patch("integration.integration.requests.post")
def test_create_chat_success(mock_post):
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {"chat_id": "abc-123"}
    chat_id = create_chat(MOCK_EVENT_START)
    assert chat_id == "abc-123"


sample_data = [
    {
        "conversation_id": 2,
        "event_name": "MESSAGE",
        "event_at": 1749484938,
        "data": {
            "message": "Excepturi voluptate repellat ratione blanditiis laudantium blanditiis."
        },
    },
    {
        "conversation_id": 3,
        "event_name": "MESSAGE",
        "event_at": 1749484941,
        "data": {"message": "Expedita iure eos corporis."},
    },
    {"conversation_id": 4, "event_name": "END", "event_at": 1749484941, "data": None},
    {
        "conversation_id": 5,
        "event_name": "MESSAGE",
        "event_at": 1749484940,
        "data": {"message": "Aperiam saepe cum repellendus veritatis."},
    },
    {
        "conversation_id": 6,
        "event_name": "MESSAGE",
        "event_at": 1749484938,
        "data": {"message": "Adipisci ea qui impedit."},
    },
    {
        "conversation_id": 7,
        "event_name": "MESSAGE",
        "event_at": 1749484939,
        "data": {"message": "Alias voluptate hic labore impedit magnam distinctio."},
    },
    {
        "conversation_id": 8,
        "event_name": "TRANSFER",
        "event_at": 1749484941,
        "data": {"old_advisor_id": 8, "new_advisor_id": 5},
    },
    {
        "conversation_id": 9,
        "event_name": "MESSAGE",
        "event_at": 1749484938,
        "data": {"message": "Ducimus ipsum debitis molestiae."},
    },
    {
        "conversation_id": 10,
        "event_name": "START",
        "event_at": 1749488542,
        "data": None,
    },
]
