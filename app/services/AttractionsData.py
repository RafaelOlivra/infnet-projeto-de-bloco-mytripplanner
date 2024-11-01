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
            json += attraction.model_dump_json() + ","
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
    # Overall Attractions Data
    # --------------------------

    def get_all_attractions(self) -> List[AttractionModel]:
        """
        Retrieve a list of all attractions data for all cities.

        Returns:
            list: A list of Attraction objects.
        """
        all_attractions = []
        for city_attractions in self.app_data.get_all("attractions"):
            for attraction in city_attractions:
                all_attractions.append(AttractionModel(**attraction))
        return all_attractions

    def get_attractions_by_city(self) -> dict[str, List[AttractionModel]]:
        """
        Retrieve a dictionary with all attractions data grouped by city.

        Returns:
            dict: A dictionary with city names as keys and a list of Attraction objects as values.
        """
        attractions_by_city = {}
        for city_attractions in self.app_data.get_all("attractions"):
            city_name = (
                city_attractions[0]["city_name"]
                + ", "
                + city_attractions[0]["state_name"]
            )
            attractions = []
            for attraction in city_attractions:
                attractions.append(AttractionModel(**attraction))
            attractions_by_city[city_name] = attractions
        return attractions_by_city

    def get_cities(self) -> List[str]:
        """
        Retrieve a list of all cities with attractions.

        Returns:
            list: A list of city names.
        """
        cities = []
        for city_attractions in self.app_data.get_all("attractions"):
            city_name = (
                city_attractions[0]["city_name"]
                + ", "
                + city_attractions[0]["state_name"]
            )
            cities.append(city_name)
        # Order the cities alphabetically
        cities.sort()

        # Remove duplicates
        cities = list(dict.fromkeys(cities))

        return cities

    def count_cities(self) -> int:
        """
        Count the total number of scanned cities.

        Returns:
            int: The total number of scanned cities.
        """
        return len(self.get_cities())

    def count_attractions(self) -> int:
        """
        Count the total number of attractions.

        Returns:
            int: The total number of attractions.
        """
        return len(self.get_all_attractions())

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
