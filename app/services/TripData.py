from pydantic import ValidationError

from services.AppData import AppData
from lib.Utils import Utils

from models.Trip import TripModel


class TripData:
    def __init__(self):
        """
        Initialize the TripData class.
        """
        self.app_data = AppData()

    # --------------------------
    # File Operations
    # --------------------------
    def save(self, id, key="", value="") -> bool:
        """
        Save or update trip data to a JSON file.

        Args:
            id (str): Trip ID.
            key (str): The key to update within the trip data. If empty, the entire trip dat is replaced.
            value (any): The value to store in the trip data.

        Returns:
            bool: True if the data was saved successfully, False otherwise.
        """

        # Check if the trip ID is provided
        if not id:
            raise ValueError("Trip ID is required to save/update trip data.")

        # Try to get the trip data if it already exists
        # If not we assume we are creating a new trip
        if key:
            trip_data = self.get(id)
        else:
            trip_data = value

        # Check if we have a valid TripModel object
        if type(trip_data) != TripModel:
            raise ValueError("Trip data is not a valid TripModel object.")

        # Update the trip data with the new key-value pair
        if key and value:
            setattr(trip_data, key, value)

        # Convert dates to string format
        trip_data.start_date = Utils().to_date_string(trip_data.start_date)
        trip_data.end_date = Utils().to_date_string(trip_data.end_date)
        trip_data.created_at = Utils().to_date_string(trip_data.created_at)

        # Save the updated or new data
        return self.app_data.save("trip", id, trip_data.model_dump_json(), replace=True)

    def get(_self, id) -> TripModel:
        """
        Retrieve trip data for the specified ID.

        Args:
            id (str): The trip ID.

        Returns:
            TripModel or None: The trip data as a TripModel object.
        """
        return _self._to_trip_model(_self.app_data.get("trip", id))

    def delete(self, id) -> bool:
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
    def get_all_ids(self, user_id=0, limit: int = 0) -> list[str]:
        """
        Retrieve a list of available trip IDs.

        Returns:
            list: A list of trip IDs.
        """
        trips = self.get_all(user_id=user_id, limit=limit)
        trips = [trip.id for trip in trips]

    def get_all(
        self, user_id=0, limit: int = 0, order_by: str = "created_at"
    ) -> list[TripModel]:
        """
        Retrieve a list of available trips with their IDs and titles.

        Returns:
            list: A list of dictionaries containing trip ID and title.
        """

        # TODO: This is a temporary solution until we implement user authentication
        # and a better way to query trips by user ID (Database, etc.)
        trips = self.app_data.get_all("trip", limit=limit)
        trips = [self._to_trip_model(trip) for trip in trips]

        # Filter trips by user ID
        if user_id is not None:
            trips = [trip for trip in trips if trip.user_id == user_id]

        # Sort the trips by the specified field
        if order_by:
            if order_by == "created_at":
                trips = sorted(trips, key=lambda x: x.created_at, reverse=True)

        return trips

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
            print(f"Error validating trip data: {e}")
            return None
