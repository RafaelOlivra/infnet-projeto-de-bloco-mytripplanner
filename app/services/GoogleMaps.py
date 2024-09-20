import requests
import os
from datetime import datetime, timedelta
from services.AppData import AppData
from functools import lru_cache


class GoogleMaps:
    def __init__(self, api_key=None):
        # Set the API key, either from the environment or directly from the parameter
        self.api_key = api_key or AppData().get_api_key("googlemaps")
        if not self.api_key:
            raise ValueError("API key is required for Google Maps API")

    def get_directions_url(self, origin: str, destination: str):
        base_url = "https://www.google.com/maps/dir/?api=1"
        url = f"{base_url}&origin={self.url_encode(origin)}&destination={
            self.url_encode(destination)}"
        return url

    @lru_cache(maxsize=100)
    def get_directions(self, origin: str, destination: str, mode: str = 'car'):
        """
        Get directions from an origin to a destination using Google Maps API.

        Args:
        - origin (str): The starting location for directions.
        - destination (str): The destination location for directions.
        - mode (str, optional): The mode of transportation. Defaults to 'car'.

        Returns:
        - dict: The directions data.
        """
        url = f"https://maps.googleapis.com/maps/api/directions/json?origin={self.url_encode(
            origin)}&destination={self.url_encode(destination)}&mode={self.url_encode(mode)}&key={self.api_key}"
        return self.fetch_json(url)

    def get_google_maps_directions_iframe_url(self, origin, destination, zoom: int | None = None):
        """
        Generate URL code for an iframe that displays Google Maps directions.

        Args:
        - origin (str): The starting location for directions.
        - destination (str): The destination location for directions.

        Returns:
        - str: URL for the embeddable iframe.
        """
        if zoom is not None and zoom.isnumeric():
            zoom = '&zoom=' + int(zoom)
        else:
            zoom = ''

        url = f"https://www.google.com/maps/embed/v1/directions?origin={self.url_encode(
            origin)}&destination={self.url_encode(destination)}&key={self.api_key}{zoom}"
        return url

    @lru_cache(maxsize=100)
    def fetch_json(self, url: str):
        """
        Fetches JSON data from the specified URL.

        Args:
            url (str): The URL to fetch the JSON data from.

        Returns:
            dict: The JSON data as a dictionary.

        """
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    def url_encode(self, text):
        """
        Encode a text string for use in a URL.

        Args:
        - text (str): The text to encode.

        Returns:
        - str: The URL-encoded text.
        """
        return requests.utils.quote(text)

    @lru_cache(maxsize=100)
    def get_latitude_longitude(self, location: str):
        """
        Retrieve latitude and longitude for a given location using the Google Maps Geocoding API.

        Args:
        - location (str): The location (e.g., city, state, or address) to geocode.

        Returns:
        - tuple: A tuple containing (latitude, longitude).

        Raises:
        - ValueError: If the location cannot be geocoded.
        """
        url = f"https://maps.googleapis.com/maps/api/geocode/json?address={
            self.url_encode(location)}&key={self.api_key}"
        data = self.fetch_json(url)

        if data['status'] == 'OK' and len(data['results']) > 0:
            location_data = data['results'][0]['geometry']['location']
            return location_data['lat'], location_data['lng']
        else:
            raise ValueError(
                f"Could not retrieve coordinates for location: {location}")
