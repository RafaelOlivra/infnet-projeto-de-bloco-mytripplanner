import yaml
from datetime import datetime, date, timedelta
from typing import List, Optional

from services.AppData import AppData
from services.Logger import SimpleLogger

from models.Weather import ForecastModel
from models.Itinerary import ItineraryModel
from models.Attraction import AttractionModel

from lib.Utils import Utils


class AiProvider:
    def __init__(self):
        self.prompt_file = AppData().get_config("ai_config_file")
        self.reserved_templates = [
            "%%LOCATION%%",
            "%%WEATHER%%",
            "%%ATTRACTIONS%%",
        ]
        self.prompt = None

    def ask(self, message: str) -> dict:
        raise NotImplementedError("Ask method must be implemented in child class")

    def _generate_final_prompt(
        self,
        location: str,
        start_date: date,
        end_date: date,
        forecast_list: List[ForecastModel],
        attractions_list: List[AttractionModel],
        base_prompt: str = None,
    ) -> str:
        # Allow prompt to be overridden
        prompt = base_prompt if base_prompt else self._load_base_prompt()

        # Set the location
        location = self._strip_reserved_templates(location)
        prompt = prompt.replace("%%LOCATION%%", location)

        # Set the weather
        weather = self._generate_weather_summary(
            forecast_list=forecast_list, start_date=start_date, end_date=end_date
        )
        weather = self._strip_reserved_templates(weather)
        prompt = prompt.replace("%%WEATHER%%", weather)

        # Set the attractions
        attractions = self._generate_attractions_summary(attractions_list)
        attractions = self._strip_reserved_templates(attractions)
        prompt = prompt.replace("%%ATTRACTIONS%%", attractions)

        return prompt

    def _generate_weather_summary(
        self, forecast_list: List[ForecastModel], start_date: date, end_date: date
    ) -> str:

        if not forecast_list:
            return "* Não há dados do tempo disponíveis"

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
                summary += f"* {Utils.to_date_string(day)} - {forecast.weather} \n"
            else:
                summary += f"* {Utils.to_date_string(day)} - Não há dados do tempo \n"
        return summary

    def _generate_attractions_summary(
        self, attractions_list: List[AttractionModel]
    ) -> str:

        if not attractions_list:
            return "* Não há atrações disponíveis"

        locations = ""
        for attraction in attractions_list:
            locations += f"* {attraction.name} - {attraction.city_name}, {attraction.state_name} \n"
        return locations

    def _load_base_prompt(self) -> str:

        if self.prompt:
            return self.prompt

        with open(self.prompt_file, "r") as file:
            data = yaml.safe_load(file)
            self.prompt = data["prompt"]
            return self.prompt

    def _strip_reserved_templates(self, text: str) -> str:
        for template in self.reserved_templates:
            text = text.replace(template, "")
        return text
