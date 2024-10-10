import pandas as pd
from datetime import datetime
from services.OpenWeatherMap import OpenWeatherMap
import streamlit as st


class WeatherView:
    city_name = ""
    state_name = ""
    days = 5
    forecast = {}
    weather_data = {}

    def __init__(self, city_name="", state_name="", days=5, weather_data=None):
        """
        Initialize the WeatherView class.

        Args:
            city_name (str): The name of the city.
            state_name (str): The name of the state.
            days (int): The number of days to forecast.
            weather_data (dict): The weather data for the specified city and state.
        """
        self.city_name = city_name
        self.state_name = state_name
        self.days = days
        self.forecast = weather_data if weather_data else self._get_forecast()

    def _get_forecast(self):
        """
        Get the weather data for the specified city and state.
        """
        return OpenWeatherMap().get_forecast_for_next_5_days(
            self.city_name, self.state_name
        )

    # Function to map weather description to icon (you can customize this as needed)
    def _get_weather_icon(self, weather_desc):
        """
        Maps the Portuguese weather descriptions from OpenWeatherMap to weather icons (emojis).

        Args:
            weather_desc (str): The weather description in Portuguese.

        Returns:
            str: The corresponding weather icon (emoji).
        """
        weather_icons = {
            "céu limpo": "☀️",
            "algumas nuvens": "🌤️",
            "nuvens dispersas": "🌥️",
            "nublado": "☁️",
            "nuvens quebradas": "🌥️",
            "chuva leve": "🌧️",
            "chuva moderada": "🌧️",
            "chuva forte": "⛈️",
            "chuva muito forte": "⛈️",
            "chuva extrema": "⛈️",
            "chuvisco": "🌦️",
            "chuvisco leve": "🌦️",
            "chuvisco intenso": "🌧️",
            "trovoada": "🌩️",
            "trovoada com chuva": "⛈️",
            "trovoada com chuva leve": "⛈️",
            "trovoada com chuva forte": "⛈️",
            "trovoada com chuvisco": "⛈️",
            "neve": "❄️",
            "neve leve": "🌨️",
            "neve moderada": "❄️",
            "neve forte": "❄️",
            "granizo": "🌨️",
            "nevoeiro": "🌫️",
            "neblina": "🌫️",
            "poeira": "🌬️",
            "areia": "🌬️",
            "tempestade de areia": "🌪️",
            "fumaça": "🌫️",
            "neve gélida": "❄️",
            "vento forte": "💨",
            "vendaval": "🌪️",
            "calor extremo": "🔥",
            "frio extremo": "❄️",
            "tornado": "🌪️",
            "furacão": "🌀",
            "chuva de granizo": "🌨️",
            # Default for unknown descriptions
            "desconhecido": "🌡️",
        }
        # Default to thermometer emoji
        return weather_icons.get(weather_desc, "🌡️")

    def display_forecast(self):
        """
        Display the weather forecast for the specified city and state.
        """

        # Check if the forecast data is available
        # Currently, the forecast data is only available for the next 5 days
        if not self.forecast:
            st.info("Ainda não temos previsão do tempo para a data selecionada.")
            return

        # Display temperatures in 5 columns
        cols = st.columns(5)
        i = 0
        for forecast in self.forecast:

            # Convert each Forecast object to dictionary
            forecast = forecast.__dict__

            if i < 5:  # Only show the first 5 days
                with cols[i]:
                    # Display the weather icon
                    weather_icon = self._get_weather_icon(forecast["weather"])
                    st.write(f"#### {weather_icon}")

                    # Format the date to DD-MM-YYYY
                    forecast_timestamp = forecast["timestamp"]
                    forecast_date = datetime.fromtimestamp(forecast_timestamp).strftime(
                        "%d-%m-%Y"
                    )

                    # Display the weather and temperature using st.metric
                    st.metric(
                        label=f"{forecast_date}",
                        value=f"{int(forecast['temperature_max'])}°C",
                        delta=f"Min: {int(forecast['temperature_min'])}°C",
                    )
                    i += 1
