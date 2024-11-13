import json
import pytest

from datetime import datetime, time

from unittest.mock import patch
from services.AiProvider import AiProvider
from lib.Utils import Utils

from tests.test_Trip import mock_trip_model, mock_trip
from tests.test_Itinerary import mock_activity, mock_itinerary


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
    assert "2024-11-13T00:00:00 - nuvens dispersas" in summary
    assert "chuva moderada" in summary
    assert "Não há dados do tempo" in summary
