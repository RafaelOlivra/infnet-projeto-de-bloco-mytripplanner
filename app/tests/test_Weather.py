from services.Logger import _log
from views.WeatherView import WeatherView

from tests.mocks import mock_forecast_list, mock_trip_model, mock_trip


# --------------------------
# WeatherView Tests
# --------------------------


def test_render_forecast():
    city_name = mock_trip_model().destination_city
    state_name = mock_trip_model().destination_state
    days = mock_trip()._calculate_trip_length(
        mock_trip_model().start_date, mock_trip_model().end_date
    )

    weather = mock_forecast_list()
    weather_view = WeatherView(city_name, state_name, days, weather)

    rendered_forecast = weather_view.render_forecast()

    assert rendered_forecast
