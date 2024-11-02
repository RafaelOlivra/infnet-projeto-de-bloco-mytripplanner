import streamlit as st
import pandas as pd
import plotly.express as px
import pydeck as pdk

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

    # Total users
    with st.container(border=True):
        cols = st.columns(5)
        cols[0].metric("Total de Usuários", "1")

        # Total stored trips
        cols[1].metric("Total de Viagens", f"{TripData().count_all()}")

        # Visited cities
        visited_cities = TripData().get_all_trips()
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
    trips = TripData().get_all_trips()
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

    ##### Plot a bar chart with the number of attractions by city
    attractions_by_city = AttractionsData().get_attractions_by_city()

    # Prepare a dictionary with city names and the number of attractions
    attractions_count = {}
    for city in attractions_by_city.keys():
        attractions_count[city] = len(attractions_by_city[city])

    try:
        # Plot a bar chart with the number of attractions by city
        fig = px.bar(
            x=list(attractions_count.keys()),
            y=list(attractions_count.values()),
            labels={"x": "Cidade", "y": "Número de Atrações"},
            title="Atrações por Cidade",
        )
        st.plotly_chart(fig)
    except ValueError:
        st.write("Nenhuma atração encontrada.")


# --------------------------
# INIT
# --------------------------
View_Stats()
