import pandas as pd
from datetime import datetime
from services.OpenWeatherMap import OpenWeatherMap
import streamlit as st


class WeatherView:
    city_name = ""
    state_name = ""
    days = 5
    forecast = {}

    def __init__(self, city_name, state_name, days=5):
        """
        Initialize the WeatherView class with a trip
        """
        self.city_name = city_name
        self.state_name = state_name
        self.days = days
        self.forecast = self.get_forecast()

    def get_forecast(self):
        """
        Get the weather data for the specified city and state.
        """
        return OpenWeatherMap().get_forecast(self.city_name, self.state_name, self.days)

    def view(self):
        """
        Display the weather forecast for the specified city and state.
        """
        print(f"Tempo para {self.city_name}, {self.state_name}")

        df = pd.DataFrame(self.forecast)
        st.dataframe(df)
