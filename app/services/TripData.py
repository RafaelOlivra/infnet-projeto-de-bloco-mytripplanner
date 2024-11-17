from pydantic import ValidationError

from lib.Utils import Utils
from services.Logger import _log
from services.AppData import AppData

from models.Trip import TripModel


class TripData:
    def __init__(self):
        """
        Initialize the TripData class.
        """
        self.app_data = AppData()

    def save(self, trip_id, trip_data: TripModel) -> bool:
        """
        Save a new trip or replace the entire trip data.

        Args:
            trip_id (str): Trip ID.
            trip_data (TripModel): The trip data to save.

        Returns:
            bool: True if the data was saved successfully, False otherwise.
        """

        # Check if the trip ID is provided
        if not trip_id:
            raise ValueError("Trip ID is required to save trip data.")

        # Check if we have a valid TripModel object
        if type(trip_data) != TripModel:
            raise ValueError("Trip data is not a valid TripModel object.")

        # Convert dates to string format
        trip_data.start_date = Utils().to_date_string(trip_data.start_date)
        trip_data.end_date = Utils().to_date_string(trip_data.end_date)
        trip_data.created_at = Utils().to_date_string(trip_data.created_at)

        # Save the new or entire trip data
        return self.app_data.save(
            "trip", trip_id, trip_data.model_dump_json(), replace=True
        )

    def update(self, trip_id, key="", value="") -> bool:
        """
        Update specific fields of an existing trip.

        Args:
            trip_id (str): Trip ID.
            key (str): The key to update within the trip data.
            value (any): The value to store in the trip data.

        Returns:
            bool: True if the data was updated successfully, False otherwise.
        """

        # Check if the trip ID is provided
        if not trip_id:
            raise ValueError("Trip ID is required to update trip data.")

        # Get the existing trip data
        trip_data = self.get(trip_id)

        # Check if we have a valid TripModel object
        if type(trip_data) != TripModel:
            raise ValueError("Trip data is not a valid TripModel object.")

        # Update the trip data with the new key-value pair
        if key and value:
            # if key = __ALL__, replace the entire trip data
            if key == "__ALL__":
                return self.save(trip_id, value)

            setattr(trip_data, key, value)
        else:
            raise ValueError("Key and value are required to update the trip.")

        # Convert dates to string format
        trip_data.start_date = Utils().to_date_string(trip_data.start_date)
        trip_data.end_date = Utils().to_date_string(trip_data.end_date)
        trip_data.created_at = Utils().to_date_string(trip_data.created_at)

        # Save the updated data
        return self.app_data.save(
            "trip", trip_id, trip_data.model_dump_json(), replace=True
        )

    def get(_self, trip_id: str) -> TripModel:
        """
        Retrieve trip data for the specified ID.

        Args:
            id (str): The trip ID.

        Returns:
            TripModel or None: The trip data as a TripModel object.
        """
        return _self._to_trip_model(_self.app_data.get("trip", trip_id))

    def delete(self, trip_id) -> bool:
        """
        Delete the trip data for the specified trip ID.

        Args:
            id (str): The trip ID to delete.

        Returns:
            bool: True if the file was deleted, False otherwise.
        """
        return self.app_data.delete("trip", trip_id)

    # --------------------------
    # User Operations
    # --------------------------
    def get_user_trip_ids(self, user_id: int = 0, limit: int = 0) -> list[str]:
        """
        Retrieve a list of available trip IDs.

        Returns:
            list: A list of trip IDs.
        """
        trips = self.get_user_trips(user_id=user_id, limit=limit)
        trips = [trip.id for trip in trips]

    def get_user_trip(self, trip_id: str, user_id: int = 0) -> TripModel:
        """
        Retrieve a trip by ID.

        Args:
            user_id (int): The user ID.
            trip_id (str): The trip ID.

        Returns:
            TripModel or None: The trip data as a TripModel object.
        """
        if not trip_id:
            return None

        trip = self.get(trip_id)

        # Check if the trip belongs to the user
        if trip and trip.user_id == user_id:
            return trip

    def get_user_trips(
        self, user_id: int = 0, limit: int = 0, order_by: str = "created_at"
    ) -> list[TripModel]:
        """
        Retrieve a list of available trips with their IDs and titles.

        Returns:
            list: A list of dictionaries containing trip ID and title.
        """
        # Check if we have a valid user ID
        if user_id is None or int(user_id) < 0:
            return []

        # TODO: This is a temporary solution until we implement user authentication
        # and a better way to query trips by user ID (Database, etc.)
        trips = self.get_all_trips(limit=limit)
        trips = [trip for trip in trips if trip.user_id == user_id]

        # Sort the trips by the specified field
        if order_by:
            if order_by == "created_at":
                trips = sorted(trips, key=lambda x: x.created_at, reverse=True)

        return trips

    # --------------------------
    # Overall Trip Operations
    # --------------------------

    def get_all_trips(
        self, limit: int = 0, order_by: str = "created_at"
    ) -> list[TripModel]:
        """
        Retrieve a list of all available trips.

        Returns:
            list: A list of TripModel objects.
        """
        trips = self.app_data.get_all("trip", limit=limit)
        trips = [self._to_trip_model(trip) for trip in trips]

        # Remove empty or invalid trip data
        trips = [trip for trip in trips if trip]

        # Sort the trips by the specified field
        if order_by:
            if order_by == "created_at":
                trips = sorted(trips, key=lambda x: x.created_at, reverse=True)

        return trips

    def count_all(self) -> int:
        """
        Retrieve the total number of trips.

        Returns:
            int: The total number of trips.
        """
        return self.app_data.count("trip")

    # --------------------------
    # Utils
    # --------------------------

    def _to_trip_model(self, trip_data: dict) -> TripModel:
        """
        Convert a dictionary to a TripModel object.

        Args:
            trip_data (dict): The trip data as a dictionary.

        Returns:
            TripModel: The trip data as a TripModel object.
        """

        if not trip_data:
            return None

        try:
            # Convert date strings to datetime objects
            trip_data["start_date"] = Utils.to_datetime(trip_data["start_date"])
            trip_data["end_date"] = Utils.to_datetime(trip_data["end_date"])

            # Date published was not required in the original model
            # We need to check if it exists before converting it
            if "created_at" in trip_data:
                trip_data["created_at"] = Utils.to_datetime(trip_data["created_at"])
            else:
                # Update the model to include the created_at field
                trip_data["created_at"] = trip_data["start_date"]

            return TripModel(**trip_data)
        except ValidationError as e:
            _log(f"Error validating trip data: {e}", level="ERROR")
            return None
