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

from services.SentimentAnalysisProvider import SentimentAnalyzer


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

    trips = TripData().get_all_trips()

    ######################## Trip Stats ########################

    # --------------------------
    # Total trips
    # --------------------------

    st.write("#### 🧳 Viagens")

    # Total users
    with st.container(border=True):
        cols = st.columns(5)
        cols[0].metric("Total de Usuários", "1")

        # Total stored trips
        cols[1].metric("Total de Viagens", f"{TripData().count_all()}")

        # Visited cities
        visited_cities = trips
        cities_attractions = set()
        for trip_model in visited_cities:
            cities_attractions.add(
                trip_model.destination_city + ", " + trip_model.destination_state
            )
        cols[2].metric("Cidades Visitadas", f"{len(cities_attractions)}")

        # Scraped cities
        cols[3].metric("Cidades Scrapeadas", f"{AttractionsData().count_cities()}")

        # Scraped attractions
        cols[4].metric(
            "Atrações Scrapeadas", f"{AttractionsData().count_attractions()}"
        )
    st.write("")

    # --------------------------
    # Plotly Graphs with Trips by City
    # --------------------------
    st.write("###### Total de Viagens por Cidade")

    ##### Plot the a map with most visited cities

    # Get the most visited places
    trips_by_destination_tracker = []
    trips_by_destination = []
    for trip_model in trips:
        destination = trip_model.destination_city + ", " + trip_model.destination_state
        if destination not in trips_by_destination_tracker:
            trips_by_destination_tracker.append(destination)

            # Add geolocation to the destination
            lat, long = LatLong().get_coordinates(
                city=trip_model.destination_city, state=trip_model.destination_state
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
                    item["visits"] += len(trip_model.attractions)

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

    # --------------------------
    # Bar with the number os trips by month and year
    # --------------------------
    trips_by_month = {}
    for trip_model in trips:
        month = trip_model.start_date.strftime("%b %Y")
        if month not in trips_by_month:
            trips_by_month[month] = 0
        trips_by_month[month] += 1

    try:
        # Plot a bar chart with the number of trips by month
        fig = px.bar(
            x=list(trips_by_month.keys()),
            y=list(trips_by_month.values()),
            labels={"x": "Mês", "y": "Número de Viagens"},
            title="Viagens por Mês",
        )
        st.plotly_chart(fig)
    except ValueError:
        st.write("Nenhuma viagem encontrada.")

    # --------------------------
    # Pie chart with the number with the transport used
    # --------------------------
    col1, col2 = st.columns(2)
    transport_tracker = []
    for trip_model in trips:
        transport = trip_model.travel_by
        if transport not in transport_tracker:
            transport_tracker.append(transport)

    transport_count = {}
    transport_labels = Trip()._get_travel_by_options()
    for transport in transport_tracker:
        transport_name = transport_labels[transport]
        transport_count[transport_name] = 0
        for trip_model in trips:
            if trip_model.travel_by == transport:
                transport_count[transport_name] += 1

    try:
        # Plot a pie chart
        fig = px.pie(
            values=list(transport_count.values()),
            names=list(transport_count.keys()),
            title="Meio de Transporte Utilizado",
        )
        col1.plotly_chart(fig)

    except ValueError:
        col1.write("Nenhuma viagem encontrada.")

    # --------------------------
    # Pier chart with most common weather conditions
    # --------------------------
    weather_tracker = {}
    for trip_model in trips:
        weather = trip_model.weather
        if weather:
            for forecast in weather:
                condition = forecast.weather
                if condition not in weather_tracker:
                    weather_tracker[condition] = 0
                weather_tracker[condition] += 1

    try:
        # Plot a pie chart
        fig = px.pie(
            values=list(weather_tracker.values()),
            names=list(weather_tracker.keys()),
            title="Condições do Tempo",
        )
        col2.plotly_chart(fig)
    except ValueError:
        col2.write("Nenhuma condição do tempo encontrada.")

    ######################## Attractions ########################

    st.write("#### 🚩 Atrações")

    # --------------------------
    # Plotly Graphs with Attractions by City
    # --------------------------
    st.write("")
    st.write("###### Total de Atrações por Cidade")

    ##### Plot the a map with the attractions by city

    # Get the attractions by city
    attractions_by_city = AttractionsData().get_attractions_by_city()

    cities_attractions = []
    for city_uf in attractions_by_city.keys():
        # Count attractions per city
        if city_uf not in cities_attractions:
            count = 0
        count += len(attractions_by_city[city_uf])

        # Add geolocation to the destination
        city_uf, state = city_uf.split(", ")
        lat, long = LatLong().get_coordinates(city=city_uf, state=state)

        cities_attractions.append(
            {
                "city": city_uf,
                "attractions": count,
                "lat": lat,
                "long": long,
            }
        )

    # Create a DataFrame with the data
    df = pd.DataFrame(cities_attractions)

    # Plot the map with pydeck

    # Create a ColumnLayer for the Aérea (Air) data
    column_layer = pdk.Layer(
        "ColumnLayer",
        df,
        get_position="[long, lat]",
        get_elevation="attractions",
        elevation_scale=20000,
        get_fill_color=[33, 204, 220],
        elevation_range=[0, 100],
        radius=10000,
        pickable=True,
        extruded=True,
        auto_highlight=True,
    )

    view_state = pdk.ViewState(
        latitude=-15.793889, longitude=-47.882778, zoom=3.5, pitch=10, bearing=0
    )

    r = pdk.Deck(
        layers=[column_layer],
        initial_view_state=view_state,
        map_provider="mapbox",
        tooltip={"text": "{city}\n{attractions} Atrações"},
    )

    st.pydeck_chart(r)

    # --------------------------
    # Bar chart with the number of attractions by state
    # --------------------------

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

    ######################## Users ########################

    st.write("#### 👤 Usuários")

    # Stopwords
    stopwords = ""
    stopwords_file = AppData().get_config("stopwords_file")

    # Load the stopwords file
    with open(stopwords_file, "r", encoding="utf-8") as file:
        stopwords = file.read()

    stopwords = stopwords.split()

    # --------------------------
    # Do sentiment analysis on the trips
    # --------------------------
    # Get the sentiment of the trips
    with st.spinner("Analisando sentimentos..."):
        sentiments_tracker = []
        for trip_model in trips:
            trip = Trip().from_model(trip_model)
            sentiment = trip.get_meta("sentiment")
            if not sentiment:
                feedback = trip.get_meta("feedback")
                if feedback:
                    sentiment = SentimentAnalyzer().analyze_sentiment(feedback)
                    trip.save_meta("sentiment", sentiment)
                else:
                    sentiment = "N/A"
            sentiments_tracker.append(sentiment)

    # Create a DataFrame with the data
    df = pd.DataFrame(sentiments_tracker, columns=["Sentimento"])

    # Plot the sentiment analysis in a pie chart
    try:
        fig = px.pie(
            df,
            names="Sentimento",
            title="Análise de Sentimentos (Feedback das Viagens)",
        )
        st.plotly_chart(fig)
    except ValueError:
        st.write("Nenhum sentimento encontrado.")

    # --------------------------
    # Crate a bar char with the most common words in the feedback,
    # grouped  and colored by the trip destination
    # --------------------------
    words_by_destination = {}
    for trip_model in trips:
        trip = Trip().from_model(trip_model)
        destination = trip_model.destination_city + ", " + trip_model.destination_state
        feedback = trip.get_meta("feedback")
        if feedback:
            feedback_words = re.sub(r"[^\w\s]", "", feedback.lower()).split()
            # remove stopwords
            feedback_words = [word for word in feedback_words if word not in stopwords]
            if destination not in words_by_destination:
                words_by_destination[destination] = []
            words_by_destination[destination].extend(feedback_words)

    # Create a DataFrame
    df = pd.DataFrame(
        [
            {"Destination": dest, "Word": word}
            for dest, words in words_by_destination.items()
            for word in words
        ]
    )

    # Count occurrences of words per destination
    word_counts = df.groupby(["Destination", "Word"]).size().reset_index(name="Count")

    # Plotting with Plotly
    fig = px.bar(
        word_counts,
        x="Word",
        y="Count",
        color="Destination",
        barmode="group",
        title="Palavras mais Comuns nos Feedbacks (Por Destino)",
        labels={"Word": "Feedback", "Count": "Contagem"},
    )

    fig.update_layout(
        xaxis_title="Words", yaxis_title="Count", legend_title="Destination"
    )

    st.plotly_chart(fig, use_container_width=True)

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

    for trip_model in trips:
        # Get words from the title and description
        words.extend(get_words(trip_model.title))
        words.extend(get_words(trip_model.origin_city))
        words.extend(get_words(trip_model.origin_state))
        words.extend(get_words(trip_model.destination_city))
        words.extend(get_words(trip_model.destination_state))
        words.extend(get_words(trip_model.goals))
        words.extend(get_words(trip_model.notes))

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
        generate_wordcloud(words=words, stopwords=stopwords),
        use_column_width=True,
    )


# --------------------------
# INIT
# --------------------------
View_Stats()
