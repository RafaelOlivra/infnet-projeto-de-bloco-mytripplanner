import streamlit as st
import streamlit.components.v1 as components
import streamlit_tags as st_tags
import datetime
from model.Trip import Trip
from services.CityStateData import CityStateData
from services.GoogleMaps import GoogleMaps
from views.WeatherView import WeatherView
from views.AttractionsView import AttractionsView


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

    # Get the trips
    trip_id = st.session_state.selected_trip_id
    if trip_id:
        trip = Trip(trip_id=trip_id)
        trip_json = trip._to_json()
        st.write(trip_json)


View_Trip()
