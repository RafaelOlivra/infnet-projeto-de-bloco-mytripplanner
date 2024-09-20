from services.AppData import AppData
from services.GoogleMaps import GoogleMaps


class LatLong:
    def __init__(self):
        return

    def get_coordinates(self, city, state):
        """Get the latitude and longitude of a location using Google Maps."""
        lat, long = GoogleMaps().get_latitude_longitude(city, state)

        if lat is None or long is None:
            raise ValueError(
                "Could not find coordinates for the specified location")

        return lat, long
