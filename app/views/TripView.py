import pandas as pd
import streamlit as st

import streamlit.components.v1 as components

from services.GoogleMaps import GoogleMaps
from services.CityStateData import CityStateData
from services.Utils import Utils

from views.WeatherView import WeatherView
from views.AttractionsView import AttractionsView

from models.Trip import Trip


class TripView:
    trip = None

    def __init__(self, trip: str):

        # Check if got a trip object
        if isinstance(trip, Trip):
            self.trip = trip.model
        else:
            try:
                self.trip = Trip(id=trip).model
            except ValueError as e:
                st.error("A viagem especificada não pôde ser carregada.")

    def render_trip(self):
        """
        Render the trip view.
        """
        if not self.trip:
            return

        # Display trip title centered
        self.render_title()
        self.render_tags()
        self.render_directions_iframe()
        self.render_origin_destination()

        st.write("#### 🌤️ Previsão do Tempo")
        if self.trip.weather:
            self.render_forecast()
        else:
            st.info("Não há dados disponíveis para esta viagem.")

        st.write("#### 🏕️ Objetivos")
        self.render_goals()

        if self.trip.attractions:
            st.write("##### Atrações para conhecer")
            self.render_attractions()

        st.write("#### 🤖 Roteiro")
        self.render_schedule()

        if self.trip.notes:
            st.write("#### 📝 Notas")
            self.render_notes()

    def render_origin_destination(self):
        col1, col2 = st.columns(2)
        with col1.container(border=True):
            st.write(
                f"##### 🏠 Origem: {self.trip.origin_city}, {self.trip.origin_state}"
            )
            st.write(
                f"📆 Partida: {Utils.format_date_str(self.trip.start_date, format="display")}"
            )

        with col2.container(border=True):
            st.write(
                f"##### 📍 Destino: {self.trip.destination_city}, {self.trip.destination_state}"
            )
            st.write(
                f"📆 Retorno: {Utils.format_date_str(self.trip.end_date, format="display")}"
            )

    def render_title(self):
        """
        Render the trip title.
        """
        if not self.trip:
            return

        # Display trip title centered
        icon = Trip.get_travel_by_icon(self.trip.travel_by)
        st.write(f"## {icon} {self.trip.title}")

    def render_tags(self):
        """
        Render the trip tags.
        """
        if not self.trip:
            return

        # Display tags
        tags = self.trip.tags
        if tags:
            tags = [f"`{tag}`" for tag in tags]
            tags = " ".join(tags)
            st.write(f"🏷️ {tags}")

    def render_directions_iframe(self):
        """
        Render the Google Maps directions iframe.
        """
        if not self.trip:
            return

        # Display Google Maps directions iframe
        google_maps = GoogleMaps()
        origin = f"{self.trip.origin_city}, {CityStateData().uf_to_state(self.trip.origin_state)}"
        destination = f"{self.trip.destination_city}, {CityStateData().uf_to_state(self.trip.destination_state)}"
        iframe_url = google_maps.get_google_maps_directions_iframe_url(
            origin, destination, mode=self.trip.travel_by
        )
        components.iframe(iframe_url, height=450)

    def render_goals(self):
        """
        Render the trip objectives.
        """
        if not self.trip:
            return

        # Display objectives
        if self.trip.goals:
            with st.container(border=True):
                st.text(f"{self.trip.goals}")

    def render_schedule(self):
        """
        Render the trip schedule.
        """
        if not self.trip:
            return

        # Display schedule
        # if self.trip.schedule:
        #     with st.container(border=True):
        #         st.write(self.trip.schedule)
        with st.container(border=True):
            st.write("Em breve...")

    def render_forecast(self):
        trip_length = Trip._calculate_trip_length(
            self.trip.start_date, self.trip.end_date
        )
        with st.container(border=True):
            WeatherView(
                city_name=self.trip.destination_city,
                state_name=self.trip.destination_state,
                weather_data=self.trip.weather,
                days=trip_length,
            ).render_forecast()

    def render_attractions(self):
        """
        Render the attractions data in a grid layout.
        """
        attractions = self.trip.attractions
        if attractions:
            AttractionsView(attractions=attractions).render_attractions()

    def render_notes(self):
        """
        Render the trip notes.
        """
        if not self.trip:
            return

        # Display notes
        if self.trip.notes:
            with st.container(border=True):
                st.write(self.trip.notes)
