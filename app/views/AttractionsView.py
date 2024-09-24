import streamlit as st
from services.YelpScrapper import YelpScrapper
import json


class AttractionsView:
    city_name = ""
    state_name = ""
    start = 0
    limit = 12
    attractions_data = {}

    def __init__(self, city_name: str = "", state_name: str = "", start: int = 0, limit: int = 12, attractions_data=None):

        self.city_name = city_name
        self.state_name = state_name
        self.start = start
        self.limit = limit
        self.attractions_data = attractions_data if attractions_data else self.get_attractions()

    def get_attractions(self):
        """
        Get the attractions data for the specified city and state.
        """
        with st.spinner("Buscando atrações..."):
            json_string = YelpScrapper().get_near_attractions_json(
                self.city_name, self.state_name, self.start, self.limit)

            if json_string:
                return json.loads(json_string)
            else:
                return {}

    def display_attractions(self, display_selector=False, selected_attractions=None, on_change=None):
        """
        Display the attractions data.
        """
        if self.attractions_data and len(self.attractions_data) > 0:
            cols = st.columns(6)
            for idx, attraction in enumerate(self.attractions_data):
                with cols[idx % 6]:
                    if display_selector:
                        self.display_attraction_selector(
                            attraction, selected=selected_attractions and attraction['name'] in selected_attractions, on_change=on_change)
                    else:
                        self.display_attraction_card(attraction)
        else:
            st.warning("Nenhuma sugestão de atração encontrada para o destino.")

    def display_attraction_card(self, attraction):
        """
        Display a single attraction card.
        """

        st.image(attraction['image'], use_column_width=True)
        st.markdown(f"##### {attraction['name']}")
        if attraction['description']:
            st.markdown(f"{attraction['description']}")
        st.markdown(f"[Mais informações]({attraction['url']})")

    def display_attraction_selector(self, attraction, on_change=None, selected=False):
        """
        Display a single attraction card, with the option to select it with streamlit checkbox.
        """

        st.image(attraction['image'], use_column_width=True)
        st.markdown(f"##### {attraction['name']}")
        if attraction['description']:
            st.markdown(f"{attraction['description']}")
        st.markdown(f"[Mais informações]({attraction['url']})")
        if st.checkbox(
                "Selecionar", key=attraction['name'], value=selected):
            if on_change:
                on_change(attraction['name'])
        else:
            if on_change:
                on_change(attraction['name'], remove=True)
