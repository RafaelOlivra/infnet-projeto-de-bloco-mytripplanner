import requests
from datetime import datetime, timedelta
from services.AppData import AppData
import streamlit as st
from services.LatLong import LatLong


class OpenWeatherMap:
    def __init__(self, api_key=None):
        # Set the API key, either from the environment or directly from the parameter
        self.api_key = api_key or AppData().get_api_key("openweathermap")
        if not self.api_key:
            raise ValueError("API key is required for OpenWeatherMap")

    @st.cache_data(ttl=86400)
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
            url=f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={long}&lang=pt_br&appid={_self.api_key}")
        return _self._flatten_weather_data(data)

    @st.cache_data(ttl=86400)
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

    @st.cache_data(ttl=86400)
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
            url=f"http://api.openweathermap.org/geo/1.0/direct?q={_self._url_encode(city_name)},{_self._url_encode(state_name)},Brazil&lang=pt_br&appid={_self.api_key}")
        return data[0]['lat'], data[0]['lon']

    @st.cache_data(ttl=86400)
    def get_hourly_forecast(_self, city_name: str, state_name: str, days: int = 5):
        """
        Retrieves the weather forecast for a given city and state.

        Args:
            city_name (str): The name of the city.
            state_name (str): The name of the state.
            days (int, optional): The number of days to retrieve the forecast for. Defaults to 5.

        Returns:
            Dict[str, List[Dict[str, Union[int, str, float]]]]: A dictionary containing the forecast data for each day.
                The keys are the date in the format 'YYYY-MM-DD' and the values are lists of dictionaries, where each
                dictionary represents a forecast for a specific time. The dictionaries have the following keys:
                - 'timestamp' (int): The timestamp of the forecast.
                - 'date' (str): The date of the forecast in the format 'YYYY-MM-DD'.
                - 'city_name' (str): Name of the requested city
                - 'state_name' (str): Name of the requested state
                - 'temperature' (float): The temperature in Celsius.
                - 'weather' (str): The description of the weather.
                - 'wind_speed' (float): The wind speed in meters per second.
        """
        lat, long = _self.get_coordinates(city_name, state_name)
        data = _self._fetch_json(
            url=f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={long}&units=metric&lang=pt_br&appid={_self.api_key}")

        forecast_list = data['list']
        hourly_forecast = {}
        current_date = datetime.now().date()

        for forecast in forecast_list:
            forecast_timestamp = int(forecast['dt'])
            forecast_datetime = datetime.fromtimestamp(forecast_timestamp)
            forecast_date = forecast_datetime.date()
            forecast_date_str = _self._format_date(
                forecast_timestamp)  # International datetime

            # Check if we are still within the selected days
            if forecast_date > current_date + timedelta(days=int(days)):
                break

            # Check if the forecast is for the current day
            if forecast_date_str not in hourly_forecast:
                hourly_forecast[forecast_date_str] = []

            hourly_forecast[forecast_date_str] = {
                'timestamp': forecast_timestamp,
                'date': forecast_date_str,
                'city_name': city_name,
                'state_name': state_name,
                'temperature': forecast['main']['temp'],
                'weather': forecast['weather'][0]['description'],
                'wind_speed': forecast['wind']['speed']
            }

        return _self._flatten_forecast_data(hourly_forecast)

    @st.cache_data(ttl=86400)
    def get_forecast_for_next_5_days(_self, city_name: str, state_name: str, days: int = 5):
        """
        Retrieves the daily weather forecast for the next 'days' days by aggregating hourly forecast data.

        Args:
            city_name (str): The name of the city.
            state_name (str): The name of the state.
            days (int, optional): The number of days to retrieve the forecast for. Defaults to 5.

        Returns:
            Dict[str, Dict[str, Union[int, str, float]]]: A dictionary containing the forecast data for each day.
                The keys are the date in the format 'YYYY-MM-DD', and the values are dictionaries representing the day.
                The dictionary has the following keys:
                - 'date' (str): The date of the forecast in the format 'YYYY-MM-DD'.
                - 'city_name' (str): Name of the requested city.
                - 'state_name' (str): Name of the requested state.
                - 'temperature_min' (float): The minimum temperature in Celsius.
                - 'temperature_max' (float): The maximum temperature in Celsius.
                - 'weather' (str): The most common weather description.
                - 'wind_speed' (float): The average wind speed in meters per second.
        """
        # Reuse the hourly forecast function to get all the hourly data
        hourly_forecast = _self.get_hourly_forecast(
            city_name, state_name, days)

        # Dictionary to hold the aggregated daily data
        daily_forecast = {}

        # Iterate over each forecast entry in hourly_forecast
        for forecast in hourly_forecast:
            # Extract the date part from the "date" field (YYYY-MM-DD)
            date_str = forecast['date'].split('T')[0]

            # Initialize daily forecast data if this is the first entry for this day
            if date_str not in daily_forecast:

                daily_forecast[date_str] = {
                    'date': date_str,
                    'timestamp': forecast['timestamp'],
                    'city_name': city_name,
                    'state_name': state_name,
                    'temperature_min': float('inf'),
                    'temperature_max': float('-inf'),
                    'weather_descriptions': [],
                    'wind_speeds': []
                }

            # Update temperature_min and temperature_max for the day
            daily_forecast[date_str]['temperature_min'] = min(
                daily_forecast[date_str]['temperature_min'], forecast['temperature'])
            daily_forecast[date_str]['temperature_max'] = max(
                daily_forecast[date_str]['temperature_max'], forecast['temperature'])

            # Append weather description and wind speed for later aggregation
            daily_forecast[date_str]['weather_descriptions'].append(
                forecast['weather'])
            daily_forecast[date_str]['wind_speeds'].append(
                forecast['wind_speed'])

        # Finalize daily forecast by aggregating wind speeds and finding the most common weather description
        for date_str, daily_data in daily_forecast.items():
            # Get the most common weather description for the day
            daily_data['weather'] = max(set(
                daily_data['weather_descriptions']), key=daily_data['weather_descriptions'].count)

            # Calculate average wind speed for the day
            daily_data['wind_speed'] = sum(
                daily_data['wind_speeds']) / len(daily_data['wind_speeds'])

            # Remove the temporary fields
            del daily_data['weather_descriptions']
            del daily_data['wind_speeds']

        return _self._flatten_forecast_data(daily_forecast)

    @st.cache_data(ttl=86400)
    def get_forecast_between_dates(_self, city_name: str, state_name: str, start_date: str, end_date: str):
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
            city_name, state_name, days=5)  # Fetching for the next 5 days

        # Dictionary to hold the aggregated daily data
        daily_forecast = {}

        # Convert start_date and end_date to datetime objects
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')

        # Iterate over each forecast entry in hourly_forecast
        for forecast in hourly_forecast:
            # Extract the date part from the "date" field (YYYY-MM-DD)
            date_str = forecast['date'].split('T')[0]
            forecast_date = datetime.strptime(date_str, '%Y-%m-%d')

            # Check if the forecast date is within the specified range
            if start_date <= forecast_date <= end_date:
                if date_str not in daily_forecast:
                    daily_forecast[date_str] = {
                        'date': date_str,
                        'timestamp': forecast['timestamp'],
                        'city_name': city_name,
                        'state_name': state_name,
                        'temperature_min': float('inf'),
                        'temperature_max': float('-inf'),
                        'weather_descriptions': [],
                        'wind_speeds': []
                    }

                # Update temperature_min and temperature_max for the day
                daily_forecast[date_str]['temperature_min'] = min(
                    daily_forecast[date_str]['temperature_min'], forecast['temperature'])
                daily_forecast[date_str]['temperature_max'] = max(
                    daily_forecast[date_str]['temperature_max'], forecast['temperature'])

                # Append weather description and wind speed for later aggregation
                daily_forecast[date_str]['weather_descriptions'].append(
                    forecast['weather'])
                daily_forecast[date_str]['wind_speeds'].append(
                    forecast['wind_speed'])

        # Finalize daily forecast by aggregating wind speeds and finding the most common weather description
        for date_str, daily_data in daily_forecast.items():
            # Get the most common weather description for the day
            daily_data['weather'] = max(set(
                daily_data['weather_descriptions']), key=daily_data['weather_descriptions'].count)

            # Calculate average wind speed for the day
            daily_data['wind_speed'] = sum(
                daily_data['wind_speeds']) / len(daily_data['wind_speeds'])

            # Remove the temporary fields
            del daily_data['weather_descriptions']
            del daily_data['wind_speeds']

        return _self._flatten_forecast_data(daily_forecast)

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

    def _flatten_weather_data(self, resp_json: dict):
        """
        Flattens the weather data from the OpenWeatherMap API response JSON.

        Args:
            resp_json (dict): The response JSON from the OpenWeatherMap API.

        Returns:
            dict: A dictionary containing the flattened weather data with the following keys:
                - "City": The name of the city.
                - "Country": The country code.
                - "Coordinates": The latitude and longitude of the location.
                - "Temperature (K)": The temperature in Kelvin.
                - "Feels Like (K)": The feels like temperature in Kelvin.
                - "Min Temperature (K)": The minimum temperature in Kelvin.
                - "Max Temperature (K)": The maximum temperature in Kelvin.
                - "Pressure (hPa)": The atmospheric pressure in hPa.
                - "Humidity (%)": The humidity percentage.
                - "Visibility (m)": The visibility in meters.
                - "Wind Speed (m/s)": The wind speed in meters per second.
                - "Wind Direction (°)": The wind direction in degrees.
                - "Wind Gust (m/s)": The wind gust speed in meters per second.
                - "Cloudiness (%)": The cloudiness percentage.
                - "Weather": The main weather condition.
                - "Weather Description": The description of the weather condition.
                - "Sunrise (UTC)": The UTC time of sunrise.
                - "Sunset (UTC)": The UTC time of sunset.
                - "Timezone (s)": The timezone offset in seconds.
                - "Timestamp (dt)": The timestamp of the weather data.

        """
        flattened_data = {
            "City": resp_json.get("name"),
            "Country": resp_json.get("sys", {}).get("country"),
            "Coordinates": f"({resp_json.get('coord', {}).get('lat')}, {resp_json.get('coord', {}).get('lon')})",
            "Temperature (K)": resp_json.get("main", {}).get("temp"),
            "Feels Like (K)": resp_json.get("main", {}).get("feels_like"),
            "Min Temperature (K)": resp_json.get("main", {}).get("temp_min"),
            "Max Temperature (K)": resp_json.get("main", {}).get("temp_max"),
            "Pressure (hPa)": resp_json.get("main", {}).get("pressure"),
            "Humidity (%)": resp_json.get("main", {}).get("humidity"),
            "Visibility (m)": resp_json.get("visibility"),
            "Wind Speed (m/s)": resp_json.get("wind", {}).get("speed"),
            "Wind Direction (°)": resp_json.get("wind", {}).get("deg"),
            "Wind Gust (m/s)": resp_json.get("wind", {}).get("gust"),
            "Cloudiness (%)": resp_json.get("clouds", {}).get("all"),
            "Weather": resp_json.get("weather", [{}])[0].get("main"),
            "Weather Description": resp_json.get("weather", [{}])[0].get("description"),
            "Sunrise (UTC)": resp_json.get("sys", {}).get("sunrise"),
            "Sunset (UTC)": resp_json.get("sys", {}).get("sunset"),
            "Timezone (s)": resp_json.get("timezone"),
            "Timestamp (dt)": resp_json.get("dt")
        }
        return flattened_data

    def _flatten_forecast_data(self, data: dict):
        """
        Flattens the forecast data from the OpenWeatherMap API response.

        Args:
            data (dict): The parsed data retrieved from the OpenWeatherMap API.

        Returns:
            list: A list of dictionaries containing flattened forecast data.

        """
        flattened_data = []
        for timestamp, entry in data.items():
            flattened_data.append({
                "timestamp": entry["timestamp"],
                "date": entry["date"],
                "city_name": entry["city_name"],
                "state_name": entry["state_name"],
                "temperature": entry["temperature"] if "temperature" in entry else None,
                "temperature_min": entry["temperature_min"] if "temperature_min" in entry else None,
                "temperature_max": entry["temperature_max"] if "temperature_max" in entry else None,
                "weather": entry["weather"],
                "wind_speed": entry["wind_speed"]
            })

        return flattened_data

    def _format_date(self, timestamp: int):
        """
        Formats a timestamp into a string representation of date and time.

        Parameters:
            timestamp (int): The timestamp to be formatted.

        Returns:
            str: The formatted date and time string.
        """
        return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%dT%H:%M:%S')

    def _url_encode(self, text):
        """
        Encode a text string for use in a URL.

        Args:
        - text (str): The text to encode.

        Returns:
        - str: The URL-encoded text.
        """
        return requests.utils.quote(text)
