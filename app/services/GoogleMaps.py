import requests
import os
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
    def get_latitude_longitude(_self, location: str):
        """
        Retrieve latitude and longitude for a given location using the Google Maps Geocoding API.

        Args:
        - location (str): The location (e.g., city, state, or address) to geocode.

        Returns:
        - tuple: A tuple containing (latitude, longitude).

        Raises:
        - ValueError: If the location cannot be geocoded.
        """
        # Encode the location
        url = f"https://maps.googleapis.com/maps/api/geocode/json?address={_self.url_encode(location)}&key={_self.api_key}"
        data = _self.fetch_json(url)

        # Check if the request was successful
        if data.get('status') == 'OK' and len(data.get('results', [])) > 0:
            location_data = data['results'][0]['geometry']['location']
            return location_data['lat'], location_data['lng']
        else:
            raise ValueError(
                f"Could not retrieve coordinates for location: {location}")

    def get_directions_url(self, origin: str, destination: str):
        """
        Generate Google Maps directions URL.

        Args:
        - origin (str): Starting location.
        - destination (str): Destination location.

        Returns:
        - str: URL for Google Maps directions.
        """
        base_url = "https://www.google.com/maps/dir/?api=1"
        url = f"{base_url}&origin={self.url_encode(origin)}&destination={
            self.url_encode(destination)}"
        return url

    @st.cache_data(ttl=86400)
    def get_directions(_self, origin: str, destination: str, mode: str = 'car'):
        """
        Get directions from an origin to a destination using Google Maps API.

        Args:
        - origin (str): The starting location for directions.
        - destination (str): The destination location for directions.
        - mode (str, optional): The mode of transportation. Defaults to 'car'.

        Returns:
        - dict: The directions data.
        """
        url = f"https://maps.googleapis.com/maps/api/directions/json?origin={_self.url_encode(
            origin)}&destination={_self.url_encode(destination)}&mode={_self.url_encode(mode)}&key={_self.api_key}"
        return _self.fetch_json(url)

    def get_google_maps_directions_iframe_url(self, origin, destination, zoom: int | None = None):
        """
        Generate URL code for an iframe that displays Google Maps directions.

        Args:
        - origin (str): The starting location for directions.
        - destination (str): The destination location for directions.
        - zoom (int, optional): The zoom level for the map.

        Returns:
        - str: URL for the embeddable iframe.
        """
        zoom_param = f"&zoom={int(zoom)}" if zoom is not None else ""
        url = f"https://www.google.com/maps/embed/v1/directions?origin={self.url_encode(
            origin)}&destination={self.url_encode(destination)}&key={self.api_key}{zoom_param}"
        return url

    def fetch_json(self, url: str):
        """
        Fetch JSON data from the specified URL.

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
        if not isinstance(text, str):
            raise ValueError("Input must be a string")
        return requests.utils.quote(text)
