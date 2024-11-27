from models.Weather import ForecastModel

from services.Logger import _log

from views.WeatherView import WeatherView

from tests.test_Trip import mock_trip_model, mock_trip


def mock_weather() -> list[ForecastModel]:
    return mock_trip_model().weather


def mock_weather_model() -> ForecastModel:
    return mock_weather()[0]


def test_render_forecast():
    city_name = mock_trip_model().destination_city
    state_name = mock_trip_model().destination_state
    days = mock_trip()._calculate_trip_length(
        mock_trip_model().start_date, mock_trip_model().end_date
    )

    weather = mock_weather()
    weather_view = WeatherView(city_name, state_name, days, weather)

    rendered_forecast = weather_view.render_forecast()

    assert rendered_forecast
