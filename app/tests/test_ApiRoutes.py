import pytest
from fastapi.testclient import TestClient
from fastapi import status
from unittest import mock
from unittest.mock import patch

from routes.api import app, ApiKeyHandler
from services.TripData import TripData
from services.Trip import Trip

from tests.test_Trip import mock_trip_data

# Create a test client for the FastAPI app
client = TestClient(app)

demo_key = "ABCDEFGHIJKLMNOPQRSTUVWXYZ012345:0"  # :0 is the user_id
headers = {"X-API-Key": demo_key}
user_id = 0


@patch("routes.api.ApiKeyHandler._get_raw_keys")
def test_get_api_keys(mock__get_raw_keys):
    mock__get_raw_keys.return_value = demo_key

    keys = ApiKeyHandler().get_available_keys()
    assert keys == [{"ABCDEFGHIJKLMNOPQRSTUVWXYZ012345": 0}]


def test_no_api_key():
    response = client.post(f"/trip", headers=headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN


@patch("services.TripData.TripData.get_user_trips")
@patch("routes.api.ApiKeyHandler._get_raw_keys")
def test_get_user_trips(mock__get_raw_keys, mock_trip_data_get_user_trips):
    mock__get_raw_keys.return_value = demo_key
    mock_trip_data_get_user_trips.return_value = [
        TripData()._to_trip_model(trip_data=mock_trip_data())
    ]

    response = client.get(f"/trips", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()[0]["slug"] == [mock_trip_data()][0]["slug"]


@patch("services.TripData.TripData.get_user_trip")
@patch("routes.api.ApiKeyHandler._get_raw_keys")
def test_get_user_trip(mock__get_raw_keys, mock_trip_data_get_user_trip):
    mock__get_raw_keys.return_value = demo_key
    mock_trip_data_get_user_trip.return_value = TripData()._to_trip_model(
        trip_data=mock_trip_data()
    )

    trip_id = mock_trip_data()["id"]
    response = client.get(f"/trip/?trip_id={trip_id}", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["slug"] == mock_trip_data()["slug"]


@patch("services.TripData.AppData.save")
@patch("services.TripData.TripData.get_user_trip")
@patch("routes.api.ApiKeyHandler._get_raw_keys")
def test_create_user_trip(
    mock__get_raw_keys, mock_trip_data_get_user_trip, mock_app_data_save
):
    mock__get_raw_keys.return_value = demo_key
    mock_trip_data_get_user_trip.return_value = [
        TripData()._to_trip_model(trip_data=mock_trip_data())
    ]
    mock_app_data_save.return_value = True

    response = client.post(f"/trip", headers=headers, json=mock_trip_data())
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["slug"] == mock_trip_data()["slug"]


@patch("routes.api.ApiKeyHandler._get_raw_keys")
def test_create_user_trip_no_data(mock__get_raw_keys):
    mock__get_raw_keys.return_value = demo_key

    response = client.post(f"/trip", headers=headers)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@patch("routes.api.ApiKeyHandler._get_raw_keys")
def test_delete_user_trip(mock__get_raw_keys):
    mock__get_raw_keys.return_value = demo_key

    # Create a new trip
    trip = Trip(trip_data=mock_trip_data())
    trip_id = trip.get("id")

    response = client.delete(f"/trip/?trip_id={trip_id}", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["detail"] == "Trip deleted successfully"

    trip.delete()  # Clean up
