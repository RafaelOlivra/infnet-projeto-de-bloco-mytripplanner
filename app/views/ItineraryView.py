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
        st.write("## 🗺️ Roteiro")
        with st.container(border=True):
            for day in self.itinerary:
                self.render_day(day)

    def render_daily_itinerary(self, day: DailyItineraryModel):
        st.write(f"### 📅 {Utils.to_date_string(day.date)} - {day.title}")
        with st.container(border=True):
            for activity in day.items:
                self.render_activity(activity)

    def render_activity(self, activity: ActivityModel):
        st.write(
            f"#### 🕒 {activity.start_time} - {activity.end_time} - {activity.title}"
        )
        st.write(f"📍 {activity.location}")
        if activity.description:
            st.write(f"ℹ️ {activity.description}")
