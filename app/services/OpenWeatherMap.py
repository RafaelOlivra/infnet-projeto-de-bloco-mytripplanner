import requests
import streamlit as st
from datetime import datetime, timedelta

from services.AppData import AppData
from services.LatLong import LatLong

from models.WeatherModel import ForecastModel, WeatherModel
from typing import List


class OpenWeatherMap:
    def __init__(self, api_key=None):
        # Set the API key, either from the environment or directly from the parameter
        self.api_key = api_key or AppData().get_api_key("openweathermap")
        if not self.api_key:
            raise ValueError("API key is required for OpenWeatherMap")

    # --------------------------
    # Coordinate Operations
    # --------------------------
    def get_coordinates(_self, city_name: str, state_name: str):
        """
        Retrieves the latitude and longitude coordinates of a given city and state.

        Parameters:
            city_name (str): The name of the city.
            state_name (str): The name of the state.

        Returns:
            tuple: A tuple containing the latitude and longitude coordinates of the city.
        """
        return LatLong().get_coordinates(city_name, state_name)

    def get_coordinates_from_openweathermap(_self, city_name: str, state_name: str):
        """
        Retrieves the latitude and longitude coordinates of a given city and state.

        Parameters:
            city_name (str): The name of the city.
            state_name (str): The name of the state.

        Returns:
            tuple: A tuple containing the latitude and longitude coordinates of the city.
        """
        data = _self._fetch_json(
            url=f"http://api.openweathermap.org/geo/1.0/direct?q={_self._url_encode(city_name)},{_self._url_encode(state_name)},Brazil&lang=pt_br&appid={_self.api_key}"
        )
        return data[0]["lat"], data[0]["lon"]

    # --------------------------
    # Forecast Operations
    # --------------------------
    def get_hourly_forecast(
        _self, city_name: str, state_name: str, days: int = 5
    ) -> List[ForecastModel]:
        """
        Retrieves the weather forecast for a given city and state.

        Args:
            city_name (str): The name of the city.
            state_name (str): The name of the state.
            days (int, optional): The number of days to retrieve the forecast for. Defaults to 5.

        Returns:
            List[ForecastModel]: A list of forecast data for each hour.
        """
        lat, long = _self.get_coordinates(city_name, state_name)
        data = _self._fetch_json(
            url=f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={long}&units=metric&lang=pt_br&appid={_self.api_key}"
        )

        forecast_list = data["list"]
        hourly_forecast = {}
        current_date = datetime.now().date()

        for forecast in forecast_list:
            forecast_timestamp = int(forecast["dt"])
            forecast_datetime = datetime.fromtimestamp(forecast_timestamp)
            forecast_date = forecast_datetime.date()
            forecast_date_str = _self._format_date(
                forecast_timestamp
            )  # International datetime

            # Check if we are still within the selected days
            if forecast_date > current_date + timedelta(days=int(days)):
                break

            # Check if the forecast is for the current day
            if forecast_date_str not in hourly_forecast:
                hourly_forecast[forecast_date_str] = []

            hourly_forecast[forecast_date_str] = {
                "timestamp": forecast_timestamp,
                "date": forecast_date_str,
                "city_name": city_name,
                "state_name": state_name,
                "temperature": forecast["main"]["temp"],
                "weather": forecast["weather"][0]["description"],
                "wind_speed": forecast["wind"]["speed"],
            }

        return _self._to_forecast_list(hourly_forecast)

    def get_forecast_for_next_5_days(
        _self, city_name: str, state_name: str
    ) -> List[ForecastModel]:
        """
        Retrieves the daily weather forecast for the next 'days' days by aggregating hourly forecast data.

        Args:
            city_name (str): The name of the city.
            state_name (str): The name of the state.
            days (int, optional): The number of days to retrieve the forecast for. Defaults to 5.

        Returns:
            List[ForecastModel]: A list of forecast data for each day.
        """
        # Reuse the hourly forecast function to get all the hourly data
        hourly_forecast = _self.get_hourly_forecast(
            city_name, state_name, days=5
        )  # Fetching for the next 5 days

        # Dictionary to hold the aggregated daily data
        daily_forecast = {}

        # Iterate over each forecast entry in hourly_forecast
        for forecast in hourly_forecast:

            # Convert the forecast object to a dictionary
            forecast = forecast.dict()

            # Extract the date part from the "date" field (YYYY-MM-DD)
            date_str = forecast["date"].split("T")[0]

            # Initialize daily forecast data if this is the first entry for this day
            if date_str not in daily_forecast:

                daily_forecast[date_str] = {
                    "date": date_str,
                    "timestamp": forecast["timestamp"],
                    "city_name": city_name,
                    "state_name": state_name,
                    "temperature_min": float("inf"),
                    "temperature_max": float("-inf"),
                    "weather_descriptions": [],
                    "wind_speeds": [],
                }

            # Update temperature_min and temperature_max for the day
            daily_forecast[date_str]["temperature_min"] = min(
                daily_forecast[date_str]["temperature_min"], forecast["temperature"]
            )
            daily_forecast[date_str]["temperature_max"] = max(
                daily_forecast[date_str]["temperature_max"], forecast["temperature"]
            )

            # Append weather description and wind speed for later aggregation
            daily_forecast[date_str]["weather_descriptions"].append(forecast["weather"])
            daily_forecast[date_str]["wind_speeds"].append(forecast["wind_speed"])

        # Finalize daily forecast by aggregating wind speeds and finding the most common weather description
        for date_str, daily_data in daily_forecast.items():
            # Get the most common weather description for the day
            daily_data["weather"] = max(
                set(daily_data["weather_descriptions"]),
                key=daily_data["weather_descriptions"].count,
            )

            # Calculate average wind speed for the day
            daily_data["wind_speed"] = sum(daily_data["wind_speeds"]) / len(
                daily_data["wind_speeds"]
            )

            # Remove the temporary fields
            del daily_data["weather_descriptions"]
            del daily_data["wind_speeds"]

        return _self._to_forecast_list(daily_forecast)

    def get_forecast_between_dates(
        _self, city_name: str, state_name: str, start_date: str, end_date: str
    ):
        """
        Retrieves the weather forecast between specified start and end dates by aggregating hourly forecast data.

        Args:
            city_name (str): The name of the city.
            state_name (str): The name of the state.
            start_date (str): The start date in the format 'YYYY-MM-DD'.
            end_date (str): The end date in the format 'YYYY-MM-DD'.

        Returns:
            Dict[str, Dict[str, Union[int, str, float]]]: A dictionary containing the forecast data for each day
                between the specified dates.
        """
        # Fetch hourly forecast data
        hourly_forecast = _self.get_hourly_forecast(
            city_name, state_name, days=5
        )  # Fetching for the next 5 days

        # Dictionary to hold the aggregated daily data
        daily_forecast = {}

        # Convert start_date and end_date to datetime objects
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        end_date = datetime.strptime(end_date, "%Y-%m-%d")

        # Iterate over each forecast entry in hourly_forecast
        for forecast in hourly_forecast:

            # Convert the forecast object to a dictionary
            forecast = forecast.dict()

            # Extract the date part from the "date" field (YYYY-MM-DD)
            date_str = forecast["date"].split("T")[0]
            forecast_date = datetime.strptime(date_str, "%Y-%m-%d")

            # Check if the forecast date is within the specified range
            if start_date <= forecast_date <= end_date:
                if date_str not in daily_forecast:
                    daily_forecast[date_str] = {
                        "date": date_str,
                        "timestamp": forecast["timestamp"],
                        "city_name": city_name,
                        "state_name": state_name,
                        "temperature_min": float("inf"),
                        "temperature_max": float("-inf"),
                        "weather_descriptions": [],
                        "wind_speeds": [],
                    }

                # Update temperature_min and temperature_max for the day
                daily_forecast[date_str]["temperature_min"] = min(
                    daily_forecast[date_str]["temperature_min"], forecast["temperature"]
                )
                daily_forecast[date_str]["temperature_max"] = max(
                    daily_forecast[date_str]["temperature_max"], forecast["temperature"]
                )

                # Append weather description and wind speed for later aggregation
                daily_forecast[date_str]["weather_descriptions"].append(
                    forecast["weather"]
                )
                daily_forecast[date_str]["wind_speeds"].append(forecast["wind_speed"])

        # Finalize daily forecast by aggregating wind speeds and finding the most common weather description
        for date_str, daily_data in daily_forecast.items():
            # Get the most common weather description for the day
            daily_data["weather"] = max(
                set(daily_data["weather_descriptions"]),
                key=daily_data["weather_descriptions"].count,
            )

            # Calculate average wind speed for the day
            daily_data["wind_speed"] = sum(daily_data["wind_speeds"]) / len(
                daily_data["wind_speeds"]
            )

            # Remove the temporary fields
            del daily_data["weather_descriptions"]
            del daily_data["wind_speeds"]

        return _self._to_forecast_list(daily_forecast)

    def get_current_weather(_self, city_name: str, state_name: str):
        """
        Retrieves the current weather data for a specific city and state.

        Args:
            city_name (str): The name of the city.
            state_name (str): The name of the state.

        Returns:
            dict: The flattened weather data.

        """
        lat, long = _self.get_coordinates(city_name, state_name)
        data = _self._fetch_json(
            url=f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={long}&lang=pt_br&appid={_self.api_key}"
        )
        return _self._to_weather(data)

    # --------------------------
    # Model Conversion
    # --------------------------

    def _to_weather(self, resp_json: dict) -> WeatherModel:
        """
        Flattens the weather data from the OpenWeatherMap API response JSON.

        Args:
            resp_json (dict): The response JSON from the OpenWeatherMap API.

        Returns:
            WeatherModel: A WeatherModel object containing the flattened weather data.
        """
        weather = WeatherModel(
            city=resp_json.get("name"),
            country=resp_json.get("sys", {}).get("country"),
            coordinates=f"({resp_json.get('coord', {}).get('lat')}, {resp_json.get('coord', {}).get('lon')})",
            temperature_k=resp_json.get("main", {}).get("temp"),
            feels_like_k=resp_json.get("main", {}).get("feels_like"),
            min_temperature_k=resp_json.get("main", {}).get("temp_min"),
            max_temperature_k=resp_json.get("main", {}).get("temp_max"),
            pressure_hpa=resp_json.get("main", {}).get("pressure"),
            humidity_percent=resp_json.get("main", {}).get("humidity"),
            visibility_m=resp_json.get("visibility"),
            wind_speed_ms=resp_json.get("wind", {}).get("speed"),
            wind_direction_deg=resp_json.get("wind", {}).get("deg"),
            wind_gust_ms=resp_json.get("wind", {}).get("gust"),
            cloudiness_percent=resp_json.get("clouds", {}).get("all"),
            weather=resp_json.get("weather", [{}])[0].get("main"),
            weather_description=resp_json.get("weather", [{}])[0].get("description"),
            sunrise_utc=resp_json.get("sys", {}).get("sunrise"),
            sunset_utc=resp_json.get("sys", {}).get("sunset"),
            timezone_s=resp_json.get("timezone"),
            timestamp_dt=resp_json.get("dt"),
        )

        return weather

    def _to_forecast_list(self, data: dict) -> List[ForecastModel]:
        """
        Flattens the forecast data from the OpenWeatherMap API response.

        Args:
            data (dict): The parsed data retrieved from the OpenWeatherMap API.

        Returns:
            List[ForecastModel]: A list of ForecastModel objects containing the flattened forecast data.

        """
        forecast_list = []
        for timestamp, entry in data.items():
            forecast_list.append(
                ForecastModel(
                    timestamp=int(entry["timestamp"]),
                    date=entry["date"],
                    city_name=entry["city_name"],
                    state_name=entry["state_name"],
                    temperature=(
                        float(entry["temperature"]) if "temperature" in entry else None
                    ),
                    temperature_min=(
                        float(entry["temperature_min"])
                        if "temperature_min" in entry
                        else None
                    ),
                    temperature_max=(
                        float(entry["temperature_max"])
                        if "temperature_max" in entry
                        else None
                    ),
                    weather=entry["weather"],
                    wind_speed=entry["wind_speed"],
                )
            )
        return forecast_list

    # --------------------------
    # Utils
    # --------------------------

    @st.cache_data(ttl=86400)
    def _fetch_json(_self, url: str):
        """
        Fetches JSON data from the specified URL.

        Args:
            url (str): The URL to fetch the JSON data from.

        Returns:
            dict: The JSON data as a dictionary.

        """
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    def _format_date(self, timestamp: int):
        """
        Formats a timestamp into a string representation of date and time.

        Parameters:
            timestamp (int): The timestamp to be formatted.

        Returns:
            str: The formatted date and time string.
        """
        return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%dT%H:%M:%S")

    def _url_encode(self, text):
        """
        Encode a text string for use in a URL.

        Args:
        - text (str): The text to encode.

        Returns:
        - str: The URL-encoded text.
        """
        return requests.utils.quote(text)
