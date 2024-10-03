import streamlit as st
import pandas as pd
from services.TripData import TripData
from model.Trip import Trip
from io import StringIO
import time

# --------------------------
# Session State
# --------------------------
if "selected_trip_id" not in st.session_state:
    st.session_state.selected_trip_id = None


# --------------------------
# View Trip Data
# --------------------------
def View_Trip():
    # Set page title
    st.set_page_config(
        page_title="Minhas Viagens",
        page_icon="🗺️",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.title("🗺️ Minhas Viagens")
    st.write(
        """
        Aqui estão as viagens que você planejou

        ---
        """
    )

    available_trips = TripData().get_available_trips()
    selected_trip_id = st.session_state.selected_trip_id

    if not available_trips and not selected_trip_id:
        st.write("Você ainda não planejou nenhuma viagem.")
        return

    if not selected_trip_id:
        selected_trip_id = available_trips[0].get("id")
        st.session_state.selected_trip_id = selected_trip_id

    # Display a select box for the available trips, if the selected trip is not in the available trips
    # the first trip in the list will be selected by default.
    # Options can have the same name, but the id is unique. So we add a prefix to the title to make it unique.
    options = [f"{trip['title']} ({trip['id']})" for trip in available_trips]

    # Check selected_trip_id is contained in the options and set the selected index
    selected_index = 0
    for option in options:
        # Check if the string contains the selected_trip_id
        if selected_trip_id in option:
            selected_index = options.index(option)
            break

    selected_trip_id = st.selectbox(
        "Selecione uma viagem:",
        options=options,
        index=selected_index,
        key="select_trip",
    )
    selected_trip_id = selected_trip_id.split("(")[-1].split(")")[0]

    trip = Trip(id=selected_trip_id)
    df = pd.read_csv(StringIO(trip.to_csv()))
    st.dataframe(df)

    # Allow users to export the trip data
    st.write("---")
    st.write("### ⬇️ Exportar Dados da Viagem")
    st.write("Clique no botão abaixo para baixar os dados da viagem.")
    col1, col2 = st.columns(2)
    with col1:
        csv_data = trip.to_csv()
        st.download_button(
            label="Exportar Dados da Viagem (CSV)",
            data=csv_data,
            file_name=f"{trip.slug}.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with col2:
        json_data = trip.to_json()
        st.download_button(
            label="Exportar Dados da Viagem (JSON)",
            data=json_data,
            file_name=f"{trip.slug}.json",
            mime="application/json",
            use_container_width=True,
        )

    # Allow users to delete the trip
    st.write("---")
    st.write("### 🗑️ Deletar Viagem")
    st.write("Clique no botão abaixo para deletar a viagem.")
    st.error("**Atenção:** Esta ação é irreversível.")

    confirm_delete = st.checkbox("Confirmar a exclusão da viagem", key="confirm_delete")
    if (
        st.button(
            "Deletar Viagem",
            key="delete_trip",
            type="primary",
            use_container_width=True,
            disabled=(not confirm_delete),
        )
        and confirm_delete
    ):
        TripData().delete(trip.id)
        st.session_state.selected_trip_id = None
        st.success("Viagem deletada com sucesso!")
        with st.spinner("Atualizando..."):
            time.sleep(2)
            st.switch_page("pages/02_🗺️_Minhas_Viagens.py")


# --------------------------
# INIT
# --------------------------
View_Trip()
