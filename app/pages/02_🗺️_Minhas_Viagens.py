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
if 'add_new_trip_form' not in st.session_state:
    st.session_state.add_new_trip_form = {
        'attractions': set()
    }


# --------------------------
# Form State Handlers
# --------------------------
def update_selected_attractions(attraction_name, remove=False):
    """
    Update the selected attractions and save it using session state.
    """
    selected_attractions = get_selected_attractions()
    if remove:
        if attraction_name in selected_attractions:
            selected_attractions.remove(attraction_name)
    else:
        selected_attractions.add(attraction_name)

    st.session_state.add_new_trip_form['attractions'] = selected_attractions


def get_selected_attractions():
    """
    Get the selected attractions from the session state.
    """
    return st.session_state.add_new_trip_form['attractions']


# --------------------------
# Add new trip form
# --------------------------
def Minhas_Viagens():
    # Set page title
    st.set_page_config(
        page_title="Minhas Viagens",
        page_icon="🗺️",
        layout='wide',
        initial_sidebar_state="expanded",
    )

    st.title('🗺️ Minhas Viagens')
    st.write(
        '''
        Aqui você pode cadastrar suas viagens e planejar seus roteiros de forma personalizada.
        '''
    )


Minhas_Viagens()
