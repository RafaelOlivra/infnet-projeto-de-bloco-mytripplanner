import streamlit as st
import datetime
import random

from services.YelpScrapper import YelpScrapper
from services.AttractionsData import AttractionsData
from services.Logger import _log
from lib.Utils import Utils

from models.Attraction import AttractionModel
from typing import List


class AttractionsView:
    def __init__(
        self,
        city_name: str = "",
        state_name: str = "",
        start: int = 0,
        limit: int = 18,
        attractions: List[AttractionModel] = None,
        expire_time: int = 8640000,  # 100 days
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
        self.expire_time = expire_time

        # Should be last!
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

        if st.checkbox("Selecionar", key=attraction.id, value=selected):
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

            # Check if the data is expired
            old_attractions = None
            if attractions and self._attractions_expired(attractions[0].created_at):
                old_attractions = attractions  # Save the old data
                attractions = None

            if attractions:
                return attractions

            # Fetch the attractions data
            try:
                attractions = self._fetch_attractions()
            except Exception as e:
                _log(f"Error fetching attractions: {e}", level="ERROR")
                # Use the old data if available
                attractions = old_attractions if old_attractions else []

            return attractions

    def _fetch_attractions(self) -> List[AttractionModel]:
        """
        Fetch the attractions data from the Yelp API.

        Returns:
            list[Attraction]: List of Attraction objects.
        """
        attractions = YelpScrapper().get_near_attractions(
            self.city_name, self.state_name, self.start, self.limit
        )

        # Save the attractions data
        AttractionsData().save(slug=self.slug, attractions=attractions)

        return attractions

    def _attractions_expired(self, created_at: datetime) -> bool:
        """
        Check if the attractions data is expired.

        Args:
            last_updated (datetime): The last updated timestamp.

        Returns:
            bool: True if the data is expired, False otherwise.
        """
        lifetime = datetime.datetime.now() - Utils.to_datetime(created_at)
        lifetime_seconds = lifetime.total_seconds()
        is_expired = lifetime_seconds > self.expire_time

        return is_expired
