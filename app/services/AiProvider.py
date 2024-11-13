from datetime import datetime, date, timedelta
from typing import List, Optional

from services.AppData import AppData
from services.Logger import SimpleLogger

from models.Weather import ForecastModel
from models.Itinerary import ItineraryModel

from lib.Utils import Utils


class AiProvider:
    def __init__(self):

        self.prompt_file = AppData().get_config("assistant_base_prompt")

    def ask(self, message: str) -> dict:
        raise NotImplementedError("Ask method must be implemented in child class")

    def _generate_final_prompt(
        self, forecast_list: List[ForecastModel], start_date: date, end_date: date
    ) -> str:
        return ""

    def _generate_weather_summary(
        self, forecast_list: List[ForecastModel], start_date: date, end_date: date
    ) -> str:
        days = (end_date - start_date).days

        summary = ""
        for day in range(days + 1):
            day = start_date + timedelta(days=day)

            # Find the forecast for the current day
            forecast = None
            for f in forecast_list:
                if Utils.to_date_string(f.date) == Utils.to_date_string(day):
                    forecast = f
                    break

            if forecast is not None:
                summary += f"{Utils.to_date_string(day)} - {forecast.weather} \n"
            else:
                summary += f"{Utils.to_date_string(day)} - Não há dados do tempo \n"
        return summary

    def _load_base_prompt(self) -> str:
        return self.prompt
