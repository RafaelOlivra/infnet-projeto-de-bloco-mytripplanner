import requests
import os
import json
from datetime import datetime, timedelta
import streamlit as st


class AppData:
    """
    A class to handle data storage and retrieval from configuration files and environment variables.

    This class provides methods for retrieving and saving configuration data, API keys, and trip data.
    """

    def __init__(self):
        """
        Initialize the AppData class.
        """
        pass

    # --------------------------
    # Getters
    # --------------------------
    def get_config(self, key):
        """
        Retrieve configuration data from the config JSON file.

        Args:
            key (str): The specific key in the configuration file.

        Returns:
            Any: The configuration value, or None if the key does not exist.
        """
        config_file = "app/config/cfg.json"
        if os.path.exists(config_file):
            with open(config_file, "r") as f:
                data = json.load(f)
                return data.get(key)
        return None

    def get_api_key(self, key):
        """
        Retrieve an API key from environment variables.

        Args:
            key (str): The key name of the API service (e.g., 'googlemaps').

        Returns:
            str: The corresponding API key, or None if not found.
        """
        key_map = {
            "openweathermap": "OPENWEATHERMAP_API_KEY",
            "googlemaps": "GOOGLEMAPS_API_KEY",
            "scraperapi": "SCRAPER_API_KEY",
        }
        return os.getenv(key_map.get(key))

    def _get_storage_map(self):
        """
        Define the storage map based on configuration.

        Returns:
            dict: A dictionary with storage directory mappings.
        """
        temp_storage_dir = self.get_config("temp_storage_dir")
        permanent_storage_dir = self.get_config("permanent_storage_dir")
        return {
            "trip": f"{temp_storage_dir}/trip",
            "attractions": f"{permanent_storage_dir}/attractions",
        }

    # --------------------------
    # Utils
    # --------------------------

    def _save_to_file(self, file_path, data):
        """
        Save data to a file.

        Args:
            file_path (str): The file path to save the data to.
            data (Any): The data to save.

        Returns:
            bool: True if saved successfully, False otherwise.
        """
        # Ensure the directory exists
        folder = os.path.dirname(file_path)
        if not os.path.exists(folder):
            os.makedirs(folder)

        try:
            with open(file_path, "w") as f:
                json.dump(data, f)
            return True
        except Exception as e:
            print(f"Error saving data to file: {e}")
            return False

    def sanitize_id(self, id):
        """
        Sanitize the trip ID. For now, it ensures the ID is valid (e.g., UUID).

        Args:
            id (str): The trip ID.

        Returns:
            str: The sanitized ID.
        """
        if len(id) == 36:
            return id
        return None
