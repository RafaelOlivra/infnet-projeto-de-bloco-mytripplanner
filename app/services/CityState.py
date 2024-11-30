import json

from services.AppData import AppData


class CityStateData:
    """
    City and state data service.
    Provides methods to retrieve city and state data based on the data stored in a JSON file.
    """

    def __init__(self):
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
        Retrieves a list of all state names.

        Returns:
            list: A list of state names (str).
        """
        return [state["nome"] for state in self.city_state_data.get("estados", [])]

    def get_ufs(self):
        """
        Retrieves a list of all state abbreviations (UFs).

        Returns:
            list: A list of state abbreviations (str).
        """
        return [state["sigla"] for state in self.city_state_data.get("estados", [])]

    def get_cities_by_state(self, state):
        """
        Retrieves a list of cities in a specified state by its name.

        Args:
            state (str): The name of the state.

        Returns:
            list: A list of city names (str) in the specified state.
        """
        for s in self.city_state_data.get("estados", []):
            if s["nome"].lower() == state.lower():
                return s["cidades"]
        return []

    def get_cities_by_uf(self, uf):
        """
        Retrieves a list of cities in a specified state by its UF (abbreviation).

        Args:
            uf (str): The abbreviation of the state (UF).

        Returns:
            list: A list of city names (str) in the specified state.
        """
        for s in self.city_state_data.get("estados", []):
            if s["sigla"].lower() == uf.lower():
                return s["cidades"]
        return []

    def uf_to_state(self, uf):
        """
        Retrieves the full name of a state given its abbreviation.

        Args:
            uf (str): The abbreviation of the state (UF).

        Returns:
            str: The full name of the state, or an empty string if not found.
        """
        for s in self.city_state_data.get("estados", []):
            if s["sigla"].lower() == uf.lower():
                return s["nome"]
        return ""
