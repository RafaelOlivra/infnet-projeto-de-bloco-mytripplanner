import json
import pytest

from datetime import datetime, time

from unittest.mock import patch
from services.AiProvider import AiProvider
from services.Logger import _log
from lib.Utils import Utils

from tests.test_Trip import mock_trip_model, mock_trip
from tests.test_Itinerary import mock_activity, mock_itinerary
from tests.test_Attractions import mock_attractions


def mock_weather():
    return mock_trip_model().weather


def test_generate_weather_summary():
    ai_provider = AiProvider()
    forecast_list = mock_weather()
    start_date = Utils.to_datetime(mock_trip_model().start_date)
    end_date = Utils.to_datetime(mock_trip_model().end_date)

    summary = ai_provider._generate_weather_summary(
        forecast_list=forecast_list, start_date=start_date, end_date=end_date
    )

    date = Utils.to_datetime(forecast_list[0].date).isoformat()
    test_summary = date + " - " + forecast_list[0].weather

    assert test_summary in summary
    assert "chuva moderada" in summary
    assert "Não há dados do tempo" in summary


def test_generate_attractions_summary():
    ai_provider = AiProvider()
    attractions_list = mock_attractions()

    summary = ai_provider._generate_attractions_summary(
        attractions_list=attractions_list
    )

    test_summary = (
        "* "
        + attractions_list[0].name
        + " - "
        + attractions_list[0].city_name
        + ", "
        + attractions_list[0].state_name
    )

    assert test_summary in summary


def test_generate_final_prompt():
    ai_provider = AiProvider()

    location = (
        mock_trip_model().destination_city + ", " + mock_trip_model().destination_state
    )
    attractions_list = mock_attractions()
    forecast_list = mock_weather()
    start_date = Utils.to_datetime(mock_trip_model().start_date)
    end_date = Utils.to_datetime(mock_trip_model().end_date)

    prompt = ai_provider._generate_final_prompt(
        location=location,
        start_date=start_date,
        end_date=end_date,
        forecast_list=forecast_list,
        attractions_list=attractions_list,
    )

    # Check for the presence of the test strings

    # Location
    assert location in prompt

    # Weather summary
    date = Utils.to_datetime(forecast_list[0].date).isoformat()
    test_summary = date + " - " + forecast_list[0].weather
    assert test_summary in prompt

    # Attractions summary
    test_summary = (
        "* "
        + attractions_list[0].name
        + " - "
        + attractions_list[0].city_name
        + ", "
        + attractions_list[0].state_name
    )
    assert test_summary in prompt
