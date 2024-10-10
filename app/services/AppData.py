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
    # Config Operations
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

    # --------------------------
    # CRUD Operations
    # --------------------------

    def save(self, type: str = "", id: str = "", json="", replace=False):
        """
        Save arbitrary data to a file.
        """
        # Check if we have the required parameters
        if not type or not id or not json:
            return False

        # Sanitize the ID
        id = self.sanitize_id(id)
        if not id:
            return False

        # Get the storage directory
        folder_map = self._get_storage_map()
        save_path = folder_map.get(type)
        file_path = f"{save_path}/{id}.json"

        # Check if the file already exists
        if os.path.exists(file_path) and not replace:
            # Return an error if the file already exists
            return False

        # Save the data to the file
        return self._save_file(file_path, json)

    @st.cache_data(ttl=10)
    def get(_self, type: str = "", id: str = "") -> dict:
        """
        Retrieve data from a file.
        """

        # Check if we have the required parameters
        if not type or not id:
            return None

        # Sanitize the ID
        id = _self.sanitize_id(id)
        if not id:
            return False

        folder_map = _self._get_storage_map()
        save_path = folder_map.get(type)
        file_path = f"{save_path}/{id}.json"

        # Check if the file exists
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                data = json.load(f)

                #  If we have a string, try to load it as JSON again
                if isinstance(data, str):
                    data = json.loads(data)

            return data
        return None

    def get_all(self, type: str = "") -> list:
        """
        Retrieve all data from a file.
        """
        # Check if we have the required parameters
        if not type:
            return []

        folder_map = self._get_storage_map()
        save_path = folder_map.get(type)

        # Check if the directory exists
        if not os.path.exists(save_path):
            return []

        # Get all files in the directory
        files = os.listdir(save_path)
        data = []

        # Use the get method to retrieve the data for each file
        for file in files:
            id = file.replace(".json", "")
            data.append(self.get(type, id))

        return data

    def get_all_ids(self, type: str = "") -> list:
        """
        Retrieve all data IDs from a file.
        """

        # Check if we have the required parameters
        if not type:
            return []

        folder_map = self._get_storage_map()
        save_path = folder_map.get(type)

        # Check if the directory exists
        if not os.path.exists(save_path):
            return []

        # Get all files in the directory
        files = os.listdir(save_path)
        return [file.replace(".json", "") for file in files]

    def update(self, type: str = "", id: str = "", key: str = "", value: str = ""):
        """
        Update a specific key in a file.
        """

        # Check if we have the required parameters
        if not type or not id or not key:
            return False

        # Get the existing data
        data = self.get(type, id)
        if not data:
            return False

        # Update the specific key
        data[key] = value

        # Save the updated data
        return self.save(type, id, data, replace=True)

    def delete(self, type: str = "", id: str = ""):
        """
        Delete data from a file.
        """

        # Check if we have the required parameters
        if not type or not id:
            return False

        # Sanitize the ID
        id = self.sanitize_id(id)

        if not id:
            return False

        # Get the storage directory
        folder_map = self._get_storage_map()
        save_path = folder_map.get(type)
        file_path = f"{save_path}/{id}.json"

        return self._delete_file(file_path)

    # --------------------------
    # Utils
    # --------------------------

    def _save_file(self, file_path, json):
        """
        Save data to a file.

        Args:
            file_path (str): The file path to save the data to.
            json (Any): The json data to save.

        Returns:
            bool: True if saved successfully, False otherwise.
        """
        # Ensure the directory exists
        folder = os.path.dirname(file_path)
        if not os.path.exists(folder):
            os.makedirs(folder)

        # If we have a json object, convert it to a string
        if isinstance(json, dict):
            json = json.dumps(json)

        try:
            with open(file_path, "w") as f:
                f.write(json)
            return True
        except Exception as e:
            print(f"Error saving data to file: {e}")
            return False

    def _delete_file(self, file_path):
        """
        Delete a file.

        Args:
            file_path (str): The file path to delete.

        Returns:
            bool: True if deleted successfully, False otherwise.
        """
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False

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
