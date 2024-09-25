from services.AppData import AppData
import json


class CityStateData:
    def __init__(self):
        """
        Initialize CityStateData by loading the city and state names from a JSON file.
        """
        # Load the JSON file with city and state data
        json_file = AppData().get_config("city_state_json")
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                self.city_state_data = json.load(f)
        except FileNotFoundError:
            print(f"CityStateData: The file '{json_file}' was not found.")
            self.city_state_data = {}

    def get_states(self):
        """
        Get a list of all state names.

        Returns:
            list: A list of state names.
        """
        return [state["nome"] for state in self.city_state_data.get("estados", [])]

    def get_ufs(self):
        """
        Get a list of all state abbreviations (UFs).

        Returns:
            list: A list of state abbreviations (UFs).
        """
        return [state["sigla"] for state in self.city_state_data.get("estados", [])]

    def get_cities_by_state(self, state):
        """
        Get a list of cities in a given state by its name.

        Args:
            state (str): The name of the state.

        Returns:
            list: A list of city names in the given state.
        """
        for s in self.city_state_data.get("estados", []):
            if s["nome"].lower() == state.lower():
                return s["cidades"]
        return []

    def get_cities_by_uf(self, uf):
        """
        Get a list of cities in a given state by its UF (abbreviation).

        Args:
            uf (str): The abbreviation of the state (UF).

        Returns:
            list: A list of city names in the given state.
        """
        for s in self.city_state_data.get("estados", []):
            if s["sigla"].lower() == uf.lower():
                return s["cidades"]
        return []

    def uf_to_state(self, uf):
        """
        Get the full name of a state given its abbreviation.

        Args:
            uf (str): The abbreviation of the state (UF).

        Returns:
            str: The full name of the state.
        """
        for s in self.city_state_data.get("estados", []):
            if s["sigla"].lower() == uf.lower():
                return s["nome"]
        return ""
