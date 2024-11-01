import datetime

from lib.Utils import Utils

from services.AttractionsData import AttractionsData
from services.YelpScrapper import YelpScrapper

from models.Attraction import AttractionModel

from views.AttractionsView import AttractionsView


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


# Test retrieving attractions from the cache
def test_AttractionsData_get():
    limit = 30
    slug = "sp_sao-paulo"

    # Remove any existing data
    AttractionsData().delete(slug)
    assert AttractionsData().get(slug) == None

    # Retrieve new data
    view = AttractionsView(city_name="São Paulo", state_name="SP")

    # Act
    results = AttractionsData().get(slug)

    # Assert
    assert results is not None
    assert len(results) == limit
    assert type(results[0]) == AttractionModel
    current_time = datetime.datetime.now()
    assert Utils.to_datetime(results[0].created_at) < current_time
