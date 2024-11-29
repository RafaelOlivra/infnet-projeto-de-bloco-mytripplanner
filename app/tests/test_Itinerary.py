import pytest

from datetime import time

from unittest.mock import patch
from models.Itinerary import ActivityModel

from tests.mocks import mock_activity

# --------------------------
# Itinerary Tests
# --------------------------


def test_invalid_time_order():
    activity = mock_activity().model_dump()
    activity["start_time"] = time(12, 0)

    # Test that the function raises a ValueError
    with pytest.raises(ValueError):
        ActivityModel(**activity)
