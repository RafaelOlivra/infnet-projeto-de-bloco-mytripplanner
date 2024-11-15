import pandas as pd
import streamlit as st

from datetime import datetime, date, timedelta

from services.OpenWeatherMap import OpenWeatherMap
from services.GeminiProvider import GeminiProvider
from lib.Utils import Utils

from models.Itinerary import DailyItineraryModel, ActivityModel
from models.Weather import ForecastModel
from models.Attraction import AttractionModel

from typing import List


class ItineraryView:
    def __init__(
        self,
        itinerary: List[DailyItineraryModel] = None,
    ):
        self.itinerary = itinerary

    def render_itinerary(self):

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

    def render_daily_itinerary(self, day: DailyItineraryModel):
        with st.container(border=True):
            if day.items.__len__() > 0:
                st.write(
                    f"#### 📅 {Utils.to_date_string(day.date, format='display')} - {day.title}"
                )
                for activity in day.items:
                    self.render_activity(activity)

    def render_activity(self, activity: ActivityModel):
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

        ai_provider = GeminiProvider()
        ai_provider.prepare(
            location=location,
            start_date=start_date,
            end_date=end_date,
            forecast_list=forecast_list,
            attractions_list=attractions_list,
        )

        with st.spinner("Gerando roteiro..."):
            response = ai_provider._generate_itinerary()

            if not response:
                st.error("Não foi possível gerar o roteiro com IA.")
                return

            # Convert to DailyItineraryModel
            return ai_provider._to_itinerary(response)
