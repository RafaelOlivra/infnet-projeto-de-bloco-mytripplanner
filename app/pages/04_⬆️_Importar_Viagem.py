import streamlit as st
import time

from services.Trip import Trip
from services.Logger import _log
from services.AppData import AppData

# --------------------------
# Session State
# --------------------------
if "selected_trip_id" not in st.session_state:
    st.session_state.selected_trip_id = None


# --------------------------
# View Trip Data
# --------------------------
def View_Trip():
    # Set logo
    assets_dir = AppData().get_assets_dir()
    st.logo(f"{assets_dir}my-trip-planner-logo.svg", size="large")
    
    # Set page title
    st.set_page_config(
        page_title="Importar Viagem",
        page_icon="⬆️",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    
    # Styles
    with open(f"{assets_dir}style.css") as css:
        st.markdown(f"<style>{css.read()}</style>", unsafe_allow_html=True)

    st.title("⬆️ Importar Viagem")
    st.write(
        """
        Aqui você pode importar as viagens que você planejou.

        ---
        """
    )

    trip = None
    uploaded_file = st.file_uploader(
        "Selecione o arquivo para importar", type=["csv", "json"]
    )
    with st.spinner("Importando viagem..."):
        if uploaded_file is not None:
            file_type = uploaded_file.name.split(".")[-1]
            file_contents = uploaded_file.getvalue().decode("utf-8")

            try:
                if file_type == "csv":
                    trip = Trip().from_csv(file_contents)
                elif file_type == "json":
                    trip = Trip().from_json(file_contents)
                else:
                    st.error(
                        "Formato de arquivo inválido. Por favor, selecione um arquivo CSV ou JSON."
                    )
                    return
            except Exception as e:
                st.error(f"Erro ao importar viagem: {str(e)}")
                return

            # Save the trip
            trip._save()

    if trip:
        st.success("Viagem importada com sucesso!")

        # Change to the trip view
        st.session_state.selected_trip_id = trip.get("id")
        with st.spinner("Redirecionando..."):
            time.sleep(2)
            st.switch_page("pages/02_🗺️_Minhas_Viagens.py")


# --------------------------
# INIT
# --------------------------
View_Trip()
