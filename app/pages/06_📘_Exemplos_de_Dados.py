from io import StringIO
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd

from services.OpenWeatherMap import OpenWeatherMap
from services.GoogleMaps import GoogleMaps
from app.services.YelpAttractionsScrapper import YelpAttractionsScrapper

from models.Attraction import AttractionModel

st.set_page_config(
    page_title="Exemplo: OpenWeatherMap",
    page_icon="#️⃣",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# OpenWeatherMap Example
def openweathermap_example():
    """
    OpenWatherMap Example
    """
    st.write(
        """
        ### 🌎 OpenWeatherMap
        - [Documentação](https://openweathermap.org/api)
        """
    )

    # Create OpenWeatherMap instance
    owm = OpenWeatherMap()

    # Get Weather data
    data = owm.get_forecast_for_next_5_days(
        city_name="Sorocaba", state_name="São Paulo"
    )
    st.write("### Dados do Tempo (Próximos 5 dias) (Sorocaba-SP)")

    # Convert each Forecast object to JSON
    data = [forecast.__dict__ for forecast in data]

    # Create DataFrame
    df = pd.DataFrame(data)

    df.drop(columns=["temperature"], inplace=True)

    # Correct formats for display
    df["timestamp"] = df["timestamp"].astype(str)
    df["date"] = pd.to_datetime(df["date"])

    # Show with Pandas
    st.dataframe(df, use_container_width=True)

    st.write("### Dados do Tempo Detalhado (Atual) (Sorocaba-SP)")
    data = owm.get_current_weather(city_name="Sorocaba", state_name="São Paulo")
    data = data.__dict__
    df = pd.DataFrame([data])

    # Correct formats for display
    df["timestamp_dt"] = df["timestamp_dt"].astype(str)

    st.dataframe(df, use_container_width=True)


# Google Maps Example
def googlemaps_example():
    """
    Google Maps Example
    """
    st.write(
        """
        ### 🚗 Google Maps
        - [Documentação](https://cloud.google.com/maps-platform)
        """
    )

    # Create GoogleMaps instance
    gm = GoogleMaps()

    # Get Directions URL
    st.write("### URL de Direções: (Sorocaba-SP → São Paulo-SP)")
    directions_url = gm.get_directions_url(
        origin="Sorocaba, SP", destination="São Paulo, SP", location_mode=""
    )

    # Show a button with directions url
    st.link_button(
        label="Clique para abrir as direções no Google Maps", url=directions_url
    )

    # Get Directions Iframe
    st.write("### Iframe de Direções: (Sorocaba-SP → São Paulo-SP)")
    iframe_url = gm.get_google_maps_directions_iframe_url(
        origin="Centro, Sorocaba, SP", destination="Centro, São Paulo, SP"
    )
    components.iframe(iframe_url, height=450)


# Yelp Example


def yelp_example():
    """
    Yelp Example
    """
    st.write(
        """
        ### ⭐ Yelp (Via scraper)
        - [Página de Busca](https://yelp.com/search?find_desc=Attractions&find_loc=Sorocaba,%20Sao+Paulo,%20Brasil&start=0&limit=10)
        """
    )

    # Create YelpScrapper instance
    yelp = YelpAttractionsScrapper()

    # Get Attractions JSON
    st.write("### Atrações Perto de Sorocaba-SP")
    attractions = yelp.get_near_attractions(
        city_name="Sorocaba", state_name="São Paulo"
    )

    # Convert the Attraction objects to JSON
    attractions = [attraction.__dict__ for attraction in attractions]
    attractions = pd.json_normalize(attractions)

    # Show JSON data with Pandas
    st.write(attractions)


openweathermap_example()
st.divider()
googlemaps_example()
st.divider()
yelp_example()
