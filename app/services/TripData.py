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
            key (str): The key to update within the trip data. If empty, the entire trip dat is replaced.
            value (any): The value to store in the trip data.

        Returns:
            bool: True if the data was saved successfully, False otherwise.
        """
        # Get the trip data
        trip_data = self.get(id)

        # If the trip data does not exist, create a new one
        if not trip_data:
            trip_data = TripModel(id=id)

        # Update the trip data with the new key-value pair
        if key and value:
            setattr(trip_data, key, value)

        # Convert dates to string format
        trip_data.start_date = trip_data.start_date.strftime(self._get_time_format())
        trip_data.end_date = trip_data.end_date.strftime(self._get_time_format())

        # Save the updated or new data
        return self.app_data.save("trip", id, trip_data.json(), replace=True)

    def get(_self, id) -> TripModel:
        """
        Retrieve trip data for the specified ID.

        Args:
            id (str): The trip ID.

        Returns:
            TripModel or None: The trip data as a TripModel object.
        """
        trip_data = _self.app_data.get("trip", id)

        if trip_data:

            # Convert date strings to datetime objects
            trip_data["start_date"] = datetime.strptime(
                trip_data["start_date"], _self._get_time_format()
            )
            trip_data["end_date"] = datetime.strptime(
                trip_data["end_date"], _self._get_time_format()
            )

            # Convert the JSON data to a TripModel object
            try:
                return TripModel(**trip_data)
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
        return self.app_data.delete("trip", id)

    # --------------------------
    # Data Operations
    # --------------------------
    def get_available_trip_ids(self):
        """
        Retrieve a list of available trip IDs.

        Returns:
            list: A list of trip IDs.
        """
        return self.app_data.get_all_ids("trip")

    def get_available_trips(self):
        """
        Retrieve a list of available trips with their IDs and titles.

        Returns:
            list: A list of dictionaries containing trip ID and title.
        """
        return self.app_data.get_all("trip")

    # --------------------------
    # Utils
    # --------------------------
    def _get_time_format(self):
        return self.app_data.get_config("time_format")
