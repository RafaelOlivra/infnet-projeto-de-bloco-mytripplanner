import json

from unittest.mock import patch
from services.Trip import Trip
from services.TripData import TripData
from services.Logger import _log

from tests.mocks import mock_trip_dict, mock_trip_csv_new_date

# --------------------------
# CRUD Tests
# --------------------------


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


# --------------------------
# Meta Tests
# --------------------------


def test_get_trip_meta():
    # Create a new trip
    trip = Trip(trip_data=mock_trip_dict())

    # Check if the trip meta was retrieved correctly
    assert trip.get_meta("sentiment") == "POSITIVE"


# Test updating a meta property from the trip
@patch("services.TripData.AppData.save")
def test_update_trip_meta(app_data_save_mock):

    # Create a mock instance of AppData
    app_data_save_mock.return_value = True

    # Create a new trip
    trip = Trip(trip_data=mock_trip_dict())

    # _log(trip["meta"])

    # Update the trip meta
    trip.update_meta("feedback", "Nice trip")

    # Check if the trip meta was updated correctly
    assert trip.get_meta("feedback") == "Nice trip"


# Test deleting a meta property from the trip
@patch("services.TripData.AppData.save")
def test_delete_trip_meta(app_data_save_mock):
    # Create a mock instance of AppData
    app_data_save_mock.return_value = True

    # Create a new trip
    trip = Trip(trip_data=mock_trip_dict())

    # Delete the trip meta
    trip.delete_meta("feedback")

    # Check if the trip meta was deleted correctly
    assert trip.get_meta("feedback") is None


# --------------------------
# Import/Export Testes
# --------------------------
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
