import json
import pytest
import time
from datetime import datetime, timedelta

from unittest.mock import patch
from models.Trip import TripModel
from services.Trip import Trip
from services.TripData import TripData
from services.Logger import _log


# Mock trip data for testing
start_date = datetime.now().isoformat()
end_date = (datetime.now() + timedelta(days=2)).isoformat()


def mock_trip_dict() -> dict:
    return {
        "id": "00000000-0000-0000-0000-000000000000",
        "user_id": 0,
        "created_at": "2024-10-15T00:00:00",
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
        "start_date": start_date,
        "end_date": end_date,
        "weather": [
            {
                "timestamp": 1729026000,
                "date": start_date,
                "city_name": "Arraial do Cabo",
                "state_name": "RJ",
                "temperature": None,
                "temperature_min": 23.27,
                "temperature_max": 23.92,
                "weather": "nuvens dispersas",
                "wind_speed": 9.41,
            },
            {
                "timestamp": 1729209600,
                "date": end_date,
                "city_name": "Arraial do Cabo",
                "state_name": "RJ",
                "temperature": None,
                "temperature_min": 23.27,
                "temperature_max": 23.92,
                "weather": "chuva moderada",
                "wind_speed": 9.41,
            },
        ],
        "attractions": [
            {
                "id": "5d609698-9323-4ec3-84f4-fb557ecae7a5",
                "city_name": "Arraial do Cabo",
                "state_name": "RJ",
                "name": "Praia do Arrail",
                "url": "https://www.yelp.com/biz/arraial-do-cabo-arraial-do-cabo",
                "review_count": 6,
                "review_stars": 4.7,
                "description": "",
                "image": "https://s3-media0.fl.yelpcdn.com/bphoto/9t3__2a-LlPTLdosAVXgOw/348s.jpg",
            },
            {
                "id": "00000000-0000-4ec3-84f4-fb557ecae7a5",
                "city_name": "Arraial do Cabo",
                "state_name": "RJ",
                "name": "Atração Genérica",
                "url": "https://www.yelp.com/biz/arraial-do-cabo-arraial-do-cabo",
                "review_count": 1000,
                "review_stars": 3.0,
                "description": "",
                "image": "https://s3-media0.fl.yelpcdn.com/bphoto/9t3__2a-LlPTLdosAVXgOw/348s.jpg",
            },
        ],
        "itinerary": [
            {
                "date": start_date,
                "title": "Dia 1",
                "items": [
                    {
                        "start_time": "09:00",
                        "end_time": "11:00",
                        "location": "Praia do Arrail - Arraial do Cabo, RJ",
                        "title": "Manhã na Praia do Arrail",
                        "description": "Aproveite a manhã relaxando na Praia do Arrail com nuvens dispersas.",
                    },
                    {
                        "start_time": "11:30",
                        "end_time": "13:00",
                        "location": "Centro de Arraial do Cabo, RJ",
                        "title": "Almoço em Restaurante Local",
                        "description": "Desfrute de pratos tradicionais em um restaurante aconchegante no centro.",
                    },
                ],
            },
            {
                "date": end_date,
                "title": "Dia 2",
                "items": [
                    {
                        "start_time": "09:00",
                        "end_time": "11:00",
                        "location": "Atração Genérica - Arraial do Cabo, RJ",
                        "title": "Exploração da Atração Genérica",
                        "description": "Descubra os encantos locais da Atração Genérica em Arraial do Cabo.",
                    },
                    {
                        "start_time": "11:30",
                        "end_time": "13:00",
                        "location": "Praia dos Anjos - Arraial do Cabo, RJ",
                        "title": "Relaxamento na Praia dos Anjos",
                        "description": "Desfrute do sol e do mar nesta bela praia.",
                    },
                ],
            },
        ],
        "goals": "Test",
        "notes": "This is a test note",
        "tags": ["teste"],
        "summary": "This is a test summary",
        "meta": [
            {
                "feedback": "Nice trip",
                "sentiment": "POSITIVE",
            }
        ],
    }


