from io import StringIO
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from services.OpenWeatherMap import OpenWeatherMap
from services.GoogleMaps import GoogleMaps
from services.YelpScrapper import YelpScrapper

st.set_page_config(
    page_title="Exemplo: OpenWeatherMap",
    page_icon="#️⃣",
    layout='wide',
    initial_sidebar_state="collapsed",
)


# OpenWeatherMap Example
def openweathermap_example():
    '''
    OpenWatherMap Example
    '''
    st.write(
        '''
        ### 🌎 OpenWeatherMap
        - [Documentação](https://openweathermap.org/api)
        '''
    )

    # Create OpenWeatherMap instance
    owm = OpenWeatherMap()

    # Get Weather data
    data = owm.get_forecast_for_next_5_days(city_name="Sorocaba",
                                            state_name="São Paulo")
    st.write('### Dados do Tempo (Próximos 5 dias) (Sorocaba-SP)')

    # Create DataFrame
    df = pd.DataFrame(data)
    df.drop(columns=['temperature'], inplace=True)

    # Correct formats for display
    df['timestamp'] = df['timestamp'].astype(str)
    df['date'] = pd.to_datetime(df['date'])

    # Show with Pandas
    st.write(df)


# Google Maps Example
def googlemaps_example():
    '''
    Google Maps Example
    '''
    st.write(
        '''
        ### 🚗 Google Maps
        - [Documentação](https://cloud.google.com/maps-platform)
        '''
    )

    # Create GoogleMaps instance
    gm = GoogleMaps()

    # Get Directions URL
    st.write('### URL de Direções: (Sorocaba-SP → São Paulo-SP)')
    directions_url = gm.get_directions_url(
        origin="Sorocaba-SP", destination="São Paulo-SP")

    # Show a button with directions url
    st.link_button(label="Clique para abrir as direções no Google Maps",
                   url=directions_url)

    # Get Directions Iframe
    st.write('### Iframe de Direções: (Sorocaba-SP → São Paulo-SP)')
    iframe_url = gm.get_google_maps_directions_iframe_url(
        origin="Sorocaba-SP", destination="São Paulo-SP")
    components.iframe(iframe_url, height=450)

# Yelp Example


def yelp_example():
    '''
    Yelp Example
    '''
    st.write(
        '''
        ### ⭐ Yelp (Via scraper)
        - [Página de Busca](https://yelp.com/search?find_desc=Attractions&find_loc=Sorocaba,%20Sao+Paulo,%20Brasil&start=0&limit=10)
        '''
    )

    # Create YelpScrapper instance
    yelp = YelpScrapper()

    # Get Attractions JSON
    st.write('### Atrações Perto de Sorocaba-SP')
    attractions = yelp.get_near_attractions_json(
        city_name="Sorocaba", state_name="São Paulo")

    # Show JSON data with Pandas
    df = pd.read_json(StringIO(attractions))
    st.write(df)


openweathermap_example()
st.divider()
googlemaps_example()
st.divider()
yelp_example()
