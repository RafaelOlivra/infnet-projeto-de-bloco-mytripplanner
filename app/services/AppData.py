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

    def get(self, group="app", id="", key=""):
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
        if group == "app":
            return self._get_config(key)

        # API Keys
        if group == "api_key":
            return self._get_api_key(key)

        # Trip Data
        if group == "trip":
            return self._get_trip_data(id, key)

    def get_config(self, key):
        folder_map = self._get_storage_map()
        file_path = folder_map["app"]["data"] + folder_map["app"]["file"]
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                data = f.read()
                data = json.loads(data)
                if key in data:
                    return data[key]

            return data
        return None

    def get_api_key(self, key):

        key_map = {
            "openweathermap": "OPENWEATHERMAP_API_KEY",
            "googlemaps": "GOOGLEMAPS_API_KEY",
            "yelp": "YELP_API_KEY",
            "opencagedata": "OPENCAGEDATA_API_KEY",
        }

        return os.getenv(key_map[key])

    def _get_trip_data(self, id, key):
        id = self.sanitize_id(id)
        folder_map = self._get_storage_map()
        file_path = folder_map["trip"]["data"] + \
            id + "/" + folder_map["trip"][id]+'.json'
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                data = f.read()
                data = json.loads(data)
                if key in data:
                    return data[key]

            return data
        return None

    def _get_storage_map(self):
        return {
            "trip": {
                "data": "app/data/.storage/trip/"
            },
            "config": {
                "data": "app/config/",
                "file": "cfg.json",
            },
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

        # Check if group exists
        if group not in folder_map:
            return False
        # Check if value is empty
        if value is None:
            return False

        # Trip Data
        if group == "trip":
            print("Saving trip data")
            return self._save_trip_data(value)

    def _save_trip_data(self, TripData):
        id = self.sanitize_id(TripData["trip_id"])
        folder_map = self._get_storage_map()
        file_path = folder_map["trip"]["data"] + id + '.json'

        # Create directory if it doesn't exist
        if not os.path.exists(folder_map["trip"]["data"]):
            os.makedirs(folder_map["trip"]["data"])

        with open(file_path, "w") as f:
            f.write(json.dumps(TripData))
        return True

    def _update_trip_data(self, id, key, value):
        id = self.sanitize_id(id)
        folder_map = self._get_storage_map()
        file_path = folder_map["trip"]["data"] + id + '.json'

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
        folder_map = self._get_storage_map()
        file_path = folder_map["trip"]["data"] + \
            id + "/" + folder_map["trip"][id]+'.json'
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
        return False

    # --------------------------
    # Utils
    # ---------------------------

    def sanitize_id(self, id):
        # Check if it's a valid UUID
        if len(id) == 36:
            return id
