import streamlit as st
import streamlit.components.v1 as components
import streamlit_tags as st_tags
import datetime
import time

from services.Trip import Trip

from services.CityState import CityStateData
from services.GoogleMaps import GoogleMaps
from services.Logger import _log

from lib.Utils import Utils

from views.WeatherView import WeatherView
from views.AttractionsView import AttractionsView
from views.ItineraryView import ItineraryView

from models.Attraction import AttractionModel
from models.Weather import ForecastModel
from models.Itinerary import DailyItineraryModel


# --------------------------
# Session State
# --------------------------
if "selected_attractions" not in st.session_state:
    st.session_state.selected_attractions = set()

if "show_new_trip_form" not in st.session_state:
    st.session_state.show_new_trip_form = True

if "selected_trip_id" not in st.session_state:
    st.session_state.selected_trip_id = None

if "cached_itinerary" not in st.session_state:
    st.session_state.cached_itinerary = None


# --------------------------
# Form State Handlers
# --------------------------
def update_selected_attractions(attraction_name, remove=False):
    """
    Update the selected attractions and save it using session state.
    """
    selected_attractions = get_selected_attractions()

    # Initialize the selected attractions if it's empty
    if not selected_attractions:
        selected_attractions = set()

    if remove:
        if attraction_name in selected_attractions:
            selected_attractions.remove(attraction_name)
    else:
        selected_attractions.add(attraction_name)

    st.session_state.selected_attractions = selected_attractions


def get_selected_attractions():
    """
    Get the selected attractions from the session state.
    """
    return st.session_state.selected_attractions


def get_cached_itinerary() -> list[DailyItineraryModel]:
    return st.session_state.cached_itinerary


def clear_cached_values():
    """
    Clear the cached values in the session state.
    """
    st.session_state.selected_attractions = None
    st.session_state.cached_itinerary = None
    st.session_state.show_new_trip_form = None


