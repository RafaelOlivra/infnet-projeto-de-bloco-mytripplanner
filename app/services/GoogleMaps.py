import requests
import streamlit as st

from services.AppData import AppData
from lib.Utils import Utils


class GoogleMaps:
    """
    Google Maps service class to interact with the Google Maps Geocoding and Directions APIs.
    """

    def __init__(self, api_key: str = None):
        """
        Initializes the GoogleMaps class.

        Args:
            api_key (str, optional): The API key for Google Maps. If not provided, it attempts to retrieve the key
            from AppData.

        Raises:
            ValueError: If the API key is not provided or cannot be retrieved from AppData.
        """
        self.api_key = api_key or AppData().get_api_key("googlemaps")
        if not self.api_key:
            raise ValueError("API key is required for Google Maps API")

    def get_latitude_longitude(self, location: str) -> tuple[float, float]:
        """
        Retrieve latitude and longitude for a given location using the Google Maps Geocoding API.

        Args:
            location (str): The location (e.g., city, state, or address) to geocode.

        Returns:
            tuple: A tuple containing (latitude, longitude).

        Raises:
            ValueError: If the location cannot be geocoded.
        """
        url = f"https://maps.googleapis.com/maps/api/geocode/json?address={Utils().url_encode(location)},Brazil&key={self.api_key}"
        data = self._fetch_json(url)

        # Check if the request was successful
        if data.get("status") == "OK" and len(data.get("results", [])) > 0:
            location_data = data["results"][0]["geometry"]["location"]
            return location_data["lat"], location_data["lng"]
        else:
            raise ValueError(f"Could not retrieve coordinates for location: {location}")

    def get_directions_url(
        self,
        origin: str,
        destination: str,
        location_mode: str | None = "coordinates",
        mode: str | None = None,
    ) -> str:
        """
        Generate Google Maps directions URL.

        Args:
            origin (str): Starting location.
            destination (str): Destination location.
            location_mode (str, optional): Whether to use coordinates or addresses. Defaults to "coordinates".
            mode (str, optional): The mode of transportation (e.g., driving, walking). Defaults to 'car'.

        Returns:
            str: URL for Google Maps directions.
        """
        if location_mode == "coordinates":
            origin_lat_long = self.get_latitude_longitude(origin)
            destination_lat_long = self.get_latitude_longitude(destination)
            origin = f"{origin_lat_long[0]},{origin_lat_long[1]}"
            destination = f"{destination_lat_long[0]},{destination_lat_long[1]}"
        else:
            origin = Utils().url_encode(origin)
            destination = Utils().url_encode(destination)

        mode_param = f"&travelmode={mode}" if mode else ""
        base_url = "https://www.google.com/maps/dir/?api=1"
        url = f"{base_url}&origin={origin}&destination={destination}&dir_action=navigate{mode_param}"
        return url

    def get_directions(
        self,
        origin: str,
        destination: str,
        location_mode: str | None = "coordinates",
        mode: str | None = None,
    ) -> dict:
        """
        Get directions from an origin to a destination using the Google Maps Directions API.

        Args:
            origin (str): The starting location for directions.
            destination (str): The destination location for directions.
            location_mode (str, optional): Whether to use coordinates or addresses. Defaults to "coordinates".
            mode (str, optional): The mode of transportation (e.g., driving, walking). Defaults to 'car'.

        Returns:
            dict: The directions data.
        """
        if location_mode == "coordinates":
            origin_lat_long = self.get_latitude_longitude(origin)
            destination_lat_long = self.get_latitude_longitude(destination)
            origin = f"{origin_lat_long[0]}, {origin_lat_long[1]}"
            destination = f"{destination_lat_long[0]}, {destination_lat_long[1]}"
        else:
            origin = Utils().url_encode(origin)
            destination = Utils().url_encode(destination)

        mode_param = f"&mode={mode}" if mode else ""
        url = f"https://maps.googleapis.com/maps/api/directions/json?key={self.api_key}&origin={origin}&destination={destination}{mode_param}"
        return self._fetch_json(url)

    def get_google_maps_directions_iframe_url(
        self,
        origin: str,
        destination: str,
        zoom: int | None = None,
        location_mode: str | None = "coordinates",
        mode: str | None = None,
    ) -> str:
        """
        Generate URL code for an iframe that displays Google Maps directions.

        Args:
            origin (str): The starting location for directions.
            destination (str): The destination location for directions.
            zoom (int, optional): The zoom level for the map.
            location_mode (str, optional): Whether to use coordinates or addresses. Defaults to "coordinates".
            mode (str, optional): The mode of transportation (e.g., driving, walking).

        Returns:
            str: URL for the embeddable iframe.
        """
        if location_mode == "coordinates":
            origin_lat_long = self.get_latitude_longitude(origin)
            destination_lat_long = self.get_latitude_longitude(destination)
            origin = f"{origin_lat_long[0]}, {origin_lat_long[1]}"
            destination = f"{destination_lat_long[0]}, {destination_lat_long[1]}"
        else:
            origin = Utils().url_encode(origin)
            destination = Utils().url_encode(destination)

        zoom_param = f"&zoom={zoom}" if zoom is not None else ""
        mode_param = f"&mode={mode}" if mode else ""
        url = f"https://www.google.com/maps/embed/v1/directions?key={self.api_key}&origin={origin}&destination={destination}&units=metric{zoom_param}{mode_param}"
        return url

    # --------------------------
    # Utils
    # --------------------------
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
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Error fetching data from {url}: {str(e)}")
