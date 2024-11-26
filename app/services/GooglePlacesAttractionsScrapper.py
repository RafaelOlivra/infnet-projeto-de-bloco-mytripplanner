import os
import requests
import streamlit as st

from services.AppData import AppData
from services.Logger import _log
from models.Attraction import AttractionModel


class GooglePlacesAttractionsScrapper:
    def __init__(self):
        self.api_key = AppData().get_api_key("googlemaps")
        self.image_cache_dir = AppData()._get_storage_map().get("image_cache")
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
            list[AttractionModel]: A list of AttractionModel objects.
        """
        location = f"{city_name}, {state_name}"
        url = "https://maps.googleapis.com/maps/api/place/textsearch/json"

        params = {
            "query": f"attractions in {location}",
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
        image_path = os.path.join(_self.image_cache_dir, f"{photo_reference}.jpg")

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
            with open(image_path, "wb") as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            _log(f"[GoogleMapsScrapper] Cached image: {image_path}")
            return image_path

        _log(
            f"[GoogleMapsScrapper] Failed to fetch photo for reference: {photo_reference}"
        )
        return ""
