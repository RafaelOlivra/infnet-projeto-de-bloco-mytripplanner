import os
import json
import streamlit as st
from services.AppData import AppData


class TripData:
    def __init__(self):
        """
        Initialize the TripData class.
        """
        self.app_data = AppData()

    def save(self, id="", key="", value=""):
        """
        Save or update trip data to a JSON file.

        Args:
            id (str): Trip ID.
            key (str): The key to update within the trip data. If empty, the entire value is replaced.
            value (any): The value to store in the trip data.

        Returns:
            bool: True if the data was saved successfully, False otherwise.
        """
        print("Saving or updating trip data")
        folder_map = self.app_data._get_storage_map()
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
            # Create new data if file doesn't exist
            data = {key: value} if key else value

        # Save the updated or new data
        return self.app_data._save_to_file(file_path, data)

    def delete(self, id):
        """
        Delete the trip data for the specified trip ID.

        Args:
            id (str): The trip ID to delete.

        Returns:
            bool: True if the file was deleted, False otherwise.
        """
        id = self.app_data.sanitize_id(id)
        save_path = self.app_data._get_storage_map().get("trip")
        file_path = f"{save_path}/{id}.json"

        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False

    @st.cache_data(ttl=10)
    def get_trip_data(_self, id, key=""):
        """
        Retrieve trip data for the specified trip ID. Optionally, return a specific key.

        Args:
            id (str): The trip ID.
            key (str): Specific key to return from the trip data.

        Returns:
            dict or None: The trip data or the specific key value if found.
        """
        data = _self.get_trip_json(id)
        if data and key:
            return data.get(key)
        return data

    @st.cache_data(ttl=10)
    def get_trip_json(_self, id):
        """
        Retrieve the JSON data for the specified trip ID.

        Args:
            id (str): The trip ID.

        Returns:
            dict or None: The JSON data for the trip, or None if not found.
        """
        id = _self.app_data.sanitize_id(id)
        save_path = _self.app_data._get_storage_map().get("trip")
        file_path = f"{save_path}/{id}.json"

        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                try:
                    data = json.loads(json.load(f))
                    return data
                except json.JSONDecodeError as e:
                    print(f"Error loading trip JSON: {e}")
                    return None
        return None

    def get_available_trip_ids(self):
        """
        Retrieve a list of available trip IDs.

        Returns:
            list: A list of trip IDs.
        """
        save_path = self.app_data._get_storage_map().get("trip")
        if os.path.exists(save_path):
            return [
                f.split(".")[0] for f in os.listdir(save_path) if f.endswith(".json")
            ]
        return []

    def get_available_trips(self):
        """
        Retrieve a list of available trips with their IDs and titles.

        Returns:
            list: A list of dictionaries containing trip ID and title.
        """
        available_trips = []
        for trip_id in self.get_available_trip_ids():
            trip_title = self.get_trip_data(trip_id, "title")
            available_trips.append({"id": trip_id, "title": trip_title})
        return available_trips
