import requests
import os
from datetime import datetime, timedelta
from functools import lru_cache
import json


class AppData:
    def __init__(self):
        pass

    # --------------------------
    # Getters
    # ---------------------------

    def get(self, group="config", id="", key=""):
        # Data files are stored in the data folder
        # Each group has its own directory
        # Data are stored in a JSON format
        # This is temporary and will be replaced by a database

        folder_map = self._get_storage_map()

        # Check if group exists
        if group not in folder_map:
            return None
        # Check if key is empty
        if key == "":
            return None

        # App Config
        if group == "config":
            return self.get_config(key)

        # API Keys
        if group == "api_key":
            return self.get_api_key(key)

        # Trip Data
        if group == "trip":
            return self.get_trip_data(id, key)

    def get_config(self, key):
        config_file = "app/config/cfg.json"
        if os.path.exists(config_file):
            with open(config_file, "r") as f:
                data = json.load(f)
                if key in data:
                    return data[key]

    def get_api_key(self, key):
        key_map = {
            "openweathermap": "OPENWEATHERMAP_API_KEY",
            "googlemaps": "GOOGLEMAPS_API_KEY",
            "yelp": "YELP_API_KEY",
            "opencagedata": "OPENCAGEDATA_API_KEY",
        }
        return os.getenv(key_map[key])

    def get_trip_data(self, id, key):
        id = self.sanitize_id(id)
        save_path = self._get_storage_map()["trip"]
        file_path = save_path + '/' + id + '.json'

        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                data = f.read()
                data = json.loads(data)
                if key in data:
                    return data[key]

            return data
        return None

    def _get_storage_map(self):
        storage_dir = self.get_config("storage_dir")
        return {
            "trip": storage_dir + "/trip",
        }

    # --------------------------
    # Setters
    # ---------------------------

    def save(self, group="app", id="", key="", value=""):
        # Data files are stored in the data folder
        # Each group has its own directory
        # Data are stored in a JSON format
        # This is temporary and will be replaced by a database

        folder_map = self._get_storage_map()

        # Check if we have the required parameters
        if group not in folder_map:
            return False
        if value is None:
            return False

        # Trip Data
        if group == "trip":
            print("Saving trip data")
            return self._save_trip_data(value)

    def _save_trip_data(self, TripData):
        id = self.sanitize_id(TripData["trip_id"])

        save_path = self._get_storage_map()["trip"]
        file_path = save_path + '/' + id + '.json'

        # Create save directory if it doesn't exist
        if not os.path.exists(save_path):
            os.makedirs(save_path)

        with open(file_path, "w") as f:
            f.write(json.dumps(TripData))
        return True

    def _update_trip_data(self, id, key, value):
        id = self.sanitize_id(id)
        save_path = self._get_storage_map()["trip"]
        file_path = save_path + '/' + id + '.json'

        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                data = f.read()
                data = json.loads(data)
                data[key] = value
                with open(file_path, "w") as f:
                    f.write(json.dumps(data))
                return True
        return False

    # --------------------------
    # Delete
    # ---------------------------

    def delete(self, group="app", id="", key=""):
        # Data files are stored in the data folder
        # Each group has its own directory
        # Data are stored in a JSON format
        # This is temporary and will be replaced by a database

        folder_map = self._get_storage_map()

        # Check if group exists
        if group not in folder_map:
            return False
        # Check if key is empty
        if key == "":
            return False

        # Trip Data
        if group == "trip":
            return self._delete_trip_data(id, key)

    def _delete_trip_data(self, id, key):
        id = self.sanitize_id(id)
        save_path = self._get_storage_map()["trip"]
        file_path = save_path + '/' + id + '.json'

        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                data = f.read()
                data = json.loads(data)
                if key in data:
                    del data[key]
                    with open(file_path, "w") as f:
                        f.write(json.dumps(data))
                    return True
        return False

    # --------------------------
    # Utils
    # ---------------------------

    def sanitize_id(self, id):
        # Check if it's a valid UUID
        if len(id) == 36:
            return id
