import datetime
import json
import pytest

from unittest.mock import patch

from lib.Utils import Utils
from services.AttractionsData import AttractionsData
from services.Logger import _log
from services.YelpAttractionsScrapper import YelpAttractionsScrapper
from app.services.GooglePlacesAttractionsScrapper import GooglePlacesAttractionsScrapper

from models.Attraction import AttractionModel

from tests.mocks import mock_attraction, mock_attractions


# --------------------------
# CRUD Tests
# --------------------------


# Test slug generation
def test_AttractionsData_slug():
    # Arrange
    city_name = "Rio de Janeiro"
    state_name = "RJ"

    # Act
    result = AttractionsData().slugify(city_name, state_name)

    # Assert
    assert result == "rj_rio-de-janeiro"


# Test saving attractions
@patch("services.AttractionsData.AppData.save")
def test_AttractionsData_save(app_data_save_mock):
    # Create a mock instance of AppData
    app_data_save_mock.return_value = True

    # Arrange
    slug = "rj_arraial-do-cabo"
    attractions = mock_attractions()

    # Act
    results = AttractionsData().save(attractions, slug)

    # Assert
    assert results is True


# Test retrieving attractions
@patch("services.AttractionsData.AppData.get")
def test_AttractionsData_get(app_data_get_mock):
    # Create a mock instance of AppData
    json_data = "[" + mock_attraction().model_dump_json() + "]"
    app_data_get_mock.return_value = json.loads(json_data)

    limit = 1
    slug = "rj_arraial-do-cabo"

    # Act
    results = AttractionsData().get(slug)

    # Assert
    assert results is not None
    assert results[0].description == mock_attraction().description
    assert len(results) == limit
    assert type(results[0]) == AttractionModel
    current_time = datetime.datetime.now()
    assert Utils.to_datetime(results[0].created_at) < current_time


# --------------------------
# Yelp Integration Tests
# --------------------------


# Test retrieving more than 10 attractions from Yelp
@pytest.mark.skip(reason="Yelp API rate limit exceeded")
def test_YelpScrapper_get_near_attractions():
    # Arrange
    city_name = "São Paulo"
    state_name = "SP"
    start = 0
    limit = 19

    # Act
    results = YelpAttractionsScrapper().get_near_attractions(
        city_name=city_name, state_name=state_name, start=start, limit=limit
    )

    # Assert
    assert len(results) == limit
    assert type(results[0]) == AttractionModel


# --------------------------
# Google Maps Attractions Integration Tests
# --------------------------


# Test retrieving more than 10 attractions from Google Maps
def test_GoogleMapsScrapper_get_near_attractions():
    # Arrange
    city_name = "São Paulo"
    state_name = "SP"
    start = 0
    limit = 19

    # Act
    results = GooglePlacesAttractionsScrapper().get_near_attractions(
        city_name=city_name, state_name=state_name, start=start, limit=limit
    )

    # Assert
    assert len(results) == limit
    assert type(results[0]) == AttractionModel
