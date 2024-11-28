import pandas as pd
import streamlit as st

from datetime import datetime, date, timedelta

from services.OpenWeatherMap import OpenWeatherMap
from services.GeminiProvider import GeminiProvider
from services.OpenAIProvider import OpenAIProvider
from lib.Utils import Utils

from models.Itinerary import DailyItineraryModel, ActivityModel
from models.Weather import ForecastModel
from models.Attraction import AttractionModel

from typing import List


class ItineraryView:
    """
    A class that handles the itinerary view and generation in Streamlit.
    """

    def __init__(
        self,
        itinerary: List[DailyItineraryModel] = None,
    ):
        """
        Initialize the ItineraryView class.

        Args:
            itinerary (List[DailyItineraryModel], optional): The itinerary data to render. Defaults to None.
        """
        self.itinerary = itinerary

    def render_itinerary(self):
        """
        Render the streamlit itinerary view using the provided itinerary data.
        """

        if not self.itinerary:
            st.info("Não há nenhum roteiro programado para essa viagem.")
            return

        cols = st.columns(2)
        i = 0
        for day in self.itinerary:
            # Alternate between columns
            col = cols[0] if i % 2 == 0 else cols[1]
            with col:
                self.render_daily_itinerary(day)
            i += 1
            # Create a new column for every 2 days
            if col == cols[1]:
                cols = st.columns(2)

    def render_daily_itinerary(self, daily_itinerary: DailyItineraryModel):
        """
        Render the daily itinerary view for a given day.

        Args:
            daily_itinerary (DailyItineraryModel): The daily itinerary data.
        """
        with st.container(border=True):
            if daily_itinerary.items.__len__() > 0:
                st.write(
                    f"#### 📅 {Utils.to_date_string(daily_itinerary.date, format='display')} - {daily_itinerary.title}"
                )
                for activity in daily_itinerary.items:
                    self.render_activity(activity)

    def render_activity(self, activity: ActivityModel):
        """
        Render the activity view for a given activity.

        Args:
            activity (ActivityModel): The activity data.
        """
        with st.container(border=True):
            st.write(
                f"""
                ##### 🕒 {Utils.to_time_string(activity.start_time)} - {Utils.to_time_string(activity.end_time)} | {activity.title}
                📍 **{activity.location}**  \
                    
                ✨ {activity.description}
                """
            )

    def render_itinerary_generator(
        location: str = None,
        start_date: date = None,
        end_date: date = None,
        forecast_list: List[ForecastModel] = None,
        attractions_list: List[AttractionModel] = None,
    ) -> List[DailyItineraryModel]:
        """
        Render the itinerary generator view.

        Args:
            location (str): The destination location (city, state).
            start_date (date): The start date of the trip.
            end_date (date): The end date of the trip.
            forecast_list (List[ForecastModel]): The weather forecast data.
            attractions_list (List[AttractionModel]): The attractions data.

        Returns:
            List[DailyItineraryModel]: The generated itinerary data.
        """

        ai_provider = OpenAIProvider()
        ai_provider.prepare(
            location=location,
            start_date=start_date,
            end_date=end_date,
            forecast_list=forecast_list,
            attractions_list=attractions_list,
        )

        with st.spinner("Gerando roteiro..."):
            generated_itinerary = ai_provider.generate_itinerary()

            if not generated_itinerary:
                st.error("Não foi possível gerar o roteiro com IA.")
                return

            # Convert to DailyItineraryModel
            return generated_itinerary