# --------------------------
# Add new trip form
# --------------------------
def Cadastrar():
    # Set page title
    st.set_page_config(
        page_title="Planejar Viagem",
        page_icon="✏️",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.title("✏️ Planejar Nova Viagem")
    st.write(
        """
        Comece a planejar sua viagem preenchendo as informações abaixo.
        
        ---
        """
    )

    # Title
    with st.container(border=True):
        st.write("### 🧳 1. Minha Viagem")

        col1, col2 = st.columns([6, 4])
        with col1:
            st.write("##### Título")
            title = st.text_input(
                "Dê um título para sua viagem",
                placeholder="Viagem de Férias",
                label_visibility="visible",
            )

        with col2:
            # Select transportation mode
            st.write("##### Eu vou de...")
            travel_by = Trip()._get_travel_by_options()
            travel_by_labels = [travel_by[idx] for idx in travel_by]
            selected_travel_by = st.selectbox(
                "Selecione um meio de transporte",
                travel_by_labels,
                index=0,
                label_visibility="visible",
            )
            travel_by = [
                key for key, value in travel_by.items() if value == selected_travel_by
            ][0]

    if not title or not travel_by:
        # if the form is empty, clear the cached values for safety
        clear_cached_values()
        return

    # City and State
    with st.container(border=True):
        st.write("### 📍 2. Para Onde?")

        ufs = CityStateData().get_ufs()

        col1, col2, col3 = st.columns([10, 1, 10])
        with col1:
            st.write("##### Origem")
            sub_col1, sub_col2 = st.columns([2, 8])
            with sub_col1:
                origin_state = st.selectbox("Origem (Estado)", ufs, index=25)
            with sub_col2:
                origin_city = st.selectbox(
                    "Origem (Cidade)",
                    CityStateData().get_cities_by_uf(origin_state),
                    index=None,
                    placeholder="Selecione uma cidade...",
                )

        # Clear destination city if the state is not selected
        if not origin_city:
            return

        with col3:
            st.write("##### Destino")
            sub_col1, sub_col2 = st.columns([2, 8])
            with sub_col1:
                destination_state = st.selectbox("Destino (Estado)", ufs, index=18)
            with sub_col2:
                destination_city = st.selectbox(
                    "Destino (Cidade)",
                    CityStateData().get_cities_by_uf(destination_state),
                    index=None,
                    placeholder="Selecione uma cidade...",
                )

        # Clear destination city if the state is not selected
        if not destination_city:
            return

        # Display Google Maps directions iframe
        google_maps = GoogleMaps()
        origin = f"{origin_city}, {CityStateData().uf_to_state(origin_state)}"
        destination = (
            f"{destination_city}, {CityStateData().uf_to_state(destination_state)}"
        )
        iframe_url = google_maps.get_google_maps_directions_iframe_url(
            origin, destination, mode=travel_by
        )

        components.iframe(iframe_url, height=450)

    if not destination:
        return

    # Date and Weather
    trip_length = 0
    with st.container(border=True):
        st.write("### 📅 3. Quando?")
        today = datetime.datetime.now()
        week_from_today = today + datetime.timedelta(days=2)
        date = st.date_input(
            "Data da Viagem",
            (today, week_from_today),
            min_value=today,
            max_value=today + datetime.timedelta(days=365),
            format="DD/MM/YYYY",
        )
        if date:
            if len(date) > 1:
                start_date = Utils.to_datetime(date[0])
                end_date = Utils.to_datetime(date[1])
            else:
                start_date = Utils.to_datetime(date[0])
                end_date = False

        # Get the weather forecast
        if start_date and end_date:
            trip_length = (end_date - start_date).days

        # Show a notice if the trip is more than 5 days away
        if trip_length > 5:
            st.warning(
                "💡 A previsão do tempo está disponível apenas para os próximos 5 dias."
            )

        weather = None
        with st.expander(
            f"🌤️ Clima e tempo para **{destination_city}, {destination_state}** para os próximos dias.",
            expanded=True,
        ):
            weather_view = WeatherView(destination_city, destination_state)
            weather_view.render_forecast()
            weather = weather_view.forecast

    # Goals
    with st.container(border=True):
        st.write("### 🏕️ 4. Objetivos ")

        st.write("##### Objetivos da Viagem")
        st.write(
            "Descreva os objetivos da viagem, como visitar pontos turísticos, conhecer a cultura local, etc."
        )
        goals = st.text_area(
            "Objetivos",
            placeholder="Ex: Visitar o Museu do Ipiranga, Conhecer a Avenida Paulista, etc.",
            label_visibility="collapsed",
        )

        if not goals:
            return

    # Attractions
    with st.container(border=True):
        st.write("##### Atrações")
        st.write(
            "Você pode selecionar algumas das sugestões de atrações que para conhecer durante a viagem."
        )

        attractions = []
        with st.expander(
            f"💡 Sugestões de Atrações em {destination_city}, {destination_state}",
            expanded=True,
        ):
            attractions_ideas = AttractionsView(
                city_name=destination_city, state_name=destination_state
            )
            attractions_ideas.render_attractions(
                display_selector=True,
                selected_attractions=get_selected_attractions(),
                on_change=update_selected_attractions,
            )

            # Filter selected attractions
            for attraction in attractions_ideas.attractions:
                if attraction.name in get_selected_attractions():
                    attractions.append(attraction)

        # Convert to AttractionModel
        if attractions.__len__() == 0:
            attractions = None
        else:
            st.info(
                "**Atrações Selecionadas:** "
                + ", ".join(get_selected_attractions())
                + "."
            )

    # Trip AI Itinerary generation
    with st.container(border=True):
        st.write("### 🤖 5. Gerar Roteiro com IA")
        st.write(
            """
            Aqui você pode consultar e criar um roteiro da viagem com ajuda de Inteligência Artificial.  \
                
            O roteiro é gerado com base nas informações da viagem, como a previsão do tempo, atrações selecionadas, etc.
            """
        )

        # Show a notice if the trip is more than 4 days away
        if trip_length > 4:
            st.warning(
                "💡 Atualmente, nosso assistente pode gerar roteiros para no máximo 4 dias."
            )

        itinerary = get_cached_itinerary()
        if not itinerary:
            if st.button(
                "Gerar Roteiro Personalizado",
                use_container_width=True,
                key="generate_itinerary",
            ):
                if itinerary:
                    st.info("Você já gerou um roteiro para esta viagem.")

                itinerary = ItineraryView.render_itinerary_generator(
                    location=f"{destination_city}, {destination_state}",
                    start_date=start_date,
                    end_date=end_date,
                    forecast_list=weather,
                    attractions_list=attractions,
                )

                if itinerary:
                    st.session_state.cached_itinerary = itinerary
                    st.rerun()

        if itinerary:
            st.success("Roteiro gerado com sucesso!")
            ItineraryView(itinerary=itinerary).render_itinerary()
            if st.button(
                "Limpar Roteiro",
                use_container_width=True,
                key="reset_itinerary",
            ):
                st.session_state.cached_itinerary = None
                st.rerun()

    # Notes and Tags
    with st.container(border=True):
        st.write("### 📝 6. Sobre a Viagem")
        notes = st.text_area(
            "Observações",
            "",
            placeholder="Ex: Levar roupas de banho, Protetor solar, etc.",
        )
        tags = st_tags.st_tags(
            label="Tags",
            text="Pressione enter para adicionar uma tag (Max. 5)",
            value=[],
            suggestions=["Viagem", "Férias", "Lazer", "Trabalho", "Negócios"],
            maxtags=5,
            key="1",
        )

    # Save trip
    if st.button(
        "Cadastrar", key="cadastrar", type="primary", use_container_width=True
    ):

        if itinerary:
            # Convert DailyItineraryModel to dict to avoid errors
            itinerary = [daily_itinerary.model_dump() for daily_itinerary in itinerary]

        trip_data = {
            "title": title,
            "origin_city": origin_city,
            "origin_state": origin_state,
            "destination_city": destination_city,
            "destination_state": destination_state,
            "travel_by": travel_by,
            "start_date": start_date,
            "end_date": end_date,
            "weather": weather,
            "attractions": attractions,
            "itinerary": itinerary,
            "goals": goals,
            "tags": tags,
            "notes": notes,
        }

        trip = Trip(trip_data=trip_data, save=True)
        if trip:
            st.success("Viagem cadastrada com sucesso!")

            # Clear the required session state
            clear_cached_values()

            # Change to the trip view
            st.session_state.selected_trip_id = trip.get("id")
            with st.spinner("Redirecionando..."):
                time.sleep(2)
                st.switch_page("pages/02_🗺️_Minhas_Viagens.py")

        else:
            st.error("Erro ao cadastrar a viagem.")


# --------------------------
# INIT
# --------------------------
Cadastrar()
