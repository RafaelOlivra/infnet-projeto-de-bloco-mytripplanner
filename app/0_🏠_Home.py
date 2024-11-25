import streamlit as st

from streamlit_extras.switch_page_button import switch_page
from dotenv import load_dotenv, find_dotenv

from services.AppData import AppData

# --------------------------
# Configurations
# ---------------------------

# Load environment variables
load_dotenv(find_dotenv("../.env"))


# --------------------------
# Page
# ---------------------------
def Home():

    # Set page title
    st.set_page_config(page_title="MyTripPlanner", page_icon="🗺️", layout="wide")

    st.title("🗺️ MyTripPlanner")
    st.write(
        """
        O MyTripPlanner é um aplicativo de planejamento de viagens, projetado para ajudar os usuários a organizarem suas jornadas de forma eficiente e personalizada. O app oferece previsões meteorológicas detalhadas e sugestões de roteiros para o destino escolhido, utilizando dados precisos de diversas APIs e integração com Inteligência Artificial. Com o MyTripPlanner, os viajantes podem desfrutar de uma experiência tranquila e agradável, sem surpresas indesejadas pelo caminho.
        """
    )

    assets_dir = AppData().get_config("assets_dir")
    st.image(f"{assets_dir}header-image.jpg", use_column_width=True)

    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.write(
                """
                ### 🗺️ Minhas Viagens
                Visualize suas viagens planejadas e fique por dentro de todas as informações importantes.
            """
            )
            open_google_sheet_importer = st.button(
                "Ver Minhas Viagens", use_container_width=True, key="open_my_trips"
            )
            if open_google_sheet_importer:
                switch_page("minhas viagens")

    with col2:
        with st.container(border=True):
            st.write(
                """
                ### ✏️ Planejar Viagem
                Planeje uma nova viagem e obtenha sugestões de rotas e atrações com base em suas preferências.
            """
            )
            open_csv_sheet_importer = st.button(
                "Planejar Nova Viagem",
                use_container_width=True,
                key="open_trip_planner",
            )
            if open_csv_sheet_importer:
                switch_page("planejar viagem")


# --------------------------
# INIT
# --------------------------
if __name__ == "__main__":
    Home()
