import os
import json
import streamlit as st

from services.AppData import AppData
from services.Utils import Utils

from models.AttractionModel import AttractionModel
from typing import List, Optional


class AttractionsData:
    def __init__(self):
        """
        Initialize the AttractionsData class.
        """
        self.app_data = AppData()

    # --------------------------
    # CRUD Operations
    # --------------------------

    def save(self, attractions: List[AttractionModel], slug: str = "") -> bool:
        """
        Save or update attraction data to a JSON file.

        Args:
            slug (str): Attraction slug.
            attractions (list[Attraction]): List of Attraction objects.

        Returns:
            bool: True if the data was saved successfully, False otherwise.
        """
        folder_map = self.app_data._get_storage_map()
        save_path = folder_map.get("attractions")
        file_path = f"{save_path}/{slug}.json"

        # Prepare a json including all the attractions
        data = [attraction.__dict__ for attraction in attractions]

        # Save the data
        return self.app_data._save_file(file_path, data)

    @st.cache_data(ttl=10)
    def get(_self, slug: str) -> Optional[List[AttractionModel]]:
        """
        Retrieve attractions data for the specified ID.

        Args:
            slug (str): The Attraction slug.

        Returns:
            Attraction or None: The attraction data as an Attraction object.
        """
        folder_map = _self.app_data._get_storage_map()
        save_path = folder_map.get("attractions")
        file_path = f"{save_path}/{slug}.json"

        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                data = json.load(f)

                # Convert the JSON data to Attraction objects
                return [AttractionModel(**item) for item in data]
        return None

    def delete(self, slug: str) -> bool:
        """
        Delete the Attraction ID data.

        Args:
            slug (str): The Attraction slug to delete.

        Returns:
            bool: True if the file was deleted, False otherwise.
        """
        folder_map = self.app_data._get_storage_map()
        save_path = folder_map.get("attractions")
        file_path = f"{save_path}/{slug}.json"

        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False

    # --------------------------
    # Utils
    # --------------------------
    def slugify(self, city_name: str, state_name: str) -> str:
        """
        Generate a unique ID based on the city and state names.

        Returns:
            str: Generated ID.
        """
        city_name = Utils().slugify(city_name)
        state_name = Utils().slugify(state_name)
        return f"{state_name}_{city_name}"
