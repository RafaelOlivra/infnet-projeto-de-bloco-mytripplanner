import streamlit as st
from services.YelpScrapper import YelpScrapper
from services.AttractionsData import AttractionsData
from services.Utils import Utils
import json


class AttractionsView:
    id = ""
    city_name = ""
    state_name = ""
    start = 0
    limit = 12
    attractions = {}

    def __init__(self, city_name: str = "", state_name: str = "", start: int = 0, limit: int = 12, attractions=None):

        self.city_name = city_name
        self.state_name = state_name
        self.id = self._generate_id()
        self.start = start
        self.limit = limit
        self.attractions = attractions if attractions else self.get_attractions()

    def get_attractions(self):
        """
        Get the attractions data for the specified city and state.
        """
        with st.spinner("Buscando atrações..."):
            json_string = AttractionsData().get_attraction_data(self.id)
            if json_string:
                return json.loads(json_string)
            else:
                json_string = YelpScrapper().get_near_attractions_json(
                    self.city_name, self.state_name, self.start, self.limit)
                if json_string:
                    data = json.loads(json_string)
                    AttractionsData().save(self.id, data)
                    return data
                else:
                    return {}

    def display_attractions(self, display_selector=False, selected_attractions=None, on_change=None):
        """
        Display the attractions data.
        """
        if self.attractions and len(self.attractions) > 0:
            cols = st.columns(5)
            for idx, attraction in enumerate(self.attractions):
                with cols[idx % 5]:
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

    # --------------------------
    # Utils
    # --------------------------
    def _generate_id(self):
        """
        Generate a unique ID hash for the attraction.
        """
        #
        city_name = Utils().slugify(self.city_name)
        state_name = Utils().slugify(self.state_name)
        return f"{city_name}_{state_name}"
