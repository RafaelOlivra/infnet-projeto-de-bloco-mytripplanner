import re
import streamlit as st
import pandas as pd
import plotly.express as px
import pydeck as pdk
import wordcloud as wc

from lib.LatLong import LatLong

from services.Trip import Trip
from services.AttractionsData import AttractionsData
from services.AppData import AppData
from services.TripData import TripData


# --------------------------
# View Stats
# --------------------------
def View_Stats():
    # Set page title
    st.set_page_config(
        page_title="Estatísticas",
        page_icon="📈",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.title("📈 Estatísticas")
    st.write(
        """
        Aqui você pode ver estatísticas sobre os dados do projeto.
        """
    )
    st.write("")

    # Show metrics for the overall project

    # --------------------------
    # Overall Stats
    # --------------------------

    trips = TripData().get_all_trips()

    # Total users
    with st.container(border=True):
        cols = st.columns(5)
        cols[0].metric("Total de Usuários", "1")

        # Total stored trips
        cols[1].metric("Total de Viagens", f"{TripData().count_all()}")

        # Visited cities
        visited_cities = trips
        cities = set()
        for trip in visited_cities:
            cities.add(trip.destination_city + ", " + trip.destination_state)
        cols[2].metric("Cidades Visitadas", f"{len(cities)}")

        # Scraped cities
        cols[3].metric("Cidades Scrapeadas", f"{AttractionsData().count_cities()}")

        # Scraped attractions
        cols[4].metric(
            "Atrações Scrapeadas", f"{AttractionsData().count_attractions()}"
        )
    st.write("")

    # --------------------------
    # Plotly Graphs with Attractions by City
    # --------------------------
    st.write(
        """
        ###### Total de Viagens por Cidade
        """
    )

    ##### Plot the a map with most visited cities

    # Get the most visited places
    trips_by_destination_tracker = []
    trips_by_destination = []
    for trip in trips:
        destination = trip.destination_city + ", " + trip.destination_state
        if destination not in trips_by_destination_tracker:
            trips_by_destination_tracker.append(destination)

            # Add geolocation to the destination
            lat, long = LatLong().get_coordinates(
                city=trip.destination_city, state=trip.destination_state
            )

            trips_by_destination.append(
                {
                    "destination": destination,
                    "visits": 1,
                    "lat": lat,
                    "long": long,
                }
            )
        else:
            for item in trips_by_destination:
                if item["destination"] == destination:
                    item["visits"] += len(trip.attractions)

    # Create a DataFrame with the data
    df = pd.DataFrame(trips_by_destination)

    # Plot the map with pydeck

    # Create a ColumnLayer for the Aérea (Air) data
    column_layer = pdk.Layer(
        "ColumnLayer",
        df,
        get_position="[long, lat]",
        get_elevation="visits",
        elevation_scale=40000,
        get_fill_color=[253, 208, 23],
        elevation_range=[0, 100],
        radius=10000,
        pickable=True,
        extruded=True,
        auto_highlight=True,
    )

    view_state = pdk.ViewState(
        latitude=-19.793889, longitude=-47.882778, zoom=4.5, pitch=10, bearing=0
    )

    r = pdk.Deck(
        layers=[column_layer],
        initial_view_state=view_state,
        map_provider="mapbox",
        tooltip={"text": "{destination}\n{visits} Viagens"},
    )

    st.pydeck_chart(r)

    ##### Plot a bar chart with the number of attractions by state
    attractions_by_city = AttractionsData().get_attractions_by_city()
    attractions_count_by_state = {}
    for city_state in attractions_by_city.keys():
        # Split city and state, assuming the format is "City, State"
        _, state = city_state.split(", ")

        # Count attractions per state
        if state not in attractions_count_by_state:
            attractions_count_by_state[state] = 0
        attractions_count_by_state[state] += len(attractions_by_city[city_state])

    try:
        # Plot a bar chart with the number of attractions by state
        fig = px.bar(
            x=list(attractions_count_by_state.keys()),
            y=list(attractions_count_by_state.values()),
            labels={"x": "UF", "y": "Número de Atrações"},
            title="Atrações por Estado",
        )
        st.plotly_chart(fig)
    except ValueError:
        st.write("Nenhuma atração encontrada.")

    # --------------------------
    # Word Cloud with words from the trips
    # --------------------------
    words = []

    def get_words(phrase: str = ""):
        # Use regex to replace any character that is not a letter or number with a space
        cleaned_phrase = re.sub(r"[^\w\s]", "", phrase.lower())  # Remove punctuation
        cleaned_phrase = re.sub(
            r"\s+", " ", cleaned_phrase
        )  # Replace multiple spaces/newlines with a single space
        words = cleaned_phrase.split()  # Split by space into words list
        return words

    for trip in trips:
        # Get words from the title and description
        words.extend(get_words(trip.title))
        words.extend(get_words(trip.origin_city))
        words.extend(get_words(trip.origin_state))
        words.extend(get_words(trip.destination_city))
        words.extend(get_words(trip.destination_state))
        words.extend(get_words(trip.goals))
        words.extend(get_words(trip.notes))

    # Stopwords
    stopwords_pt_br = """
    a à agora aí ainda além algumas algo algumas alguns ali ano anos ante antes 
    ao aos apenas apoio após aquela aquelas aquele aqueles aqui aquilo as às assim 
    até atrás bem bom cada cá casa caso coisa com como comprido conhecido contra 
    contudo custa da daquele daqueles das de debaixo dela delas dele deles demais 
    dentro depois desde dessa dessas desse desses desta destas deste destes deve 
    devem devendo dever deverá deverão deveria deveriam devia deviam disse disso disto 
    dito diz dizem do dois dos doze duas durante e é ela elas ele eles em 
    embora enquanto entre era eram essa essas esse esses esta está estamos estão 
    estar estas estava estavam este estes estou eu fazer faz fiz foi for foram 
    fosse foram fui há isso isto já la lá lhe lhes lo mais maior mas me 
    mesma mesmas mesmo mesmos meu meus minha minhas muito muitos na não nas 
    nem nenhum nessa nessas neste nossos nossa nossas num numa nós o os onde 
    ou outra outras outro outros para pela pelas pelo pelos perante pode poder 
    poderá podia podia pois por porque portanto pouco poucos pra qual qualquer 
    quando quanto que quem ser se seja sejam sem sempre sendo seu seus só 
    sob sobre sua suas tal também tanta tantas tanto tão te tem tendo tenha 
    ter teu teus tive tivemos tiver tiveram tivesse tivessem tiveste tivestes toda 
    todas todo todos tu tua tuas tudo último um uma umas uns vendo ver 
    vez vindo vir você vocês vos
    """
    stopwords_pt_br = stopwords_pt_br.split()

    # Create the word cloud
    @st.cache_data(ttl=60 * 60 * 24, show_spinner=True)
    def generate_wordcloud(words, stopwords):
        return (
            wc.WordCloud(
                width=800,
                height=400,
                stopwords=stopwords,
                background_color="white",
                colormap="viridis",
            )
            .generate(" ".join(words))
            .to_image()
        )

    st.write(
        """
        ###### Nuvem de Palavras
        """
    )
    st.image(
        generate_wordcloud(words=words, stopwords=stopwords_pt_br),
        use_column_width=True,
    )


# --------------------------
# INIT
# --------------------------
View_Stats()
