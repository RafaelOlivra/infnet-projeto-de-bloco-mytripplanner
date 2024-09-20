import streamlit as st
import datetime
from model.Trip import Trip
from services.CityStateData import CityStateData


def Cadastrar():
    # Set page title
    st.set_page_config(
        page_title="Cadastro de Viagem",
        page_icon="✏️",
        layout='wide',
        initial_sidebar_state="expanded",
    )

    # Tests
    st.title('✏️ Cadastro de Viagem')
    st.write(
        '''
        Preencha o formulário abaixo para cadastrar uma nova viagem.
        '''
    )

    # Form
    title = st.text_input('Título', 'Viagem de Férias')

    col1, col2 = st.columns(2)
    with col1:
        origin_state = st.selectbox(
            'Origem (Estado)', CityStateData().get_ufs())
    with col2:
        origin_city = st.selectbox(
            'Origem (Cidade)', CityStateData().get_cities_by_uf(origin_state))

    col1, col2 = st.columns(2)
    with col1:
        destination_state = st.selectbox(
            'Destino (Estado)', CityStateData().get_ufs())
    with col2:
        destination_city = st.selectbox(
            'Destino (Cidade)', CityStateData().get_cities_by_uf(destination_state))

    # Datepicker
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
        if trip.save():
            st.success('Viagem cadastrada com sucesso!')
        else:
            st.error('Erro ao cadastrar a viagem.')


Cadastrar()