def mock_trip() -> Trip:
    return Trip(trip_data=mock_trip_dict(), save=False)


def mock_trip_model() -> TripModel:
    return mock_trip().model


def mock_trip_csv_new_date():
    trip = mock_trip_dict()
    csv = Trip(trip_data=trip, save=False).to_csv()
    return csv


def mock_trip_csv_old_date():
    trip = mock_trip_dict()
    trip["start_date"] = "2023-11-16T00:00:00"
    trip["end_date"] = "2023-11-17T00:00:00"
    csv = Trip(trip_data=trip, save=False).to_csv()
    return csv


# Test creating a new trip
@patch("services.TripData.AppData.save")
def test_create_trip(app_data_save_mock):
    # Create a mock instance of AppData
    app_data_save_mock.return_value = True

    # Create a new trip
    trip = Trip(trip_data=mock_trip_dict())

    # Check if the trip was created correctly
    assert trip.get("slug") == mock_trip_dict()["slug"]


# Test getting a property from the trip
@patch("services.TripData.AppData.save")
def test_get_trip_property(app_data_save_mock):
    # Create a mock instance of AppData
    app_data_save_mock.return_value = True

    # Create a new trip
    trip = Trip(trip_data=mock_trip_dict())

    # Check if the property is correct
    assert trip.get("title") == "Teste"


# Test updating a trip
@patch("services.TripData.AppData.save")
def test_update_trip(app_data_save_mock):

    # Create a mock instance of AppData
    app_data_save_mock.return_value = True

    # Create a new trip
    trip = Trip(trip_data=mock_trip_dict())

    # Update the trip
    trip.update({"title": "Updated title"})

    # Check if the trip was updated correctly
    assert trip.model.title == "Updated title"


# Test deleting a trip
def test_delete_trip():
    # Create a new trip
    trip = Trip(trip_data=mock_trip_dict())

    # Delete the trip
    trip_id = trip.get("id")
    trip.delete()

    # Check if the trip was deleted correctly
    assert TripData().get(trip_id=trip_id) is None


def test_export_trip_json():
    # Create a new trip
    trip = Trip(trip_data=mock_trip_dict())

    # Export the trip to JSON
    json_data = trip.to_json()

    # Check if the trip was exported correctly
    assert json.loads(json_data)["slug"] == "teste"


def test_export_trip_csv():
    # Create a new trip
    trip = Trip(trip_data=mock_trip_dict())

    # Export the trip to CSV
    csv_data = trip.to_csv()
    csv_header = csv_data.split("\n")[0]

    # Check if the trip was exported correctly
    assert csv_data.split("\n")[1].split(",")[3] == "teste"
    assert "weather_base64" in csv_header
    assert "attractions_base64" in csv_header
    assert "itinerary_base64" in csv_header
    assert "weather," not in csv_header
    assert "attractions," not in csv_header
    assert "itinerary," not in csv_header
    assert "meta," not in csv_header

    # _log(csv_data)


@patch("services.TripData.AppData.save")
def test_import_trip_csv(app_data_save_mock):
    # Create a mock instance of AppData
    app_data_save_mock.return_value = True

    # Create a new trip
    trip = Trip().from_csv(mock_trip_csv_new_date())
    trip_model = trip.model

    # _log(trip.to_json())

    # Check if the trip was imported correctly
    assert trip["slug"] == "teste"
    assert trip["weather"][0].city_name == "Arraial do Cabo"
    assert trip["itinerary"][0].title is not ""


@patch("services.TripData.AppData.save")
def test_import_trip_json(app_data_save_mock):
    # Create a mock instance of AppData
    app_data_save_mock.return_value = True

    trip = Trip().from_csv(mock_trip_csv_new_date())
    json_data = trip.to_json()

    # Create a new trip
    trip = Trip().from_json(json_data)

    # Check if the trip was imported correctly
    assert trip["slug"] == "teste"
