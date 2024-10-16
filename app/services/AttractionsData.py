from typing import List

from services.AppData import AppData
from lib.Utils import Utils

from models.Attraction import AttractionModel


class AttractionsData:
    def __init__(self):
        """
        Initialize the AttractionsData class.
        """
        self.app_data = AppData()

    # --------------------------
    # CRUD Operations
    # --------------------------

    def save(self, attractions: List[AttractionModel], slug: str = "") -> bool:
        """
        Save or update attraction data to a JSON file.

        Args:
            slug (str): Attraction slug.
            attractions (list[Attraction]): List of Attraction objects.

        Returns:
            bool: True if the data was saved successfully, False otherwise.
        """
        # If the slug is empty, generate a new one
        if not slug:
            city_name = attractions[0].city_name
            state_name = attractions[0].state_name
            slug = self.slugify(city_name, state_name)

        # Convert the Attraction objects to JSON
        json = "["
        for attraction in attractions:
            json += attraction.json() + ","
        json = json[:-1] + "]"

        # Save the updated or new data
        return self.app_data.save("attractions", slug, json, replace=True)

    def get(_self, slug: str) -> List[AttractionModel]:
        """
        Retrieve attractions data for the specified ID.

        Args:
            slug (str): The Attraction slug.

        Returns:
            Attraction or None: The attraction data as an Attraction object.
        """
        attraction_data = _self.app_data.get("attractions", slug)
        if attraction_data:
            # Convert the JSON data to Attraction objects
            return [AttractionModel(**item) for item in attraction_data]
        return None

    def delete(self, slug: str) -> bool:
        """
        Delete the Attraction ID data.

        Args:
            slug (str): The Attraction slug to delete.

        Returns:
            bool: True if the file was deleted, False otherwise.
        """
        return self.app_data.delete("attractions", slug)

    # --------------------------
    # Utils
    # --------------------------

    @staticmethod
    def slugify(city_name: str, state_name: str) -> str:
        """
        Generate a unique ID based on the city and state names.

        Returns:
            str: Generated ID.
        """
        city_name = Utils().slugify(city_name)
        state_name = Utils().slugify(state_name)
        return f"{state_name}_{city_name}"
