from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from integration.integration import (
    create_chat,
    create_message,
    end_chat,
    fetch_events,
    transfer_chat,
)

CONVERSATION_ID = 123

MOCK_EVENT = {
    "conversation_id": CONVERSATION_ID,
    "event_name": "START",
    "event_at": 1710000000,
}

MOCK_EVENT_START = {
    "event_name": "START",
    "conversation_id": CONVERSATION_ID,
    "event_at": 1710000000,
}

MOCK_CHAT = {
    "chat_id": "abc-123",
    "external_id": str(CONVERSATION_ID),
    "agent_id": "agent-999",
}

MOCK_EVENT_MESSAGE = {
    "event_name": "MESSAGE",
    "conversation_id": CONVERSATION_ID,
    "event_at": 1710000020,
    "data": {"message": "Hello", "sender": "customer"},
}

MOCK_EVENT_TRANSFER = {
    "event_name": "TRANSFER",
    "conversation_id": CONVERSATION_ID,
    "event_at": 1710000030,
    "data": {"new_advisor_id": 42},
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


@patch("integration.integration.requests.patch")
@patch("integration.integration.requests.get")
def test_end_chat_success(mock_get, mock_patch):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = [MOCK_CHAT]

    mock_patch.return_value.status_code = 200

    end_chat(CONVERSATION_ID)
    mock_patch.assert_called_once()


@patch("integration.integration.requests.patch")
@patch("integration.integration.requests.get")
def test_transfer_chat_success(mock_get, mock_patch):
    # First call to get chat by external_id
    mock_get.side_effect = [
        MagicMock(status_code=200, json=lambda: [MOCK_CHAT]),
        MagicMock(status_code=200, json=lambda: [{"agent_id": "agent-42"}]),
    ]

    mock_patch.return_value.status_code = 200
    transfer_chat(MOCK_EVENT_TRANSFER)

    mock_patch.assert_called_once()
    assert mock_patch.call_args[1]["json"]["agent_id"] == "agent-42"


@patch("integration.integration.requests.post")
@patch("integration.integration.requests.get")
def test_create_message_success(mock_get, mock_post):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = [MOCK_CHAT]

    mock_post.return_value.status_code = 200
    create_message(MOCK_EVENT_MESSAGE)
    mock_post.assert_called_once()
    data = mock_post.call_args[1]["json"]
    assert data["text"] == "Hello"
    assert data["agent_id"] is None


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
