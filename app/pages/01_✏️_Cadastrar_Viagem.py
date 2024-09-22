import streamlit as st
import streamlit.components.v1 as components
import datetime
from model.Trip import Trip
from services.CityStateData import CityStateData
from services.GoogleMaps import GoogleMaps
from views.WeatherView import WeatherView

def Cadastrar():
    # Set page title
    st.set_page_config(
        page_title="Cadastro de Viagem",
        page_icon="✏️",
        layout='wide',
        initial_sidebar_state="expanded",
    )

    # Tests
    st.title('✏️ Planejamento de Viagem')
    st.write(
        '''
        Comece a planejar sua viagem preenchendo as informações abaixo.
        '''
    )

    title = st.text_input('Título', 'Viagem de Férias')

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
    st.write('Aqui você pode consultar o clima e tempo para a cidade de destino.')
    weather_view = WeatherView(destination_city, destination_state)
    weather_view.display_forecast()

    st.write('#### Roteiro')
    st.write('Aqui você pode consultar e criar um roteiro da viagem.')
    st.write('Em breve...')

    st.write('#### Sobre a Viagem')
    notes = st.text_area('Observações', 'Sem observações.')

    if st.button('Cadastrar'):
        trip_data = {
            "title": title,
            "origin_city": origin_city,
            "origin_state": origin_state,
            "destination_city": destination_city,
            "destination_state": destination_state,
            "start_date": start_date,
            "end_date": end_date,
            "notes": notes
        }

        trip = Trip(trip_data=trip_data)
        if trip._save():
            st.success('Viagem cadastrada com sucesso!')
        else:
            st.error('Erro ao cadastrar a viagem.')


Cadastrar()
