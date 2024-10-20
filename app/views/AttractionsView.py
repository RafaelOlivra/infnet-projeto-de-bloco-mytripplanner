import streamlit as st

from services.YelpScrapper import YelpScrapper
from services.AttractionsData import AttractionsData
from lib.Utils import Utils

from models.Attraction import AttractionModel
from typing import List


class AttractionsView:
    def __init__(
        self,
        city_name: str = "",
        state_name: str = "",
        start: int = 0,
        limit: int = 50,
        attractions: List[AttractionModel] = None,
    ):
        """
        Initialize the AttractionsView class.

        Args:
            city_name (str): Name of the city.
            state_name (str): Name of the state.
            start (int): Starting index for fetching attractions.
            limit (int): Number of attractions to fetch.
            attractions (list[Attraction]): Pre-fetched attractions data (optional).
        """
        self.city_name = city_name
        self.state_name = state_name
        self.slug = AttractionsData().slugify(city_name, state_name)
        self.start = start
        self.limit = limit
        self.attractions = attractions if attractions else self._get_attractions()

    def render_attractions(
        self,
        display_selector=False,
        selected_attractions=None,
        on_change=None,
        st=st,
        columns=6,
    ):
        """
        Display the attractions data in a grid layout.

        Args:
            display_selector (bool): Whether to display a checkbox selector.
            selected_attractions (list): List of selected attractions (optional).
            on_change (function): Callback function to handle changes in selection (optional).
        """
        if self.attractions:
            cols = st.columns(columns)
            for idx, attraction in enumerate(self.attractions):
                with cols[idx % columns]:
                    if display_selector:
                        self.render_attraction_selector(
                            attraction,
                            selected=selected_attractions
                            and attraction.name in selected_attractions,
                            on_change=on_change,
                        )
                    else:
                        self.render_attraction_card(attraction)
        else:
            st.info("Nenhuma sugestão de atração encontrada para o destino.")

    def render_attraction_card(self, attraction: AttractionModel):
        """
        Display a single attraction card with image, name, and description.

        Args:
            attraction (Attraction): Attraction object.
        """
        st.image(str(attraction.image), use_column_width=True)

        # Display a star for review_stars
        stars = "⭐" * int(attraction.review_stars)
        review_count = (
            f"({attraction.review_count} reviews)" if attraction.review_count else ""
        )

        st.write(
            f"""
            **{attraction.name}**  \

            {stars} {review_count}  \

            [Mais informações]({attraction.url}) ⧉
            """
        )

    def render_attraction_selector(
        self, attraction: AttractionModel, on_change=None, selected=False
    ):
        """
        Display a single attraction card with a checkbox for selection.

        Args:
            attraction (Attraction): Attraction object.
            on_change (function): Callback function to handle changes in selection (optional).
            selected (bool): Whether the attraction is pre-selected (default: False).
        """
        st.image(str(attraction.image), use_column_width=True)

        # Display a star for review_stars
        stars = "⭐" * int(attraction.review_stars)
        review_count = (
            f"({attraction.review_count} reviews)" if attraction.review_count else ""
        )

        st.write(
            f"""
            **{attraction.name}**  \

            {stars} {review_count}  \

            [Mais informações]({attraction.url}) ⧉
            """
        )

        if st.checkbox("Selecionar", key=attraction.url, value=selected):
            if on_change:
                on_change(attraction.name)
        elif on_change:
            on_change(attraction.name, remove=True)

    def _get_attractions(self) -> List[AttractionModel]:
        """
        Get the attractions data for the specified city and state.

        Returns:
            list[Attraction]: List of validated Attraction objects.
        """
        with st.spinner("Buscando atrações..."):
            attractions = AttractionsData().get(self.slug)
            if attractions:
                return attractions
            else:
                attractions = YelpScrapper().get_near_attractions(
                    self.city_name, self.state_name, self.start, self.limit
                )

                if attractions:

                    # Save the attractions data
                    AttractionsData().save(slug=self.slug, attractions=attractions)

                    return attractions
                return []
