import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv, find_dotenv
import pandas as pd
from services.OpenWeatherMap import OpenWeatherMap
from services.GoogleMaps import GoogleMaps

####################
# CONFIGURATION
####################

# Load environment variables
load_dotenv(find_dotenv('../.env'))

####################
# PAGES
####################


# Home Page
def Home():

    # Set page title
    st.title('🗺️ MyTripPlanner')
    st.write(
        '''
        O MyTripPlanner é um aplicativo de planejamento de viagens, projetado para ajudar os usuários a organizarem suas jornadas de forma eficiente e personalizada. O app oferece previsões meteorológicas detalhadas e sugestões de roteiros para o destino escolhido, utilizando dados precisos de diversas APIs e integração com Inteligência Artificial. Com o MyTripPlanner, os viajantes podem desfrutar de uma experiência tranquila e agradável, sem surpresas indesejadas pelo caminho.
        '''
    )

    # Useful links
    st.write(
        '''
        ### Links Úteis

        ### Artefatos
        - [Repositório no GitHub](https://github.com/RafaelOlivra/python-llms-if-tp1)
        - [Business Model Canvas](https://docs.google.com/drawings/d/1LDVFgGZBJcKsntF1MJgB_Y5skqeSBI1mjtDtm7hmOt8/edit)
        - [Project Charter](https://docs.google.com/document/d/1aqE3sguPtd9xvBwgypT2NwycYuOskVr0EFID9omDIic/edit?usp=sharing)
        - [Data Summary Report](https://docs.google.com/document/d/1jie_4x3r550BwLlOtSxuLYOwWTwRtqeiXuroQSZUtJQ/edit?usp=sharing)

        ### Fontes de dados e APIs
        Essas fontes **poderão** ser utilizadas no desenvolvimento do MyTripPlanner
        - [OpenWeatherMap](https://openweathermap.org/)
        - [Google Maps](https://cloud.google.com/maps-platform)
        - [Waze](https://www.waze.com/pt-BR/)
        - [Here Maps](https://developer.here.com/)
        - [Perplexity AI](https://www.perplexity.ai/)
        - [Phind](https://www.phind.com/search?home=true)
        - [OpenAI](https://openai.com/)

        ### Inspirações
        - [Agenda 2030](https://brasil.un.org/pt-br/91863-agenda-2030-para-o-desenvolvimento-sustent%C3%A1vel)
        - [Streamlit Gallery](https://www.streamlit.io/gallery)
        '''
    )

####################
# DATA EXAMPLES
####################


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
    data = owm.get_forecast(city_name="Sorocaba",
                            state_name="São Paulo", days=5)
    st.write('### Dados do Tempo (Próximos 5 dias) (Sorocaba-SP)')

    # Create DataFrame
    df = pd.DataFrame(data)

    # Correct formats for display
    df['timestamp'] = df['timestamp'].astype(str)  # Show without commas
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


####################
# INIT
####################
if __name__ == '__main__':
    Home()
    st.divider()
    openweathermap_example()
    st.divider()
    googlemaps_example()
