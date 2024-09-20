from services.AppData import AppData
import json


class CityStateData:
    def __init__(self):
        # Load the json data with the city and state names
        json_file = AppData().get_config("city_state_json")
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                self.city_state_data = json.load(f)
        except FileNotFoundError:
            print("CityStateData: File not found.")
        return

    def get_states(self):
        states = []
        data = self.city_state_data
        states = data['estados']
        for state in states:
            states.append(state['nome'])
        return states

    def get_ufs(self):
        ufs = []
        data = self.city_state_data
        states = data['estados']
        for state in states:
            ufs.append(state['sigla'])
        return ufs

    def get_cities_by_state(self, state):
        cities = []
        data = self.city_state_data
        states = data['estados']
        for s in states:
            if s['sigla'] == state:
                cities = s['cidades']
                break
        return cities

    def get_cities_by_uf(self, uf):
        cities = []
        data = self.city_state_data
        states = data['estados']
        for s in states:
            if s['sigla'] == uf:
                cities = s['cidades']
                break
        return cities
