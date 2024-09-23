import streamlit as st
import streamlit.components.v1 as components
import streamlit_tags as st_tags
import datetime
from model.Trip import Trip
from services.CityStateData import CityStateData
from services.GoogleMaps import GoogleMaps
from views.WeatherView import WeatherView
from views.AttractionsView import AttractionsView
from services.TripData import TripData

# --------------------------
# Session State
# --------------------------
if 'selected_trip_id' not in st.session_state:
    st.session_state.selected_trip_id = None


# --------------------------
# View Trip Data
# --------------------------
def View_Trip():
    # Set page title
    st.set_page_config(
        page_title="Minhas Viagens",
        page_icon="🗺️",
        layout='wide',
        initial_sidebar_state="expanded",
    )

    st.title("🗺️ Minhas Viagens")
    st.write("Aqui estão as viagens que você planejou:")

    available_trips = TripData().get_available_trips()
    selected_trip_id = st.session_state.selected_trip_id

    if not available_trips and not selected_trip_id:
        st.write("Você ainda não planejou nenhuma viagem.")
        return

    if not selected_trip_id:
        selected_trip_id = available_trips[0].get("id")
        st.session_state.selected_trip_id = selected_trip_id

    # Display a select box for the available trips, if the selected trip is not in the available trips
    # the first trip in the list will be selected by default
    selected_trip_id = st.selectbox("Selecione a viagem:", [trip.get("title") for trip in available_trips], index=available_trips.index(
        next((trip for trip in available_trips if trip["title"] == selected_trip_id), available_trips[0])))
    selected_trip_id = next(
        (trip for trip in available_trips if trip["title"] == selected_trip_id), available_trips[0]).get("id")

    trip = TripData().get_trip(selected_trip_id)

    st.write(trip)


View_Trip()
