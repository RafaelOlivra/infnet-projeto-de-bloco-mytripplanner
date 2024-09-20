import requests
import os
import json
from datetime import datetime, timedelta
from functools import lru_cache


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

    def get(self, group="config", id="", key=""):
        """
        Retrieve data from a specified group and key.

        Args:
            group (str): The data group (e.g., 'config', 'api_key', 'trip').
            id (str): The identifier for the data (used mainly for 'trip').
            key (str): The specific key to retrieve the data.

        Returns:
            Any: The retrieved data, or None if the key or group is invalid.
        """
        folder_map = self._get_storage_map()

        # Check if group exists in the storage map
        if group not in folder_map or not key:
            return None

        # App Config
        if group == "config":
            return self.get_config(key)

        # API Keys
        if group == "api_key":
            return self.get_api_key(key)

        # Trip Data
        if group == "trip":
            return self.get_trip_data(id, key)

        return None

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
            "yelp": "YELP_API_KEY",
            "opencagedata": "OPENCAGEDATA_API_KEY",
        }
        return os.getenv(key_map.get(key))

    def get_trip_data(self, id, key):
        """
        Retrieve trip data by ID and key.

        Args:
            id (str): The trip ID.
            key (str): The specific key in the trip data.

        Returns:
            Any: The trip data value, or None if the file or key does not exist.
        """
        id = self.sanitize_id(id)
        save_path = self._get_storage_map().get("trip")
        file_path = f"{save_path}/{id}.json"

        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                data = json.load(f)
                return data.get(key)
        return None

    def _get_storage_map(self):
        """
        Define the storage map based on configuration.

        Returns:
            dict: A dictionary with storage directory mappings.
        """
        storage_dir = self.get_config("storage_dir")
        return {
            "trip": f"{storage_dir}/trip",
        }

    # --------------------------
    # Setters
    # --------------------------

    def save(self, group="trip", id="", key="", value=""):
        """
        Save data to the specified group and key.

        Args:
            group (str): The group to save data in (e.g., 'trip').
            id (str): The identifier for the data (used mainly for 'trip').
            key (str): The specific key to store the value.
            value (Any): The value to store.

        Returns:
            bool: True if the data was successfully saved, False otherwise.
        """
        folder_map = self._get_storage_map()

        if group not in folder_map or value is None:
            return False

        # Trip Data
        if group == "trip":
            print("Saving trip data")
            return self._save_trip_data(value)

        return False

    def _save_trip_data(self, TripData):
        """
        Save trip data to a file.

        Args:
            TripData (dict): The trip data to save.

        Returns:
            bool: True if saved successfully, False otherwise.
        """
        id = self.sanitize_id(TripData["trip_id"])
        save_path = self._get_storage_map().get("trip")
        file_path = f"{save_path}/{id}.json"

        # Create save directory if it doesn't exist
        if not os.path.exists(save_path):
            os.makedirs(save_path)

        with open(file_path, "w") as f:
            json.dump(TripData, f)
        return True

    def _update_trip_data(self, id, key, value):
        """
        Update a specific key in an existing trip data file.

        Args:
            id (str): The trip ID.
            key (str): The key to update.
            value (Any): The value to update.

        Returns:
            bool: True if updated successfully, False otherwise.
        """
        id = self.sanitize_id(id)
        save_path = self._get_storage_map().get("trip")
        file_path = f"{save_path}/{id}.json"

        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                data = json.load(f)
                data[key] = value

            with open(file_path, "w") as f:
                json.dump(data, f)
            return True
        return False

    # --------------------------
    # Delete
    # --------------------------

    def delete(self, group="trip", id="", key=""):
        """
        Delete data from a specified group by ID and key.

        Args:
            group (str): The group to delete data from (e.g., 'trip').
            id (str): The identifier for the data.
            key (str): The specific key to delete.

        Returns:
            bool: True if deletion was successful, False otherwise.
        """
        folder_map = self._get_storage_map()

        if group not in folder_map or not key:
            return False

        # Trip Data
        if group == "trip":
            return self._delete_trip_data(id, key)

        return False

    def _delete_trip_data(self, id, key):
        """
        Delete a specific key in trip data.

        Args:
            id (str): The trip ID.
            key (str): The key to delete.

        Returns:
            bool: True if deleted successfully, False otherwise.
        """
        id = self.sanitize_id(id)
        save_path = self._get_storage_map().get("trip")
        file_path = f"{save_path}/{id}.json"

        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                data = json.load(f)
                if key in data:
                    del data[key]
                    with open(file_path, "w") as f:
                        json.dump(data, f)
                    return True
        return False

    # --------------------------
    # Utils
    # --------------------------

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
