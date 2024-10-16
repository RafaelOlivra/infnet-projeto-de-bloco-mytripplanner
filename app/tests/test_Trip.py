import json
import pytest
import time

from unittest.mock import patch
from services.Trip import Trip


@pytest.fixture
def mock_trip_data():
    # Sample JSON data for testing
    return {
        "id": "00000000-0000-0000-0000-000000000000",
        "user_id": 0,
        "slug": "teste",
        "title": "Teste",
        "origin_city": "\u00c1guas de Santa B\u00e1rbara",
        "origin_state": "SP",
        "origin_longitude": -22.8812164,
        "origin_latitude": -49.2397734,
        "destination_city": "Arraial do Cabo",
        "destination_state": "RJ",
        "destination_longitude": -22.9667613,
        "destination_latitude": -42.0277716,
        "travel_by": "driving",
        "start_date": "2024-10-15T00:00:00",
        "end_date": "2024-10-22T00:00:00",
        "weather": [
            {
                "timestamp": 1729026000,
                "date": "2024-10-15 00:00:00",
                "city_name": "Arraial do Cabo",
                "state_name": "RJ",
                "temperature": None,
                "temperature_min": 23.27,
                "temperature_max": 23.92,
                "weather": "nuvens dispersas",
                "wind_speed": 9.41,
            },
        ],
        "attractions": [
            {
                "id": "5d609698-9323-4ec3-84f4-fb557ecae7a5",
                "city_name": "Arraial do Cabo",
                "state_name": "RJ",
                "name": "Arraial do Cabo",
                "url": "https://www.yelp.com/biz/arraial-do-cabo-arraial-do-cabo",
                "review_count": 6,
                "review_stars": 4.7,
                "description": "",
                "image": "https://s3-media0.fl.yelpcdn.com/bphoto/9t3__2a-LlPTLdosAVXgOw/348s.jpg",
            },
        ],
        "goals": "Test",
        "notes": "This is a test note",
        "tags": ["teste"],
    }


# Test creating a new trip
@patch("services.TripData.AppData.save")
def test_create_trip(app_data_mock, mock_trip_data):

    # Create a mock instance of AppData
    app_data_mock.return_value.return_value = True

    # Create a new trip
    trip = Trip(trip_data=mock_trip_data)

    # Check if the trip was created correctly
    assert trip.model.id == mock_trip_data["id"]


# Test updating a trip
@patch("services.TripData.AppData.save")
def test_update_trip(app_data_mock, mock_trip_data):

    # Create a mock instance of AppData
    app_data_mock.return_value.return_value = True

    # Create a new trip
    trip = Trip(trip_data=mock_trip_data)

    # Update the trip
    trip.update({"title": "Updated title"})

    # Check if the trip was updated correctly
    assert trip.model.title == "Updated title"


# Test deleting a trip
def test_delete_trip(mock_trip_data):

    # Create a new trip
    trip = Trip(trip_data=mock_trip_data)

    # Delete the trip
    trip.delete()

    # Check if the trip was deleted correctly
    assert trip.model == None
