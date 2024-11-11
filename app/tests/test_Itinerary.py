import json
import pytest

from datetime import datetime, time

from unittest.mock import patch
from models.Itinerary import ItineraryModel, ActivityModel


# Mock data for testing
def mock_itinerary():
    return [
        ItineraryModel(
            date=datetime.datetime.now(),
            items=[
                {
                    "start_time": time(8, 0),
                    "end_time": time(10, 0),
                    "location": "Test",
                    "title": "Test",
                    "description": "Test",
                },
                {
                    "start_time": time(10, 0),
                    "end_time": time(12, 0),
                    "location": "Test 2",
                    "title": "Test 3",
                    "description": "Test 5",
                },
            ],
        )
    ]


def mock_activity():
    return ActivityModel(
        start_time=time(8, 0),
        end_time=time(10, 0),
        location="Test",
        title="Test",
        description="Test description",
    )


def test_invalid_time_order():
    activity = mock_activity().model_dump()
    activity["start_time"] = time(12, 0)

    # Test that the function raises a ValueError
    with pytest.raises(ValueError):
        ActivityModel(**activity)
