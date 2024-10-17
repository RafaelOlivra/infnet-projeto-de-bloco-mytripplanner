import pytest
from fastapi.testclient import TestClient
from fastapi import status
from unittest import mock
from unittest.mock import patch

from routes.api import app, ApiKeyHandler
from services.TripData import TripData
from tests.test_Trip import mock_trip_data

# Create a test client for the FastAPI app
client = TestClient(app)

demo_key = "ABCDEFGHIJKLMNOPQRSTUVWXYZ012345:demo"
headers = {"X-API-Key": "ABCDEFGHIJKLMNOPQRSTUVWXYZ012345"}


@patch("routes.api.ApiKeyHandler._get_raw_keys")
def test_get_api_keys(mock__get_raw_keys):
    mock__get_raw_keys.return_value = demo_key

    keys = ApiKeyHandler().get_available_keys()
    assert keys == {"ABCDEFGHIJKLMNOPQRSTUVWXYZ012345": "demo"}


@patch("services.TripData.TripData.get_all")
@patch("routes.api.ApiKeyHandler._get_raw_keys")
def test_get_all_trips(mock__get_raw_keys, mock_trip_data_get_all):
    mock__get_raw_keys.return_value = demo_key
    mock_trip_data_get_all.return_value = [
        TripData()._to_trip_model(trip_data=mock_trip_data())
    ]

    response = client.get("/trips", headers=headers)
    assert response.json() == [mock_trip_data()]
    assert response.status_code == status.HTTP_200_OK
