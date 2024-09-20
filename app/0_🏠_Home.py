import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv, find_dotenv
import pandas as pd
from services.OpenWeatherMap import OpenWeatherMap
from services.GoogleMaps import GoogleMaps
from services.YelpScrapper import YelpScrapper

# --------------------------
# Configurations
# ---------------------------

# Load environment variables
load_dotenv(find_dotenv('../.env'))


# --------------------------
# Pages
# ---------------------------

# Home Page
def Home():

    # Set page title
    st.set_page_config(
        page_title="MyTripPlanner",
        page_icon="🗺️",
        layout='wide',
        initial_sidebar_state="expanded",
    )

    st.title('🗺️ MyTripPlanner')
    st.write(
        '''
        O MyTripPlanner é um aplicativo de planejamento de viagens, projetado para ajudar os usuários a organizarem suas jornadas de forma eficiente e personalizada. O app oferece previsões meteorológicas detalhadas e sugestões de roteiros para o destino escolhido, utilizando dados precisos de diversas APIs e integração com Inteligência Artificial. Com o MyTripPlanner, os viajantes podem desfrutar de uma experiência tranquila e agradável, sem surpresas indesejadas pelo caminho.
        '''
    )


####################
# INIT
####################
if __name__ == '__main__':
    Home()
