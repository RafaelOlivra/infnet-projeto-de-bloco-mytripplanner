import pandas as pd
import streamlit as st

import streamlit.components.v1 as components

from services.GoogleMaps import GoogleMaps
from services.CityState import CityStateData
from services.Logger import _log

from lib.Utils import Utils

from views.WeatherView import WeatherView
from views.AttractionsView import AttractionsView
from views.ItineraryView import ItineraryView

from services.Trip import Trip

from tests.test_AiProvider import mock_itinerary


class TripView:
    def __init__(self, trip: str):
        # Check if got a trip object
        if isinstance(trip, Trip):
            self.trip_model = trip.model
        else:
            try:
                self.trip_model = Trip(trip_id=trip).model
            except ValueError as e:
                st.error("A viagem especificada não pôde ser carregada.")

        self.trip = Trip().from_model(self.trip_model)

    def render_trip(self):
        """
        Render the trip view.
        """
        if not self.trip_model:
            return

        # Show a message if trip is expired
        if self.trip.is_expired():
            st.warning("💡 Esta viagem expirou.")

        # Display trip title centered
        self.render_title()
        self.render_tags()
        self.render_summary()
        self.render_directions_iframe()
        self.render_origin_destination()

        st.write("#### 🌤️ Previsão do Tempo")
        if self.trip_model.weather:
            self.render_forecast()
        else:
            st.info("Não há dados disponíveis para esta viagem.")

        st.write("#### 🏕️ Objetivos")
        self.render_goals()

        if self.trip_model.attractions:
            st.write("##### Atrações para conhecer")
            self.render_attractions()

        st.write("#### 🤖 Roteiro")
        self.render_itinerary()

        if self.trip_model.notes:
            st.write("#### 📝 Notas")
            self.render_notes()

    def render_origin_destination(self):
        col1, col2 = st.columns(2)
        with col1.container(border=True):
            st.write(
                f"""##### 🏠 Origem: {self.trip_model.origin_city}, {
                    self.trip_model.origin_state}"""
            )
            st.write(
                f"""📆 Partida: {Utils.to_date_string(
                    self.trip_model.start_date, format='display')}"""
            )

        with col2.container(border=True):
            st.write(
                f"""##### 📍 Destino: {self.trip_model.destination_city}, {
                    self.trip_model.destination_state}"""
            )
            st.write(
                f"""📆 Retorno: {Utils.to_date_string(
                    self.trip_model.end_date, format='display')}"""
            )

    def render_title(self):
        """
        Render the trip title.
        """
        if not self.trip_model:
            return

        # Display trip title centered
        icon = Trip.get_travel_by_icon(self.trip_model.travel_by)
        st.write(f"## {icon} {self.trip_model.title}")

    def render_summary(self):
        """
        Render the trip summary.
        """
        if not self.trip_model:
            return

        if self.trip.has_summary():
            summary = self.trip.get("summary")
        else:
            with st.spinner("🤖 Gerando resumo..."):
                summary = self.trip.summarize()

        # Display trip summary
        if summary:
            with st.container(border=True):
                st.write(f"🤖 **Resumo**: {summary}")

    def render_tags(self):
        """
        Render the trip tags.
        """
        if not self.trip_model:
            return

        # Display tags
        tags = self.trip_model.tags
        if tags:
            tags = [f"`{tag}`" for tag in tags]
            tags = " ".join(tags)
            st.write(f"🏷️ {tags}")

    def render_directions_iframe(self):
        """
        Render the Google Maps directions iframe.
        """
        if not self.trip_model:
            return

        # Display Google Maps directions iframe
        google_maps = GoogleMaps()
        origin = f"""{self.trip_model.origin_city}, {
            CityStateData().uf_to_state(self.trip_model.origin_state)}"""
        destination = f"""{self.trip_model.destination_city}, {
            CityStateData().uf_to_state(self.trip_model.destination_state)}"""
        iframe_url = google_maps.get_google_maps_directions_iframe_url(
            origin, destination, mode=self.trip_model.travel_by
        )
        components.iframe(iframe_url, height=450)

        directions_url = google_maps.get_directions_url(
            origin=origin, destination=destination, mode=self.trip_model.travel_by
        )
        st.link_button(
            label="Como Chegar ↗️",
            url=directions_url,
            use_container_width=True,
            type="primary",
        )

    def render_goals(self):
        """
        Render the trip objectives.
        """
        if not self.trip_model:
            return

        # Display objectives
        if self.trip_model.goals:
            with st.container(border=True):
                st.text(f"{self.trip_model.goals}")

    def render_itinerary(self):
        """
        Render the trip itinerary.
        """
        if not self.trip_model:
            return
        ItineraryView(itinerary=self.trip_model.itinerary).render_itinerary()

    def render_forecast(self):
        trip_length = self.trip._calculate_trip_length(
            self.trip_model.start_date, self.trip_model.end_date
        )
        with st.container(border=True):
            WeatherView(
                city_name=self.trip_model.destination_city,
                state_name=self.trip_model.destination_state,
                weather_data=self.trip_model.weather,
                days=trip_length,
            ).render_forecast()

    def render_attractions(self):
        """
        Render the attractions data in a grid layout.
        """
        attractions = self.trip_model.attractions
        if attractions:
            AttractionsView(attractions=attractions).render_attractions()

    def render_notes(self):
        """
        Render the trip notes.
        """
        if not self.trip_model:
            return

        # Display notes
        if self.trip_model.notes:
            with st.container(border=True):
                st.text(f"{self.trip_model.notes}")

    def render_feedback(self):
        """
        Render the trip feedback.
        """
        if not self.trip_model:
            return

        # Display feedback
        feedback = self.trip.get_meta("feedback")
        if feedback:
            with st.container(border=True):
                st.text(f"{feedback}")
