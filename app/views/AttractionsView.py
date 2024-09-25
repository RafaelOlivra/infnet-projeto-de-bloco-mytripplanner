import streamlit as st
from services.YelpScrapper import YelpScrapper
from services.AttractionsData import AttractionsData
from services.Utils import Utils
import json


class AttractionsView:
    def __init__(
        self,
        city_name: str = "",
        state_name: str = "",
        start: int = 0,
        limit: int = 50,
        attractions=None,
    ):
        """
        Initialize the AttractionsView class.

        Args:
            city_name (str): Name of the city.
            state_name (str): Name of the state.
            start (int): Starting index for fetching attractions.
            limit (int): Number of attractions to fetch.
            attractions (dict): Pre-fetched attractions data (optional).
        """
        self.city_name = city_name
        self.state_name = state_name
        self.id = self._generate_id()
        self.start = start
        self.limit = limit
        self.attractions = attractions if attractions else self.get_attractions()

    def get_attractions(self):
        """
        Get the attractions data for the specified city and state.

        Returns:
            dict: The attractions data in JSON format.
        """
        with st.spinner("Buscando atrações..."):
            json_string = AttractionsData().get_attraction_data(self.id)
            if json_string:
                return json.loads(json_string)
            else:
                json_string = YelpScrapper().get_near_attractions_json(
                    self.city_name, self.state_name, self.start, self.limit
                )
                if json_string:
                    data = json.loads(json_string)
                    AttractionsData().save(self.id, data)
                    return data
                return {}

    def display_attractions(
        self, display_selector=False, selected_attractions=None, on_change=None
    ):
        """
        Display the attractions data in a grid layout.

        Args:
            display_selector (bool): Whether to display a checkbox selector.
            selected_attractions (list): List of selected attractions (optional).
            on_change (function): Callback function to handle changes in selection (optional).
        """
        if self.attractions:
            cols = st.columns(5)
            for idx, attraction in enumerate(self.attractions):
                with cols[idx % 5]:
                    if display_selector:
                        self.display_attraction_selector(
                            attraction,
                            selected=selected_attractions
                            and attraction["name"] in selected_attractions,
                            on_change=on_change,
                        )
                    else:
                        self.display_attraction_card(attraction)
        else:
            st.warning("Nenhuma sugestão de atração encontrada para o destino.")

    def display_attraction_card(self, attraction):
        """
        Display a single attraction card with image, name, and description.

        Args:
            attraction (dict): Dictionary containing attraction data.
        """
        st.image(attraction["image"], use_column_width=True)
        st.markdown(f"##### {attraction['name']}")
        if attraction.get("description"):
            st.markdown(f"{attraction['description']}")
        st.markdown(f"[Mais informações]({attraction['url']})")

    def display_attraction_selector(self, attraction, on_change=None, selected=False):
        """
        Display a single attraction card with a checkbox for selection.

        Args:
            attraction (dict): Dictionary containing attraction data.
            on_change (function): Callback function to handle changes in selection (optional).
            selected (bool): Whether the attraction is pre-selected (default: False).
        """
        st.image(attraction["image"], use_column_width=True)

        # Display a star for review_stars
        stars = ""
        for _ in range(int(attraction["review_stars"])):
            stars += "⭐"

        review_count = attraction.get("review_count")
        review_count = f"({review_count} reviews)" if review_count else ""
        title = attraction["name"]
        description = attraction.get("description") or ""
        url = attraction.get("url")
        url = f"[Mais informações]({url}) ⧉" if url else ""

        st.write(
            f"""
                    **{title}**  \

                    {stars} {review_count}  \

                    {url}
                    """
        )

        if st.checkbox("Selecionar", key=url, value=selected):
            if on_change:
                on_change(attraction["name"])
        elif on_change:
            on_change(attraction["name"], remove=True)

    # --------------------------
    # Utils
    # --------------------------
    def _generate_id(self):
        """
        Generate a unique ID based on the city and state names.

        Returns:
            str: Generated ID.
        """
        city_name = Utils().slugify(self.city_name)
        state_name = Utils().slugify(self.state_name)
        return f"{state_name}_{city_name}"
