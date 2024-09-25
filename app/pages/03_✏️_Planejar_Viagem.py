import streamlit as st
import streamlit.components.v1 as components
import streamlit_tags as st_tags
import datetime
from model.Trip import Trip
from services.TripData import TripData
from services.CityStateData import CityStateData
from services.GoogleMaps import GoogleMaps
from views.WeatherView import WeatherView
from views.AttractionsView import AttractionsView
import time


# --------------------------
# Session State
# --------------------------
if 'add_new_trip_form' not in st.session_state:
    st.session_state.add_new_trip_form = {
        'attractions': set(),
    }

if 'show_new_trip_form' not in st.session_state:
    st.session_state.show_new_trip_form = True

if 'selected_trip_id' not in st.session_state:
    st.session_state.selected_trip_id = None


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
def Cadastrar():
    # Set page title
    st.set_page_config(
        page_title="Planejar Viagem",
        page_icon="✏️",
        layout='wide',
        initial_sidebar_state="expanded",
    )

    st.title('✏️ Planejar Nova Viagem')
    st.write(
        '''
        Comece a planejar sua viagem preenchendo as informações abaixo.
        '''
    )

    # Title
    st.write('### 🧳 1. Título')
    title = st.text_input('Dê um título para sua viagem.',
                          placeholder='Viagem de Férias')

    if not title:
        return

    # City and State
    st.write('---')
    st.write('### 🛫 2. Para Onde?')
    col1, col2 = st.columns(2)
    with col1:
        st.write('#### Origem')
        sub_col1, sub_col2 = st.columns([2, 8])
        with sub_col1:
            origin_state = st.selectbox(
                'Origem (Estado)', CityStateData().get_ufs(), index=25)
        with sub_col2:
            origin_city = st.selectbox(
                'Origem (Cidade)', CityStateData().get_cities_by_uf(origin_state), index=0)
    with col2:
        st.write('#### Destino')
        sub_col1, sub_col2 = st.columns([2, 8])
        with sub_col1:
            destination_state = st.selectbox(
                'Destino (Estado)', CityStateData().get_ufs(), index=18)
        with sub_col2:
            destination_city = st.selectbox(
                'Destino (Cidade)', CityStateData().get_cities_by_uf(destination_state), index=0)

    # Mostra um mapa com a origem e destino
    google_maps = GoogleMaps()
    origin = f"{origin_city}, {origin_state}"
    destination = f"{destination_city}, {destination_state}"
    iframe_url = google_maps.get_google_maps_directions_iframe_url(
        origin, destination)

    components.iframe(iframe_url, height=450)

    if not destination_city and not destination_state:
        return

    # Date
    st.write('---')
    st.write('### 📅 3. Quando?')
    today = datetime.datetime.now()
    week_from_today = today + datetime.timedelta(days=7)
    date = st.date_input(
        "Data da Viagem",
        (today, week_from_today),
        min_value=today,
        max_value=today + datetime.timedelta(days=365),
        format="DD/MM/YYYY"
    )
    if date:
        if len(date) > 1:
            start_date = date[0]
            end_date = date[1]
        else:
            start_date = date[0]
            end_date = False

    with st.expander('🌤️ Clima e Tempo', expanded=True):
        st.write(
            f"Aqui você pode consultar o clima e tempo para **{destination}** nos próximos 5 dias.")
        weather_view = WeatherView(destination_city, destination_state)
        weather_view.display_forecast()

    # Goals
    st.write('---')
    st.write('### 🏟️ 4. Objetivos ')

    st.write('Aqui você pode definir os objetivos da viagem, como visitar pontos turísticos, conhecer a cultura local, etc.')

    with st.expander(f'💡 Sugestões de Atrações em {destination_city}, {destination_state}', expanded=True):
        st.write(
            'Você pode selecionar algumas das sugestões de atrações que para conhecer durante a viagem.')

        attractions_ideas = AttractionsView(
            city_name=destination_city, state_name=destination_state)
        attractions_ideas.display_attractions(
            display_selector=True, selected_attractions=get_selected_attractions(), on_change=update_selected_attractions)

    st.write('#### Objetivos da Viagem')
    st.write(
        'Descreva os objetivos da viagem, como visitar pontos turísticos, conhecer a cultura local, etc.')
    goals = st.text_area(
        'Objetivos', placeholder='Ex: Visitar o Museu do Ipiranga, Conhecer a Avenida Paulista, etc.')

    if not goals:
        return

    # Trip AI generation
    st.write('---')
    st.write('### 🤖 5. Gerar Roteiro com IA')
    st.write('Aqui você pode consultar e criar um roteiro da viagem com ajuda de Inteligência Artificial.')
    st.write('Em breve...')

    st.write('---')
    st.write('### ✏️ 6. Sobre a Viagem')
    notes = st.text_area(
        'Observações', '', placeholder='Ex: Levar roupas de banho, Protetor solar, etc.')
    tags = st_tags.st_tags(
        label='Tags',
        text='Pressione enter para adicionar uma tag (Max. 5)',
        value=[],
        suggestions=['Viagem', 'Férias', 'Lazer', 'Trabalho', 'Negócios'],
        maxtags=5,
        key='1'
    )

    # Save trip
    if st.button('Cadastrar', key='cadastrar', type='primary', use_container_width=True):
        time_format = Trip()._get_time_format()
        trip_data = {
            "title": title,
            "origin_city": origin_city,
            "origin_state": origin_state,
            "destination_city": destination_city,
            "destination_state": destination_state,
            "start_date": start_date.strftime(time_format),
            "end_date": end_date.strftime(time_format),
            "goals": goals,
            'tags': tags,
            "notes": notes
        }

        trip = Trip(trip_data=trip_data)
        if trip:
            st.success('Viagem cadastrada com sucesso!')

            # Clear session state
            del st.session_state.add_new_trip_form

            # Change to the trip view
            st.session_state.selected_trip_id = trip.id
            with st.spinner('Redirecionando...'):
                time.sleep(2)
                st.switch_page("pages/02_🗺️_Minhas_Viagens.py")

        else:
            st.error('Erro ao cadastrar a viagem.')

# --------------------------
# INIT
# --------------------------
Cadastrar()
