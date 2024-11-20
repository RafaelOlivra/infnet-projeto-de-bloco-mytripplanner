import requests
import streamlit as st

from services.AppData import AppData
from services.Logger import _log
from models.Attraction import AttractionModel


class GooglePlacesAttractionsScrapper:
    def __init__(self):
        self.api_key = AppData().get_api_key("googlemaps")

    @st.cache_data(ttl=86400, show_spinner=False)
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
            image_url = _self.get_photo_url(image_id)
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
                image_url = _self.get_photo_url(image_id)
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
    def get_photo_url(_self, photo_reference: str, max_width: int = 400) -> str:
        """
        Retrieves the URL for a photo using its reference.

        Args:
            photo_reference (str): The reference ID of the photo.
            max_width (int): The maximum width of the image.

        Returns:
            str: The URL to the photo.
        """
        if not photo_reference:
            return ""
        return f"https://maps.googleapis.com/maps/api/place/photo?maxwidth={max_width}&photoreference={photo_reference}&key={_self.api_key}"
