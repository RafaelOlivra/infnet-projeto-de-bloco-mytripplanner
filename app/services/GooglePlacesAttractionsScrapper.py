import os
import requests
import streamlit as st
import time

from services.AppData import AppData
from services.Logger import _log
from models.Attraction import AttractionModel


class GooglePlacesAttractionsScrapper:
    """
    A class for scraping tourist attractions using the Google Places API.

    This class interacts with the Google Places API to fetch information about attractions
    in a specified location. It handles caching of attraction images and supports
    recursive fetching of results when pagination is required.
    """

    def __init__(self, api_key: str = None, image_cache_dir: str = None):
        """
        Initialize the GooglePlacesAttractionsScrapper class.

        Sets up the API key for Google Places, configures the image cache directory,
        and ensures the cache directory exists.
        """
        self.api_key = api_key or AppData().get_api_key("googlemaps")
        self.image_cache_dir = (
            image_cache_dir
            if image_cache_dir
            else AppData()._get_storage_map().get("image_cache")
        )
        os.makedirs(
            self.image_cache_dir, exist_ok=True
        )  # Ensure cache directory exists

    @st.cache_resource(ttl=86400, show_spinner=False)
    def get_near_attractions(
        _self,
        city_name: str,
        state_name: str,
        start: int = 0,
        limit: int = 18,
        recursive: bool = True,
    ) -> list[AttractionModel]:
        """
        Retrieves nearby attractions in a given city and state using the Google Places API.

        Args:
            city_name (str): The name of the city.
            state_name (str): The name of the state.
            start (int, optional): Starting index for pagination (not directly supported by API). Defaults to 0.
            limit (int, optional): The maximum number of attractions to retrieve. Defaults to 18.
            recursive (bool, optional): If True, fetch additional results recursively. Defaults to True.

        Returns:
            list[AttractionModel]: A list of AttractionModel objects containing attraction details.
        """
        location = f"{city_name}, {state_name}, Brasil"
        url = "https://maps.googleapis.com/maps/api/place/textsearch/json"

        params = {
            "query": f"attractions in {location}, Brasil",
            "key": _self.api_key,
            "type": "tourist_attraction",
            "language": "pt-BR",
        }

        _log(f"[GoogleMapsScrapper] Fetching attractions for: {location}")

        # API request
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        if "results" not in data or not data["results"]:
            _log(f"[GoogleMapsScrapper] No attractions found for {location}")
            return []

        cards = []
        for result in data["results"]:
            image_id = result.get("photos", [{}])[0].get("photo_reference", "")
            image_url = _self.fetch_and_cache_photo(image_id)
            card = AttractionModel(
                **{
                    "name": result.get("name"),
                    "city_name": city_name,
                    "state_name": state_name,
                    "url": f"https://www.google.com/maps/place/?q=place_id:{result['place_id']}",
                    "review_count": result.get("user_ratings_total", 0),
                    "review_stars": result.get("rating", -1),
                    "description": result.get("formatted_address", ""),
                    "image": image_url,
                }
            )
            cards.append(card)

            # Stop if we reach the limit
            if len(cards) >= limit:
                break

        # Handle limit with recursion
        next_page_token = data.get("next_page_token")
        while recursive and next_page_token and len(cards) < limit:
            params["pagetoken"] = next_page_token
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            next_page_token = data.get("next_page_token")

            for result in data["results"]:
                image_id = result.get("photos", [{}])[0].get("photo_reference", "")
                image_url = _self.fetch_and_cache_photo(image_id)
                card = AttractionModel(
                    **{
                        "name": result.get("name"),
                        "city_name": city_name,
                        "state_name": state_name,
                        "url": f"https://www.google.com/maps/place/?q=place_id:{result['place_id']}",
                        "review_count": result.get("user_ratings_total", 0),
                        "review_stars": result.get("rating", -1),
                        "description": result.get("formatted_address", ""),
                        "image": image_url,
                    }
                )
                cards.append(card)
                if len(cards) >= limit:
                    break

        _log(
            f"[GoogleMapsScrapper] Found {len(cards)} attractions in {city_name}, {state_name}"
        )

        return cards

    # --------------------------
    # Utils
    # --------------------------
    @st.cache_data(ttl=86400, show_spinner=False)
    def fetch_and_cache_photo(_self, photo_reference: str, max_width: int = 400) -> str:
        """
        Fetches and caches the photo locally using its reference.

        Args:
            photo_reference (str): The reference ID of the photo.
            max_width (int): The maximum width of the image.

        Returns:
            str: The local path to the cached image or an empty string if not available.
        """
        if not photo_reference:
            return ""

        # Path for the cached image
        photo_id = photo_reference[:12] + "-" + str(int(time.time()))
        image_path = os.path.join(_self.image_cache_dir, f"{photo_id}.jpg")
        image_path = _self.normalize_path(image_path)

        # Check if the image is already cached
        if os.path.exists(image_path):
            return image_path

        # Fetch and cache the image
        url = (
            f"https://maps.googleapis.com/maps/api/place/photo?"
            f"maxwidth={max_width}&photoreference={photo_reference}&key={_self.api_key}"
        )
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            try:
                with open(image_path, "wb") as f:
                    for chunk in response.iter_content(1024):
                        f.write(chunk)
                _log(f"[GoogleMapsScrapper] Cached image: {image_path}")
                return image_path
            except Exception as e:
                _log(f"[GoogleMapsScrapper] Failed to cache image: {e}")
                return ""

        _log(
            f"[GoogleMapsScrapper] Failed to fetch photo for reference: {photo_reference}"
        )
        return ""

    def normalize_path(self, path_str: str) -> str:
        """
        Normalizes a path string by removing special characters and spaces.
        And changing // to /

        Args:
            path_str (str): The path string to normalize.

        Returns:
            str: The normalized path string.
        """
        path_str = path_str.replace("\\", "/")
        # Adjust for Windows paths
        # if os.name == "nt":
        #     # CHange / to \
        #     path_str = path_str.replace("/", "\\")
        #     _log(f"Path: {path_str}")
        return path_str
