import pandas as pd
from datetime import datetime
import streamlit as st
from streamlit_card import card
from services.YelpScrapper import YelpScrapper
import json


class AttractionsView:
    city_name = ""
    state_name = ""
    start = 0
    limit = 4
    attractions_data = {}

    def __init__(self, city_name: str = "", state_name: str = "", start: int = 0, limit: int = 4, attractions_data=None):

        self.city_name = city_name
        self.state_name = state_name
        self.start = start
        self.limit = limit
        self.attractions_data = attractions_data if attractions_data else self.get_attractions()

    def get_attractions(self):
        """
        Get the attractions data for the specified city and state.
        """
        json_string = YelpScrapper().get_near_attractions_json(
            self.city_name, self.state_name, self.start, self.limit)

        if json_string:
            return json.loads(json_string)
        else:
            return {}

    def display_attractions(self):
        """
        Display the attractions data.
        """
        if self.attractions_data and len(self.attractions_data) > 0:
            cols = st.columns(4)
            for idx, attraction in enumerate(self.attractions_data):
                with cols[idx % 4]:  # Use modulo to cycle through columns
                    card(
                        title=attraction['name'],
                        text=attraction['description'],
                        image=attraction['image'],
                        url=attraction['url'],
                        styles={
                            "card": {
                                "width": "100%",
                                "height": "300px"
                            }
                        }
                    )
        else:
            st.warning("Nenhuma sugestão de atração encontrada para o destino.")
