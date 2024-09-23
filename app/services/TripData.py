import requests
import os
import json
from datetime import datetime, timedelta
import streamlit as st
from services.AppData import AppData


class TripData:
    def __init__(self):
        """
        Initialize the AppData class.
        """
        pass

    def save(self, id="", key="", value=""):
        """
        Save trip data to a JSON file.

        Args:
            trip_data (dict): The trip data to save.
        """
        print("Saving or updating trip data")
        folder_map = AppData()._get_storage_map()
        save_path = folder_map.get("trip")
        file_path = f"{save_path}/{id}.json"

        # Load existing data if the file exists
        if os.path.exists(file_path):
            try:
                with open(file_path, "r") as f:
                    data = json.load(f)
            except Exception as e:
                print(f"Error reading existing trip data: {e}")
                return False

            # Update the specific key if provided
            if key:
                data[key] = value
            else:
                data = value  # Overwrite with new data if no key is specified
        else:
            # No existing data, treat this as a new save
            data = {key: value} if key else value

        return AppData()._save_to_file(file_path, data)

    def delete(self, id, key):
        """
        Delete a specific key in trip data.

        Args:
            id (str): The trip ID.
            key (str): The key to delete.

        Returns:
            bool: True if deleted successfully, False otherwise.
        """
        id = AppData().sanitize_id(id)
        save_path = AppData()._get_storage_map().get("trip")
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

    @st.cache_data(ttl=10)
    def get_trip(_self, id, key=""):
        """
        Retrieve trip data by ID and key.

        Args:
            id (str): The trip ID.
            key (str): The specific key in the trip data.

        Returns:
            Any: The trip data value, or None if the file or key does not exist.
        """
        id = AppData().sanitize_id(id)
        save_path = AppData()._get_storage_map().get("trip")
        file_path = f"{save_path}/{id}.json"

        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:

                # Load the data
                data = json.load(f)
                data = json.loads(data)

                if key:
                    if key in data:
                        return data.get(key)
                    return None
                return data
        return None

    def get_available_trip_ids(_self):
        """
        Retrieve a list of trip IDs.

        Returns:
            list: A list of trip IDs.
        """
        save_path = AppData()._get_storage_map().get("trip")
        if os.path.exists(save_path):
            return [f.split(".")[0] for f in os.listdir(save_path) if f.endswith(".json")]
        return []

    def get_available_trips(_self):
        """
        Retrieve a list a dictionary of available trips.
        The dictionary contains the trip ID and the trip title.
        """
        available_trips = []
        for trip_id in _self.get_available_trip_ids():
            trip_title = _self.get_trip(trip_id, "title")
            available_trips.append({"id": trip_id, "title": trip_title})
        return available_trips
