import yaml
import json
import re

from datetime import date, timedelta
from typing import List

from services.AppData import AppData
from services.Logger import _log

from models.Weather import ForecastModel
from models.Itinerary import DailyItineraryModel
from models.Attraction import AttractionModel
from models.Trip import TripModel

from lib.Utils import Utils


class AiProvider:
    """
    Abstract class for AI providers.
    Provides methods to interact with an AI provider, prepare data for the provider, and generate trip artifacts.
    """

    def __init__(self):
        self.config_file = AppData().get_config("ai_config_file")
        self.reserved_templates = [
            "%%LOCATION%%",
            "%%WEATHER%%",
            "%%GOALS%%",
            "%%ATTRACTIONS%%",
            "%%TRAVEL_BY%%",
            "%%ITINERARY%%",
            "%%NO_OF_DAYS%%",
            "%%TRIP_JSON%%",
        ]
        self.gen_itinerary_prompt = None
        self.gen_trip_summary_prompt = None

        # Initialize empty data
        self.location = None
        self.start_date = None
        self.end_date = None
        self.forecast_list = None
        self.goals = None
        self.attractions_list = None
        self.trip_model = None

    def ask(self, prompt: str) -> dict[str, str]:
        """
        Main method to interact with the AI provider

        Args:
            prompt (str): The prompt to send to the AI provider.

        Returns:
            dict[str, str]: The response from the AI provider formatted
            as a dictionary containing a "response" key with the text response.
        """
        raise NotImplementedError("Ask method must be implemented in child class")

    def prepare(
        self,
        location: str = None,
        start_date: date = None,
        end_date: date = None,
        goals: str = None,
        forecast_list: List[ForecastModel] = None,
        attractions_list: List[AttractionModel] = None,
        trip_model: TripModel = None,
    ) -> dict:
        """
        Prepare the data for the AI provider.

        Args:
            location (str): The destination location (city, state)
            start_date (date): The start date of the trip
            end_date (date): The end date of the trip
            goals (str): The goals of the trip
            forecast_list (List[ForecastModel]): The weather forecast list
            attractions_list (List[AttractionModel]): The list of attractions
            trip_model (TripModel): The trip model object
        """

        self.location = location
        self.start_date = start_date
        self.end_date = end_date
        self.goals = goals
        self.forecast_list = forecast_list
        self.attractions_list = attractions_list
        self.trip_model = trip_model

    def generate_itinerary(self) -> List[DailyItineraryModel]:
        """
        Generate the itinerary for the trip.

        Returns:
            List[DailyItineraryModel]: The generated itinerary.
        """
        prompt = self._generate_prompt_from_template(
            template_key="gen_itinerary_prompt"
        )
        response = self.ask(prompt=prompt)
        _log(response, level="DEBUG")
        return self._to_itinerary(response) if response else []

    def generate_trip_summary(self) -> str:
        """
        Generate a summary of the trip.

        Returns:
            str: The generated trip summary
        """
        prompt = self._generate_prompt_from_template(
            template_key="gen_trip_summary_prompt"
        )
        response = self.ask(prompt=prompt)
        return response.get("response", "") if response else ""

    def prompt(self, prompt: str) -> str:
        """
        Prompt the AI provider with a custom prompt, and return the response text.

        Args:
            prompt (str): The custom prompt to send to the AI provider.

        Returns:
            str: The response from the AI provider.
        """
        response = self.ask(prompt=prompt)
        return response.get("response", "")

    def _generate_prompt_from_template(
        self,
        template_key: str = "gen_itinerary_prompt",
        base_prompt: str = None,
    ) -> str:
        """
        Generate a prompt from a template, replacing the variables with the data provided on the prepare() method.

        Args:
            template_key (str): The key of the template to use (Retrieved from the config file).
            base_prompt (str): The base prompt to use (overrides the template_key template).

        Returns:
            str: The final generated prompt.

        """
        # Allow prompt to be overridden
        prompt = (
            base_prompt
            if base_prompt
            else self._load_base_prompt(template_key=template_key)
        )

        # -- Prepare variables

        # %%NO_OF_DAYS%%
        start_date = self.start_date if self.start_date is not None else None
        start_date = (
            self.trip_model.start_date if self.trip_model is not None else start_date
        )
        end_date = self.end_date if self.end_date is not None else None
        end_date = self.trip_model.end_date if self.trip_model is not None else end_date

        # %%LOCATION%%
        location = self.location if self.location is not None else None
        location = (
            self.trip_model.destination_city + " - " + self.trip_model.destination_state
            if self.trip_model is not None
            else location
        )

        # %%WEATHER%%
        weather = self.forecast_list if self.forecast_list is not None else None
        weather = self.trip_model.weather if self.trip_model is not None else weather
        forecast_list = weather

        # %%GOALS%%
        goals = self.goals if self.goals is not None else None
        goals = self.trip_model.goals if self.trip_model is not None else goals

        # %%ATTRACTIONS%%
        attractions = (
            self.attractions_list if self.attractions_list is not None else None
        )
        attractions = (
            self.trip_model.attractions if self.trip_model is not None else attractions
        )

        # %%TRIP_JSON%%
        trip_model = self.trip_model if self.trip_model is not None else None
        if trip_model:
            trip_json = trip_model.model_dump_json()

        # %%ITINERARY%%
        itinerary = trip_model.itinerary if trip_model is not None else None

        # %%TRAVEL_BY%%
        travel_by = trip_model.travel_by if trip_model is not None else None

        # -- Replace variables

        # Set the number of days
        if start_date is not None and end_date is not None:
            trip_length = (end_date - start_date).days + 1

            # Set to max 4 days (for now)
            if trip_length > 4:
                trip_length = 4

            prompt = prompt.replace("%%NO_OF_DAYS%%", str(trip_length))

        # Set the location
        if location is not None:
            location = self._strip_reserved_templates(location)
            prompt = prompt.replace("%%LOCATION%%", location)

        # Set the weather
        if forecast_list is not None:
            weather = self._generate_weather_summary(
                forecast_list=forecast_list,
                start_date=start_date,
                end_date=end_date,
                strip_time=True,
            )
            weather = self._strip_reserved_templates(weather)
            prompt = prompt.replace("%%WEATHER%%", weather)

        # Set the goals
        if goals is not None:
            goals = self._strip_reserved_templates(goals)
            goals = goals.strip()
            if not goals:
                goals = "* Nenhum objetivo foi definido"
            else:
                goals = "* " + goals.replace("\n", "\n* ").replace("  ", " ")
            prompt = prompt.replace("%%GOALS%%", goals.strip())

        # Set the attractions
        if attractions is not None:
            attractions = self._generate_attractions_summary(attractions)
            attractions = self._strip_reserved_templates(attractions)
            prompt = prompt.replace("%%ATTRACTIONS%%", attractions)

        # Set the trip JSON
        if trip_model is not None:
            trip_json = self._strip_reserved_templates(trip_json)
            prompt = prompt.replace("%%TRIP_JSON%%", trip_json)

        # Set the itinerary
        if trip_model is not None:
            itinerary = self._generate_itinerary_summary(trip_model.itinerary)
            itinerary = self._strip_reserved_templates(itinerary)
            prompt = prompt.replace("%%ITINERARY%%", itinerary)

        # Set trip travel by
        if travel_by is not None:
            travel_by = self._strip_reserved_templates(travel_by)
            prompt = prompt.replace("%%TRAVEL_BY%%", travel_by)

        return prompt

    def _generate_weather_summary(
        self,
        forecast_list: List[ForecastModel],
        start_date: date,
        end_date: date,
        strip_time: bool = False,
    ) -> str:
        """
        Generate a summary of the weather forecast for the trip.

        Args:
            forecast_list (List[ForecastModel]): The list of weather forecasts.
            start_date (date): The start date of the trip.
            end_date (date): The end date of the trip.
            strip_time (bool): Whether to strip the time from the date.

        Returns:
            str: The generated weather summary.
        """
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

            # Strip the time from the date (The part after the T in the ISO format)
            day = Utils.to_date_string(day)
            if strip_time:
                day = day.split("T")[0]

            if forecast is not None:
                summary += f"* {day} - {forecast.weather} \n"
            else:
                summary += f"* {day} - Não há dados do tempo \n"
        return summary

    def _generate_attractions_summary(
        self, attractions_list: List[AttractionModel]
    ) -> str:
        """
        Generate a summary of the attractions for the trip.

        Args:
            attractions_list (List[AttractionModel]): The list of attractions.

        Returns:
            str: The generated attractions summary.
        """

        if not attractions_list:
            return "* Não há atrações disponíveis"

        locations = ""
        for attraction in attractions_list:
            locations += f"""* {attraction.name} - {
                attraction.city_name}, {attraction.state_name} \n"""
        return locations

    def _generate_itinerary_summary(self, itinerary: List[DailyItineraryModel]) -> str:
        """
        Generate a summary of the itinerary for the trip.

        Args:
            itinerary (List[DailyItineraryModel]): The itinerary for the trip.

        Returns:
            str: The generated itinerary summary.
        """
        if not itinerary:
            return "* Não há roteiro disponível"

        summary = ""
        for day in itinerary:
            summary += f"""### {Utils.to_date_string(day.date, format='display')} - {
                day.title} \n"""
            for activity in day.items:
                summary += f"""* [{Utils.to_time_string(activity.start_time)} - {Utils.to_time_string(
                    activity.end_time)}] {activity.title} | {activity.location}\n"""
        return summary

    def _to_json(self, response: dict) -> dict:
        """
        Convert the response from the AI provider to a JSON object.

        Args:
            response (dict): The response from the AI provider formatted
            as a dictionary containing a "response" key with the text response.

        Returns:
            dict: The response as a JSON object.
        """
        if not response or "response" not in response:
            return {}

        # Extract the response string
        response_str = response.get("response", "")

        # Use regex to remove the markdown code block formatting
        json_str = re.sub(r"```json\n|\n```", "", response_str).strip()

        # Parse the cleaned JSON string into a Python object
        parsed_json = json.loads(json_str)

        return parsed_json

    def _to_itinerary(self, response: dict) -> List[DailyItineraryModel]:
        """
        Convert the response from the AI provider to a list of DailyItineraryModel objects.

        Args:
            response (dict): The response from the AI provider formatted
            as a dictionary containing a "response" key with the text response.

        Returns:
            List[DailyItineraryModel]: The generated itinerary.
        """
        json = self._to_json(response)

        if not json:
            return []

        return [DailyItineraryModel(**itinerary) for itinerary in json]

    def _load_base_prompt(self, template_key: str = "gen_itinerary_prompt") -> str:
        """
        Load the base prompt from the config file.

        Args:
            template_key (str): The key of the template to load from the config file.

        Returns:
            str: The loaded base prompt.
        """
        if self.get(template_key):
            return self.get(template_key)

        with open(self.config_file, "r", encoding="utf-8") as file:
            data = yaml.safe_load(file)
            return self.set(template_key, data[template_key])

    def _override_base_prompt(
        self, prompt: str = "", template_key: str = "gen_itinerary_prompt"
    ) -> None:
        """
        Override the base prompt with a custom prompt.

        Args:
            prompt (str): The custom prompt to set
            template_key (str): The key of the template to override
        """
        self.set(template_key, prompt)

    def _strip_reserved_templates(self, text: str) -> str:
        """
        Remove the reserved templates from the text.

        Args:
            text (str): The text to remove the templates from.

        Returns:
            str: The text with the templates removed.
        """
        for template in self.reserved_templates:
            text = text.replace(template, "")
        return text

    def get(self, name):
        """
        Get the value of an attribute by name.

        Args:
            name (str): The name of the attribute to get.

        Returns:
            Any: The value of the attribute.
        """
        return getattr(self, name)

    def set(self, name, value):
        """
        Set the value of an attribute by name.

        Args:
            name (str): The name of the attribute to set.
            value (Any): The value to set.

        Returns:
            Any: The value that was set.
        """
        setattr(self, name, value)
        return value
