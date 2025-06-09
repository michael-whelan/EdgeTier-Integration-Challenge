from datetime import datetime, timezone
from unittest.mock import patch

import pytest

from integration.integration import fetch_events

MOCK_EVENT = {"conversation_id": 123, "event_name": "START", "event_at": 1710000000}


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
