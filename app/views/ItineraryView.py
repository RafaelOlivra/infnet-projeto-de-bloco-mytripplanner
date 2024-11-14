import pandas as pd
import streamlit as st

from datetime import datetime

from services.OpenWeatherMap import OpenWeatherMap
from lib.Utils import Utils

from models.Itinerary import DailyItineraryModel, ActivityModel
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

    def render_daily_itinerary(self, day: DailyItineraryModel):
        with st.container(border=True):
            st.write(
                f"### 📅 {Utils.to_date_string(day.date, format='display')} - {day.title}"
            )
            for activity in day.items:
                self.render_activity(activity)

    def render_activity(self, activity: ActivityModel):
        with st.container(border=True):
            st.write(
                f"""
                ##### 🕒 {Utils.to_time_string(activity.start_time)} | {activity.title}
                📍 **{activity.location}**  \
                    
                ✨ {activity.description}
                """
            )
