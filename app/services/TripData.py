import os
import json
import streamlit as st
from datetime import datetime
from pydantic import ValidationError

from services.AppData import AppData

from models.TripModel import TripModel


class TripData:
    def __init__(self):
        """
        Initialize the TripData class.
        """
        self.app_data = AppData()

    # --------------------------
    # File Operations
    # --------------------------
    def save(self, id, key="", value=""):
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
                # Load into TripModel for validation
                trip_data = TripModel(**data)
            except (Exception, ValidationError) as e:
                print(f"Error reading or validating existing trip data: {e}")
                return False

            # Update the specific key if provided
            if key:
                setattr(trip_data, key, value)
            else:
                trip_data = value  # Overwrite with new data if no key is specified
        else:
            # Create new trip data if file doesn't exist
            try:
                # Check if value is a TripModel object
                if isinstance(value, TripModel):
                    trip_data = value
                else:
                    trip_data = TripModel(**value)
            except ValidationError as e:
                print(f"Error validating new trip data: {e}")
                return False

        # Convert dates to string format
        trip_data.start_date = trip_data.start_date.strftime(self._get_time_format())
        trip_data.end_date = trip_data.end_date.strftime(self._get_time_format())

        # Save the updated or new data
        return self.app_data._save_to_file(file_path, trip_data.json())

    @st.cache_data(ttl=10)
    def get(_self, id) -> TripModel:
        """
        Retrieve trip data for the specified ID.

        Args:
            id (str): The trip ID.

        Returns:
            TripModel or None: The trip data as a TripModel object.
        """
        folder_map = _self.app_data._get_storage_map()
        save_path = folder_map.get("trip")
        file_path = f"{save_path}/{id}.json"

        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                data = json.load(f)

                # If data is a string, convert to JSON
                if isinstance(data, str):
                    data = json.loads(data)

                # Convert date strings to datetime objects
                data["start_date"] = datetime.strptime(
                    data["start_date"], _self._get_time_format()
                )
                data["end_date"] = datetime.strptime(
                    data["end_date"], _self._get_time_format()
                )

                # Convert the JSON data to a TripModel object
                try:
                    return TripModel(**data)
                except ValidationError as e:
                    print(f"Error validating trip data: {e}")
        return None

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

    # --------------------------
    # Data Operations
    # --------------------------
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
            trip_title = self.get(trip_id).title
            available_trips.append({"id": trip_id, "title": trip_title})
        return available_trips

    # --------------------------
    # Utils
    # --------------------------
    def _get_time_format(self):
        return self.app_data.get_config("time_format")
