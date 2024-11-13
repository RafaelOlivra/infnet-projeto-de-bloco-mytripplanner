import datetime
import json

from unittest.mock import patch

from lib.Utils import Utils
from services.AttractionsData import AttractionsData
from services.YelpScrapper import YelpScrapper
from models.Attraction import AttractionModel
from views.AttractionsView import AttractionsView

from tests.test_Trip import mock_trip_dict


# Mock data for testing
def mock_attractions():
    attraction_data = mock_trip_dict()["attractions"][0]
    return [AttractionModel(**attraction_data)]


# Test slug generation
def test_AttractionsData_slug():
    # Arrange
    city_name = "Rio de Janeiro"
    state_name = "RJ"

    # Act
    result = AttractionsData().slugify(city_name, state_name)

    # Assert
    assert result == "rj_rio-de-janeiro"


# Test retrieving more than 10 attractions from Yelp
def test_YelpScrapper_get_near_attractions():
    # Arrange
    city_name = "São Paulo"
    state_name = "SP"
    start = 0
    limit = 19

    # Act
    results = YelpScrapper().get_near_attractions(
        city_name=city_name, state_name=state_name, start=start, limit=limit
    )

    # Assert
    assert len(results) == limit
    assert type(results[0]) == AttractionModel


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
    json_data = "[" + mock_attractions()[0].model_dump_json() + "]"
    app_data_get_mock.return_value = json.loads(json_data)

    limit = 1
    slug = "rj_arraial-do-cabo"

    # Act
    results = AttractionsData().get(slug)

    # Assert
    assert results is not None
    assert results[0].description == mock_attractions()[0].description
    assert len(results) == limit
    assert type(results[0]) == AttractionModel
    current_time = datetime.datetime.now()
    assert Utils.to_datetime(results[0].created_at) < current_time
