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
def Cadastrar():
    # Set page title
    st.set_page_config(
        page_title="Planejar Viagem",
        page_icon="✏️",
        layout='wide',
        initial_sidebar_state="expanded",
    )

    st.title('✏️ Planejar Viagem')
    st.write(
        '''
        Comece a planejar sua viagem preenchendo as informações abaixo.
        '''
    )

    title = st.text_input('Título', placeholder='Viagem de Férias')

    # City and State
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

    with st.spinner('Carregando mapa...'):
        components.iframe(iframe_url, height=450)

    # Datepicker
    st.write('#### Quando?')
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

    st.write('#### Clima e Tempo')
    st.write(f"Aqui você pode consultar o clima e tempo para **{
             destination}** nos próximos 5 dias.")
    weather_view = WeatherView(destination_city, destination_state)
    weather_view.display_forecast()

    st.write('---')
    st.write('### Meu Roteiro')

    st.write('Aqui você pode definir os objetivos da viagem, como visitar pontos turísticos, conhecer a cultura local, etc.')

    st.write(f'#### Sugestões de Atrações em {
             destination_city}, {destination_state}')
    st.write('Selecione as atrações que deseja visitar durante a viagem.')

    attractions_ideas = AttractionsView(
        city_name=destination_city, state_name=destination_state)
    attractions_ideas.display_attractions(
        display_selector=True, selected_attractions=get_selected_attractions(), on_change=update_selected_attractions)

    st.write('#### Objetivos da Viagem')
    st.write(
        'Descreva os objetivos da viagem, como visitar pontos turísticos, conhecer a cultura local, etc.')
    goals = st.text_area(
        'Objetivos', placeholder='Ex: Visitar o Museu do Ipiranga, Conhecer a Avenida Paulista, etc.')

    st.write('#### Gerar Roteiro com IA')
    st.write('Aqui você pode consultar e criar um roteiro da viagem com ajuda de Inteligência Artificial.')
    st.write('Em breve...')

    st.write('---')
    st.write('#### Sobre a Viagem')
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

    if st.button('Cadastrar', key='cadastrar', type='primary', use_container_width=True):
        trip_data = {
            "title": title,
            "origin_city": origin_city,
            "origin_state": origin_state,
            "destination_city": destination_city,
            "destination_state": destination_state,
            "start_date": start_date,
            "end_date": end_date,
            "goals": goals,
            'tags': tags,
            "notes": notes
        }

        # Make sure we have all the required data
        if not all(trip_data.values()):
            st.error('Por favor, preencha todos os campos obrigatórios.')
            return

        trip = Trip(trip_data=trip_data)
        if trip._save():
            st.success('Viagem cadastrada com sucesso!')

            # Allow user to download the trip data as CSV
            st.write('### Download dos Dados da Viagem')
            st.write(
                'Clique no botão abaixo para baixar os dados da viagem em formato CSV.')
            csv_data = trip._to_csv()
            st.download_button(
                label='Baixar Dados da Viagem',
                data=csv_data,
                file_name=f'{trip.title.replace(" ", "_")}_trip_data.csv',
                mime='text/csv'
            )

            # Clear session state
            st.session_state.add_new_trip_form = {
                'attractions': set()
            }

        else:
            st.error('Erro ao cadastrar a viagem.')


Cadastrar()
