import time
import streamlit as st
from streamlit_js_eval import streamlit_js_eval

from services.TripData import TripData
from services.Trip import Trip

from views.TripView import TripView

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

    col1, col2 = st.columns(2)
    with col1:
        st.title("🗺️ Minhas Viagens")
        st.write(
            """
            Aqui estão as viagens que você planejou
            """
        )

    with col2:
        st.write("   ")
        with st.container(border=True):
            available_trips = TripData().get_user_trips()
            selected_trip_id = st.session_state.selected_trip_id

            if not available_trips or not available_trips[0]:
                st.write("Você ainda não planejou nenhuma viagem.")
                return

            # Display a select box for the available trips, if the selected trip is not in the available trips
            # the first trip in the list will be selected by default.
            # Options can have the same name, but the id is unique. So we add a prefix to the title to make it unique.
            options = [f"{trip['title']} ({trip['id']})" for trip in available_trips]

            # Check selected_trip_id is contained in the options and set the selected index
            # The first trip in the list will be selected by default
            selected_index = options.index(options[0])
            for option in options:
                # Check if the string contains the selected_trip_id
                if selected_trip_id and selected_trip_id in option:
                    selected_index = options.index(option)
                    break

            selected_trip_id = st.selectbox(
                label="Selecione uma viagem",
                options=options,
                index=selected_index,
                key="select_trip",
                placeholder="Selecione uma viagem",
            )

            # Set the selected trip id in the session state
            st.session_state.selected_trip_id = selected_trip_id

    st.write("---")

    if not selected_trip_id:
        return

    selected_trip_id = selected_trip_id.split("(")[-1].split(")")[0]

    # Get the selected trip
    trip = Trip(trip_id=selected_trip_id)

    # Render the selected trip
    TripView(trip).render_trip()

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
            file_name=f"{trip.get('slug')}.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with col2:
        json_data = trip.to_json()
        st.download_button(
            label="Exportar Dados da Viagem (JSON)",
            data=json_data,
            file_name=f"{trip.get('slug')}.json",
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
        TripData().delete(trip.get("id"))
        st.session_state.selected_trip_id = None
        st.success("Viagem deletada com sucesso!")
        with st.spinner("Atualizando..."):
            time.sleep(2)
            st.session_state.selected_trip_id = None
            selected_trip_id = None
            # st.switch_page("pages/02_🗺️_Minhas_Viagens.py")
            streamlit_js_eval(js_expressions="parent.window.location.reload()")


# --------------------------
# INIT
# --------------------------
View_Trip()
