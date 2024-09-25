import requests
from datetime import datetime, timedelta
from services.AppData import AppData
import streamlit as st


class GoogleMaps:
    def __init__(self, api_key=None):
        # Set the API key, either from the environment or directly from the parameter
        self.api_key = api_key or AppData().get_api_key("googlemaps")
        if not self.api_key:
            raise ValueError("API key is required for Google Maps API")

    @st.cache_data(ttl=86400)
    def get_latitude_longitude(_self, location: str) -> tuple[float, float]:
        """
        Retrieve latitude and longitude for a given location using the Google Maps Geocoding API.

        Args:
        - location (str): The location (e.g., city, state, or address) to geocode.

        Returns:
        - tuple: A tuple containing (latitude, longitude).

        Raises:
        - ValueError: If the location cannot be geocoded.
        """
        url = f"https://maps.googleapis.com/maps/api/geocode/json?address={_self._url_encode(location)}&key={_self.api_key}"
        data = _self._fetch_json(url)

        # Check if the request was successful
        if data.get("status") == "OK" and len(data.get("results", [])) > 0:
            location_data = data["results"][0]["geometry"]["location"]
            return location_data["lat"], location_data["lng"]
        else:
            raise ValueError(f"Could not retrieve coordinates for location: {location}")

    def get_directions_url(_self, origin: str, destination: str) -> str:
        """
        Generate Google Maps directions URL.

        Args:
        - origin (str): Starting location.
        - destination (str): Destination location.

        Returns:
        - str: URL for Google Maps directions.
        """
        base_url = "https://www.google.com/maps/dir/?api=1"
        url = f"{base_url}&origin={_self._url_encode(origin)}&destination={_self._url_encode(destination)}"
        return url

    def get_directions(
        _self, origin: str, destination: str, mode: str | None = None
    ) -> dict:
        """
        Get directions from an origin to a destination using Google Maps API.

        Args:
        - origin (str): The starting location for directions.
        - destination (str): The destination location for directions.
        - mode (str, optional): The mode of transportation. Defaults to 'car'.

        Returns:
        - dict: The directions data.
        """
        origin_lat_long = _self.get_latitude_longitude(origin)
        destination_lat_long = _self.get_latitude_longitude(destination)

        mode_param = f"&mode={mode}" if mode else ""
        url = f"https://maps.googleapis.com/maps/api/directions/json?key={_self.api_key}&origin={origin_lat_long[0]},{origin_lat_long[1]}&destination={destination_lat_long[0]},{destination_lat_long[1]}{mode_param}"
        return _self._fetch_json(url)

    def get_google_maps_directions_iframe_url(
        _self,
        origin: str,
        destination: str,
        zoom: int | None = None,
        mode: str | None = None,
    ) -> str:
        """
        Generate URL code for an iframe that displays Google Maps directions.

        Args:
        - origin (str): The starting location for directions.
        - destination (str): The destination location for directions.
        - zoom (int, optional): The zoom level for the map.
        - mode (str, optional): The mode of transportation.

        Returns:
        - str: URL for the embeddable iframe.
        """
        origin_lat_long = _self.get_latitude_longitude(origin)
        destination_lat_long = _self.get_latitude_longitude(destination)

        zoom_param = f"&zoom={zoom}" if zoom is not None else ""
        mode_param = f"&mode={mode}" if mode else ""
        url = f"https://www.google.com/maps/embed/v1/directions?key={_self.api_key}&origin={origin_lat_long[0]},{origin_lat_long[1]}&destination={destination_lat_long[0]},{destination_lat_long[1]}&units=metric{zoom_param}{mode_param}"
        return url

    @st.cache_data(ttl=86400)
    def _fetch_json(_self, url: str) -> dict:
        """
        Fetch JSON data from the specified URL.

        Args:
            url (str): The URL to fetch the JSON data from.

        Returns:
            dict: The JSON data as a dictionary.

        Raises:
            requests.exceptions.RequestException: For any network-related errors.
        """
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise exception for bad responses
            return response.json()
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Error fetching data from {url}: {str(e)}")

    def _url_encode(_self, text: str) -> str:
        """
        Encode a text string for use in a URL.

        Args:
        - text (str): The text to encode.

        Returns:
        - str: The URL-encoded text.

        Raises:
        - ValueError: If the input is not a string.
        """
        if not isinstance(text, str):
            raise ValueError("Input must be a string")
        return requests.utils.quote(text)
