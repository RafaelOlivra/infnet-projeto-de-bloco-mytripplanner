import json
import pytest

from datetime import datetime, time

from unittest.mock import patch
from models.Itinerary import DailyItineraryModel, ActivityModel

from tests.test_Trip import mock_trip_dict


# Mock data for testing
def mock_itinerary() -> list[DailyItineraryModel]:
    attraction_data = mock_trip_dict()["itinerary"]
    return [DailyItineraryModel(**attraction) for attraction in attraction_data]

    # itinerary = {
    #     "date": datetime.now(),
    #     "title": "Day 1",
    #     "items": [
    #         {
    #             "start_time": time(8, 0),
    #             "end_time": time(10, 0),
    #             "location": "Test",
    #             "title": "Test",
    #             "description": "Test",
    #         },
    #         {
    #             "start_time": time(10, 0),
    #             "end_time": time(12, 0),
    #             "location": "Test 2",
    #             "title": "Test 3",
    #             "description": "Test 5",
    #         },
    #     ],
    # }
    # return [DailyItineraryModel(**itinerary)]


def mock_activity():
    activity = mock_itinerary()[0].items[0].model_dump()
    return ActivityModel(**activity)


def test_invalid_time_order():
    activity = mock_activity().model_dump()
    activity["start_time"] = time(12, 0)

    # Test that the function raises a ValueError
    with pytest.raises(ValueError):
        ActivityModel(**activity)
