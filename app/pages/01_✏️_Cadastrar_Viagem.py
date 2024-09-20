import streamlit as st
from model.Trip import Trip


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
    origin_city = st.text_input('Origem (Cidade)', 'São Paulo')
    origin_state = st.text_input('Origem (Estado)', 'SP')
    destination_city = st.text_input('Destino (Cidade)', 'Rio de Janeiro')
    destination_state = st.text_input('Destino (Estado)', 'RJ')
    start_date = st.date_input(
        'Data de Início', value=None, min_value=None, max_value=None, key=None)
    end_date = st.date_input(
        'Data de Término', value=None, min_value=None, max_value=None, key=None)
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
