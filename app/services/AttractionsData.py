import os
import json
import streamlit as st
from services.AppData import AppData


class AttractionsData:
    def __init__(self):
        """
        Initialize the AttractionsData class.
        """
        self.app_data = AppData()

    def save(self, id="", data=""):
        """
        Save or update attraction data to a JSON file.

        Args:
            id (str): Attraction ID.
            data (any): The value to store in the attraction data.

        Returns:
            bool: True if the data was saved successfully, False otherwise.
        """
        print("Saving or updating attraction data")
        folder_map = self.app_data._get_storage_map()
        save_path = folder_map.get("attractions")
        file_path = f"{save_path}/{id}.json"

        # Save the data
        return self.app_data._save_to_file(file_path, data)

    def delete(self, id):
        """
        Delete the Attraction ID data.

        Args:
            id (str): The Attraction ID to delete.

        Returns:
            bool: True if the file was deleted, False otherwise.
        """
        id = self.app_data.sanitize_id(id)
        save_path = self.app_data._get_storage_map().get("attractions")
        file_path = f"{save_path}/{id}.json"

        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False

    @st.cache_data(ttl=10)
    def get_attraction_data(_self, id):
        """
        Retrieve attractions data for the specified ID.

        Args:
            id (str): The Attraction ID.

        Returns:
            dict or None: The attraction data.
        """
        data = _self.get_attraction_json(id)
        return data

    @st.cache_data(ttl=10)
    def get_attraction_json(_self, id):
        """
        Retrieve the JSON data for the specified Attraction ID.

        Args:
            id (str): The Attraction ID.

        Returns:
            dict or None: The JSON data for the attraction, or None if not found.
        """
        id = _self.app_data.sanitize_id(id)
        save_path = _self.app_data._get_storage_map().get("attraction")
        file_path = f"{save_path}/{id}.json"

        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                try:
                    data = json.loads(json.load(f))
                    return data
                except json.JSONDecodeError as e:
                    print(f"Error loading attraction JSON: {e}")
                    return None
        return None
